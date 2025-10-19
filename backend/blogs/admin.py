from django.contrib import admin
from .models import Blog

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_private', 'short_description')
    search_fields = ('title', 'author__username', 'description')
    list_filter = ('is_private', 'author')
    list_editable = ('is_private',)
    readonly_fields = ('author',)
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'is_private', 'author')
        }),
    )

    def short_description(self, obj):
        return (obj.description[:75] + '...') if len(obj.description) > 75 else obj.description
    short_description.short_description = 'Description'
