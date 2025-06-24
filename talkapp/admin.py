from django.contrib import admin
from .views import CustomUser, OneTimePassword
# Register your models here.

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'first_name', 'last_name', 'talk_id', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active')
    ordering = ('-date_joined',)
    list_per_page = 100
    fieldsets = (
        (None, {'fields': ('email', 'password', 'talk_id', 'email_verified', 'availability', 'marketing_emails')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(OneTimePassword)