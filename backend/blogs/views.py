from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from .models import Blog
from .serializers import BlogSerializer
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .utils import filter_visible_blogs, paginate_blogs

User = get_user_model()

class BlogAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
    operation_description="Получение ленты блогов. Публичные блоги доступны без авторизации.",
    responses={200: BlogSerializer(many=True)},
    manual_parameters=[
        openapi.Parameter('page', openapi.IN_QUERY, description="Номер страницы", type=openapi.TYPE_INTEGER)
    ]
    )
    def get(self, request):
        """
        Получение ленты блогов (20 на страницу, ?page=1)
        Публичные блоги доступны без авторизации.
        Для авторизованных пользователей — приватность и списки.
        """
        page_number = request.query_params.get('page', 1)
        blogs = Blog.objects.all().order_by('-id')

        user = request.user if request.user.is_authenticated else None

        # Только публичные блоги для неавторизованных
        if not user:  
            public_blogs = blogs.filter(is_private=False)
            page, paginator = paginate_blogs(public_blogs, page_number)
            serializer = BlogSerializer(page.object_list, many=True)
            return Response({
                'results': serializer.data,
                'count': paginator.count,
                'num_pages': paginator.num_pages,
                'page': page.number
            })

        # Админ или модератор видит все посты
        if user.is_superuser or user.groups.filter(name__in=['moderator']).exists():
            page, paginator = paginate_blogs(blogs, page_number)
            serializer = BlogSerializer(page.object_list, many=True)
            return Response({
                'results': serializer.data,
                'count': paginator.count,
                'num_pages': paginator.num_pages,
                'page': page.number
            })

        # Фильтрация по приватности и взаимным черным спискам
        visible_blogs = filter_visible_blogs(blogs, user)
        page, paginator = paginate_blogs(visible_blogs, page_number)
        serializer = BlogSerializer(page.object_list, many=True)
        return Response({
            'results': serializer.data,
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'page': page.number
        })

    @swagger_auto_schema(
        operation_description="Создание блога. Автором становится текущий пользователь.",
        request_body=BlogSerializer,
        responses={201: BlogSerializer, 400: 'Bad request'}
    )
    def post(self, request):
        """Создание блога. Автором становится текущий пользователь."""
        if not request.user or not request.user.is_authenticated:
            return Response({'error': 'Пользователь не аутентифицирован'}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = BlogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Удаление блога. Может удалить только автор, админ или модератор.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'blog_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID блога')
            }
        ),
        responses={200: openapi.Response('Blog deleted'), 403: 'Permission denied'}
    )
    def delete(self, request):
        """Удаление блога. Может удалить только автор, админ или модератор."""
        if not request.user or not request.user.is_authenticated:
            return Response({'error': 'Пользователь не аутентифицирован'}, status=status.HTTP_401_UNAUTHORIZED)
        
        blog_id = request.data.get('blog_id') or request.query_params.get('blog_id')
        blog = get_object_or_404(Blog, id=blog_id)
        user = request.user
        if blog.author == user or user.is_superuser or user.groups.filter(name__in=['moderator']).exists():
            blog.delete()
            return Response({'status': 'deleted'})
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

class UserBlogsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получение блогов пользователя по id с пагинацией (?page=1).",
        responses={200: BlogSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter('user_id', openapi.IN_PATH, description="ID пользователя", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page', openapi.IN_QUERY, description="Номер страницы", type=openapi.TYPE_INTEGER)
        ]
    )
    def get(self, request, user_id):
        """
        Получение блогов пользователя по id.
        Админ и модератор видят все посты независимо от списков.
        Приватные блоги видны только для автора и его белого списка.
        Если пользователь в черном списке автора, ничего не возвращается.
        """
        target_user = get_object_or_404(User, id=user_id)
        blogs = Blog.objects.filter(author=target_user)
        user = request.user
        page_number = request.query_params.get('page', 1)

        # Админ или модератор видит все
        if user.is_superuser or user.groups.filter(name__in=['moderator']).exists():
            page, paginator = paginate_blogs(blogs, page_number)
            serializer = BlogSerializer(page.object_list, many=True)
            return Response({
                'results': serializer.data,
                'count': paginator.count,
                'num_pages': paginator.num_pages,
                'page': page.number
            })

        # Проверка черного списка
        if hasattr(target_user, 'blacklist') and user in target_user.blacklist.all():
            return Response([])

        # Приватные блоги доступны только автору и тем, кто в белом списке
        if user == target_user:
            page, paginator = paginate_blogs(blogs, page_number)
            serializer = BlogSerializer(page.object_list, many=True)
            return Response({
                'results': serializer.data,
                'count': paginator.count,
                'num_pages': paginator.num_pages,
                'page': page.number
            })
            
        else:
            allowed_private = hasattr(target_user, 'whitelist') and user in target_user.whitelist.all()
            public_blogs = blogs.filter(is_private=False)
            private_blogs = blogs.filter(is_private=True) if allowed_private else Blog.objects.none()
            result_blogs = public_blogs | private_blogs
            page, paginator = paginate_blogs(result_blogs, page_number)
            serializer = BlogSerializer(page.object_list, many=True)
            return Response({
                'results': serializer.data,
                'count': paginator.count,
                'num_pages': paginator.num_pages,
                'page': page.number
            })
