from django.contrib import admin

from .models import User, ClientProfile, TokenSignup


class ClientProfileAdmin(admin.StackedInline):
    model = ClientProfile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    inlines = [ClientProfileAdmin]
    list_display = ('id', 'login', 'email', 'is_staff', 'is_approved', 'counterparty')
    list_filter = ('is_staff',)


@admin.register(TokenSignup)
class TokenSignUp(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'key')
