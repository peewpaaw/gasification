from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import User, ClientProfile

from apps.erp.models import Counterparty
from apps.erp.serializers import CounterpartySerializer


##############################
# CLIENT PROFILE SERIALIZERS #
##############################

class ClientProfileSerializer(serializers.ModelSerializer):
    counterparty = CounterpartySerializer()

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
        fields = ('id', 'login', 'email', 'last_login', 'is_staff', 'is_active', 'client',)


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
    client_profile = serializers.SerializerMethodField()

    def get_client_profile(self, obj):
        client = getattr(obj, "client", None)
        if client:
            return ClientProfileSerializer(client).data

    class Meta:
        model = User
        fields = ('login', 'email', 'is_staff', 'is_active', 'client_profile')
