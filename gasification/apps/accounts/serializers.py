from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('login', 'email', 'is_staff', 'is_active')
