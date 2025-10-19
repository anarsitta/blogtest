from django.urls import path
from . import views

urlpatterns = [
    # Аутентификация
    path('register/', views.RegistrationView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('token/refresh/', views.TokenRefreshView.as_view(), name='token-refresh'),
    
    # Профиль пользователя
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('profile/<str:username>/', views.AuthorUserProfileView.as_view(), name='public-user-profile'),
    path('profile/delete/', views.AccountManagementView.as_view(), name='delete-account'),
    
    # Управление списками
    path('lists/', views.UserListsView.as_view(), name='user-lists'),
    path('lists/<str:list_type>/<int:user_id>/', views.ListManagementView.as_view(), name='add-to-list'),
    
    # Управление ролями (только для суперпользователей)
    path('roles/<int:user_id>/', views.RoleManagementView.as_view(), name='promote-to-moderator'),
    path('roles/moderators/', views.ModeratorManagementView.as_view(), name='list-moderators'),
    
    # Удаление пользователей
    path('moderator/delete-user/<int:user_id>/', views.UserDeletionView.as_view(), name='delete-user'),
    
    # Обновление пароля
    path('change-password/', views.ChangePasswordView.as_view(), name='password-reset-request'),
]
