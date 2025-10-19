from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import EmailValidator
from django.utils import timezone
from .managers import CustomUserManager  # <-- Import your manager

# Создание кастомного класса пользователя
class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        SUPERUSER = 'SU', 'Суперпользователь'
        MODERATOR = 'MO', 'Модератор'
        USER = 'US', 'Пользователь'

    role = models.CharField(
        max_length=2,
        choices=Role.choices,
        default=Role.USER,
        verbose_name='Роль'
    )
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        verbose_name='Email'
    )
    blacklist = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='blacklisted_by',
        blank=True,
        verbose_name='Черный список'
    )
    whitelist = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='whitelisted_by',
        blank=True,
        verbose_name='Белый список'
    )
    last_activity = models.DateTimeField(
        default=timezone.now,
        verbose_name='Последняя активность'
    )

    date_joined = models.DateTimeField(
        default=timezone.now, 
        verbose_name='Дата регистрации'
    )
    
    # Устанавливаю кастомного менеджера
    objects = CustomUserManager()

    def is_moderator(self):
        """Пользователь является модератором"""
        return self.role == self.Role.MODERATOR

    def is_user(self):
        """Пользователь"""
        return self.role == self.Role.USER

    def can_delete_user(self, target_user):
        """Модератор может удалять только обычных пользователей"""
        return (self.is_moderator() and target_user.is_user()) or self.is_superuser

    def can_promote_to_moderator(self):
        """Только суперпользователь может назначать модераторов"""
        return self.is_superuser
    
    def can_demote_moderator(self, target_user):
        """Только суперпользователь может снимать модераторов, и нельзя снимать себя"""
        return self.is_superuser and target_user != self and target_user.is_moderator()
    
    def promote_to_moderator(self):
        """Повышение до модератора"""
        if self.role == self.Role.USER:
            self.role = self.Role.MODERATOR
            self.save(update_fields=['role'])
            return True
        return False

    def demote_to_user(self):
        """Понижение до обычного пользователя"""
        if self.role == self.Role.MODERATOR:
            self.role = self.Role.USER
            self.save(update_fields=['role'])
            return True
        return False
    
    def update_activity(self):
        """Обновляет время последней активности"""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])

    def is_active_user(self):
        """Проверяет, активен ли пользователь"""
        return (timezone.now() - self.last_activity).total_seconds() < 3600


    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    class Meta:
        unique_together = [['username', 'email']]
        
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
