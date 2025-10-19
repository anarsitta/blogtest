from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.utils import timezone
import jwt
from django.conf import settings
from .models import CustomUser
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    UserUpdateSerializer,
    UserProfileSerializer,
    UserListSerializer,
    ChangePasswordSerializer
)
from .authentication import generate_jwt_token, generate_refresh_token
from drf_yasg.utils import swagger_auto_schema
from django.http import JsonResponse
from .utils import set_auth_cookies, delete_auth_cookies, get_refresh_token
from django.contrib.auth.password_validation import validate_password
from rest_framework.serializers import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError


class AuthView(APIView):
    """Базовый класс для аутентификации"""
    permission_classes = [permissions.AllowAny]


class RegistrationView(AuthView):
    """Предсталвение регистрации пользователя"""
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_description="Регистрация нового пользователя",
        request_body=UserRegistrationSerializer,
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.update_activity() 
            token = generate_jwt_token(user)
            refresh_token = generate_refresh_token(user)
            
            return Response({
                'message': 'Пользователь успешно зарегистрирован',
                'access_token': token,
                'refresh_token': refresh_token,
                'user': UserProfileSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(AuthView):
    """Представление авторизации пользователя"""
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_description="Аутентификация пользователя",
        request_body=UserLoginSerializer,
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            try:
                user_obj = CustomUser.objects.get(email=email)
                user = authenticate(username=user_obj.username, password=password)
            except CustomUser.DoesNotExist:
                user = None
            
            if user:
                user.update_activity()
                access_token = generate_jwt_token(user)
                refresh_token = generate_refresh_token(user)
                response = JsonResponse({
                    'message': 'Успешный вход',
                    'user': UserProfileSerializer(user).data
                })
                response = set_auth_cookies(response, access_token, refresh_token)
                return response
            return Response({'error': 'Неверные учетные данные'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """Выход пользователя из системы"""
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Выход пользователя из системы",
    )
    def post(self, request):
        request.user.update_activity()
        response = JsonResponse({'message': 'Успешный выход'})
        response = delete_auth_cookies(response)
        return response


class TokenRefreshView(AuthView):
    """Обновление токена в случае неактивности"""
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_description="Обновление access и refresh токенов по refresh токену",
        request_body=None,
    )
    def post(self, request):
        refresh_token = get_refresh_token(request)
        
        if not refresh_token:
            return Response({'error': 'Refresh token обязателен'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
            
            if payload.get('type') != 'refresh':
                return Response({'error': 'Неверный тип токена'}, status=status.HTTP_400_BAD_REQUEST)
            
            user = CustomUser.objects.get(id=payload['user_id'])
            
            # Проверяем активность пользователя
            if not user.is_active_user():
                return Response({'error': 'Сессия истекла из-за неактивности'}, status=status.HTTP_401_UNAUTHORIZED)
            
            # Обновляем активность
            user.update_activity()
            
            # Генерируем новые токены
            new_access_token = generate_jwt_token(user)
            new_refresh_token = generate_refresh_token(user)
            
            response = JsonResponse({
                'access_token': new_access_token,
                'refresh_token': new_refresh_token,
                'user': UserProfileSerializer(user).data
            })
            response = set_auth_cookies(response, new_access_token, new_refresh_token)
            return response
            
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Refresh token истек'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({'error': 'Неверный refresh token'}, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)


class UserProfileView(APIView):
    """Представление профиля пользователя"""
    permission_classes = [permissions.IsAuthenticated] 
    
    @swagger_auto_schema(
        operation_description="Получение профиля текущего пользователя",
    )
    def get(self, request):
        request.user.update_activity()
        if not request.user or not request.user.is_authenticated:
            return Response({'error': 'Пользователь не аутентифицирован'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Обновление профиля текущего пользователя",
        request_body=UserUpdateSerializer,
    )
    def put(self, request):
        request.user.update_activity()
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Данные успешно обновлены',
                'user': UserProfileSerializer(request.user).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthorUserProfileView(APIView):
    """Получение профиля автора"""
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Публичный профиль пользователя по username",
    )
    def get(self, request, username):
        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=404)
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)


class AccountManagementView(APIView):
    """Удаление своего аккаунта"""
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Удаление собственного аккаунта",
    )
    def post(self, request):
        """Удаление аккаунта"""
        user = request.user
        user.update_activity()
        user.deactivate()
        return Response({'message': 'Аккаунт успешно деактивирован'})


class ListManagementView(APIView):
    """Работа с черным и белым списком пользователей"""
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Добавление пользователя в черный или белый список",
    )
    def post(self, request, user_id, list_type):
        """Добавление пользователя в список"""
        request.user.update_activity()
        try:
            target_user = CustomUser.objects.get(id=user_id)
            if target_user == request.user:
                return Response({'error': f'Нельзя добавить себя в {list_type} список'}, 
                                status=status.HTTP_400_BAD_REQUEST)
            
            if list_type == 'blacklist':
                # Удаляем из белого списка, если есть
                request.user.whitelist.remove(target_user)
                request.user.blacklist.add(target_user)
                message = f'Пользователь {target_user.username} добавлен в черный список'
                
            elif list_type == 'whitelist':
                # Удаляем из черного списка, если есть
                request.user.blacklist.remove(target_user)
                request.user.whitelist.add(target_user)
                message = f'Пользователь {target_user.username} добавлен в белый список'
                
            else:
                return Response({'error': 'Неверный тип списка'}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({'message': message})
        
        except CustomUser.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)
    
    @swagger_auto_schema(
        operation_description="Удаление пользователя из черного или белого списка",
    )
    def delete(self, request, user_id, list_type):
        """Удаление пользователя из списка"""
        request.user.update_activity()
        
        try:
            target_user = CustomUser.objects.get(id=user_id)
            
            if list_type == 'blacklist':
                request.user.blacklist.remove(target_user)
                message = f'Пользователь {target_user.username} удален из черного списка'
                
            elif list_type == 'whitelist':
                request.user.whitelist.remove(target_user)
                message = f'Пользователь {target_user.username} удален из белого списка'
                
            else:
                return Response({'error': 'Неверный тип списка'}, status=status.HTTP_400_BAD_REQUEST)
                
            return Response({'message': message})
            
        except CustomUser.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)


