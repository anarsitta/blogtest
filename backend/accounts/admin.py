from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'date_joined', 'last_activity', 'is_staff')
    list_filter = ('role', 'is_staff', 'date_joined')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('role', 'blacklist', 'whitelist', 'last_activity')
        }),
    )
    
    actions = ['promote_to_moderator', 'demote_to_user']
    
    def promote_to_moderator(self, request, queryset):
        """Действие для назначения модераторов"""
        for user in queryset:
            if user.is_user():
                user.promote_to_moderator()
        self.message_user(request, "Выбранные пользователи назначены модераторами")
    promote_to_moderator.short_description = "Назначить модераторами"
    
    def demote_to_user(self, request, queryset):
        """Действие для снятия прав модераторов"""
        for user in queryset:
            if user.is_moderator() and user != request.user:
                user.demote_to_user()
        self.message_user(request, "Выбранные модераторы понижены до пользователей")
    demote_to_user.short_description = "Снять права модераторов"
    
    def get_readonly_fields(self, request, obj=None):
        if obj and not request.user.is_superuser:
            return ('role',) + self.readonly_fields
        return self.readonly_fields