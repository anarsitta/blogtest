import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone
from datetime import timedelta


class JWTAuthentication(authentication.BaseAuthentication):
    """
    Кастомная JWT аутентификация
    """
    def authenticate(self, request):
        # Сначала пробуем взять токен из заголовка
        auth_header = request.META.get('HTTP_AUTHORIZATION') or request.headers.get('Authorization')
        token = None
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        else:
            # Если нет заголовка, пробуем взять токен из cookie
            token = request.COOKIES.get('access_token')
        if not token:
            return None

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            
            # Проверяем expiration токена
            if int(payload['exp']) < int(timezone.now().timestamp()):
                raise AuthenticationFailed('Токен истек')
            
            user = get_user_model().objects.get(id=payload['user_id'])
            
            # Проверяем активность пользователя
            if not self.is_active_user(user):
                raise AuthenticationFailed('Сессия истекла из-за неактивности')
            
            # Обновляем время активности при каждом запросе
            self.update_user_activity(user)
            return (user, token)
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Токен истек')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Неверный токен')
        except get_user_model().DoesNotExist:
            raise AuthenticationFailed('Пользователь не найден')

    def is_active_user(self, user):
        """Проверяет, активен ли пользователь (была ли активность в течение часа)"""
        if not hasattr(user, 'last_activity'):
            return True  # Если поля нет, считаем пользователя активным
        
        return (timezone.now() - user.last_activity).total_seconds() < 3600

    def update_user_activity(self, user):
        """Обновляет время последней активности пользователя"""
        if hasattr(user, 'update_activity'):
            user.update_activity()
        elif hasattr(user, 'last_activity'):
            user.last_activity = timezone.now()
            user.save(update_fields=['last_activity'])


def generate_jwt_token(user):
    """Генерация JWT токена"""
    payload = {
        'user_id': user.id,
        'username': user.username,
        'role': user.role if hasattr(user, 'role') else 'US',
        'exp': timezone.now() + timedelta(hours=1),
        'iat': timezone.now(),
        'type': 'access'
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


def generate_refresh_token(user):
    """Генерация refresh токена"""
    payload = {
        'user_id': user.id,
        'exp': timezone.now() + timedelta(days=1),
        'iat': timezone.now(),
        'type': 'refresh'
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
