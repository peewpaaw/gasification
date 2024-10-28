from django.contrib import admin

from .models import User, ClientProfile


class ClientProfileAdmin(admin.StackedInline):
    model = ClientProfile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    inlines = [ClientProfileAdmin]
    list_display = ('id', 'login', 'email', 'is_staff')
