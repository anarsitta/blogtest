from django.urls import path
from .views import BlogAPIView, UserBlogsAPIView

urlpatterns = [
    # Работа с блогами
    path('feed/', BlogAPIView.as_view(), name='blog-feed'),
    path('user/id/<int:user_id>/blogs/', UserBlogsAPIView.as_view(), name='user-blogs-by-id'),
]
