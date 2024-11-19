from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import User, ClientProfile

from apps.erp.models import Counterparty
from apps.erp.serializers import CounterpartySimpleSerializer


##############################
# USER AS CLIENT SERIALIZERS #
##############################

class UserAsClientViewSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'login', 'email', 'name', 'last_login', 'is_active', 'counterparty',)


class UserAsClientCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message="Пользователь с такой почтой уже существует.",
        )],)
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password])

    class Meta:
        model = User
        fields = ('email', 'password', 'counterparty')

    def create(self, validated_data):
        user = User.objects.create(
            login=validated_data['counterparty'].inn,
            email=validated_data['email'],
            is_staff=False,
            counterparty=validated_data['counterparty'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


##############################
# USERS AS STAFF SERIALIZERS #
##############################

class UserAsStaffViewSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'login', 'email', 'name', 'last_login', 'is_active', )


class UserAsStaffCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password])
    login = serializers.CharField(
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message="Сотрудник с таким табельным номером уже существует.",
        )])
    name = serializers.CharField()

    class Meta:
        model = User
        fields = ('email', 'password', 'login', 'name')

    def create(self, validated_data):
        user = User.objects.create(
            login=validated_data['tab_number'],
            email=validated_data['email'],
            is_staff=True,
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


#########################
# USER INFO SERIALIZERS #
#########################

class UserInfoSerializer(serializers.ModelSerializer):
    counterparty = CounterpartySimpleSerializer()

    class Meta:
        model = User
        fields = ('id', 'login', 'email', 'name', 'is_staff', 'is_active', 'counterparty')
