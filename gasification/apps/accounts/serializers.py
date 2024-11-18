from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import User, ClientProfile

from apps.erp.models import Counterparty
from apps.erp.serializers import CounterpartySimpleSerializer


##############################
# CLIENT PROFILE SERIALIZERS #
##############################

class ClientProfileSerializer(serializers.ModelSerializer):
    counterparty = CounterpartySimpleSerializer()

    class Meta:
        model = ClientProfile
        fields = ('counterparty', )


class ClientProfileCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClientProfile
        fields = ('counterparty', )


##########################
# USER AS CLIENT CONTROL #
##########################

class UserAsClientViewSerializer(serializers.ModelSerializer):
    client = ClientProfileSerializer()

    class Meta:
        model = User
        fields = ('id', 'login', 'email', 'name', 'last_login', 'is_active', 'client',)


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

    client = ClientProfileCreateSerializer()

    class Meta:
        model = User
        fields = ('email', 'password', 'client')

    def create(self, validated_data):
        counterparty = validated_data['client']['counterparty']
        user = User.objects.create(
            login=counterparty.inn,
            email=validated_data['email'],
            is_staff=False,
        )
        user.set_password(validated_data['password'])
        user.save()

        ClientProfile.objects.create(
            user=user,
            counterparty=counterparty
        )

        return user


##########################
# USERS INFO SERIALIZERS #
##########################

class UserInfoSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField()

    def get_client(self, obj):
        client = getattr(obj, "client", None)
        if client:
            return ClientProfileSerializer(client).data

    class Meta:
        model = User
        fields = ('id', 'login', 'email', 'name', 'is_staff', 'is_active', 'client')