class UserListsView(APIView):
    """Получение черного и белого списков"""
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Получение черного и белого списков пользователя",
    )
    def get(self, request):
        request.user.update_activity()
        blacklist = request.user.blacklist.all()
        whitelist = request.user.whitelist.all()
        
        return Response({
            'blacklist': UserListSerializer(blacklist, many=True).data,
            'whitelist': UserListSerializer(whitelist, many=True).data
        })


class RoleManagementView(APIView):
    """Назначение ролей пользователей"""
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Назначение пользователя модератором",
    )
    def post(self, request, user_id):
        """Назначение модератора"""
        request.user.update_activity()
        
        if not request.user.can_promote_to_moderator():
            return Response({'error': 'Недостаточно прав'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            target_user = CustomUser.objects.get(id=user_id)
            
            # Проверяем, что целевой пользователь - обычный пользователь
            if not target_user.is_user():
                return Response({'error': 'Можно назначать модераторами только обычных пользователей'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # Повышаем до модератора
            if target_user.promote_to_moderator():
                return Response({
                    'message': f'Пользователь {target_user.username} повышен до модератора',
                    'user': UserProfileSerializer(target_user).data
                })
                
            else:
                return Response({'error': 'Не удалось повысить пользователя'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
        except CustomUser.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)
    
    @swagger_auto_schema(
        operation_description="Снятие роли модератора",
    )
    def delete(self, request, user_id):
        """Снятие роли модератора"""
        request.user.update_activity()
        
        if not request.user.is_superuser:
            return Response({'error': 'Недостаточно прав'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            target_user = CustomUser.objects.get(id=user_id)
            
            # Проверяем, что можем снимать права у этого пользователя
            if not request.user.can_demote_moderator(target_user):
                return Response({'error': 'Нельзя снять права с этого пользователя'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # Понижаем до обычного пользователя
            if target_user.demote_to_user():
                return Response({
                    'message': f'Пользователь {target_user.username} понижен до обычного пользователя',
                    'user': UserProfileSerializer(target_user).data
                })
            else:
                return Response({'error': 'Пользователь не является модератором'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
        except CustomUser.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)


class ModeratorManagementView(APIView):
    """Управление для модераторов"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Получение списка модераторов",
    )
    def get(self, request):
        """Получение списка всех модераторов"""
        request.user.update_activity()
        
        if not request.user.is_superuser:
            return Response({'error': 'Недостаточно прав'}, status=status.HTTP_403_FORBIDDEN)
        
        moderators = CustomUser.objects.filter(role=CustomUser.Role.MODERATOR)
        return Response({
            'moderators': UserListSerializer(moderators, many=True).data
        })


class UserDeletionView(APIView):
    """Удаление пользователя модератором"""
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Удаление пользователя",
    )
    def post(self, request, user_id):
        request.user.update_activity()
        
        try:
            target_user = CustomUser.objects.get(id=user_id)
            if not request.user.can_delete_user(target_user):
                return Response({'error': 'Недостаточно прав для удаления пользователя'}, status=status.HTTP_403_FORBIDDEN)
            target_user.deactivate()  # Мягкое удаление деактивируем пользователя
            return Response({'message': f'Пользователь {target_user.username} деактивирован'})
        except CustomUser.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)


class ChangePasswordView(APIView):
    """Смена пароля пользователем"""
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Смена пароля пользователя",
        request_body=ChangePasswordSerializer,
    )
    def post(self, request):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        old_password = serializer.validated_data.get('old_password')
        new_password = serializer.validated_data.get('new_password')
        if not user.check_password(old_password):
            return Response({'error': 'Старый пароль неверен'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            validate_password(new_password, user)
        except (ValidationError, DjangoValidationError) as e:
            errors = e.messages if hasattr(e, 'messages') else [str(e)]
            return Response({'error': errors}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        user.update_activity()
        return Response({'message': 'Пароль успешно изменен'}, status=status.HTTP_200_OK)
