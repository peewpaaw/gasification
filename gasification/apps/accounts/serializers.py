from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.erp.serializers import CounterpartySimpleSerializer

from .models import User, TokenSignup


##############################
# USER AS CLIENT SERIALIZERS #
##############################

class UserAsClientListRetrieveSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'login', 'email', 'name', 'last_login', 'is_active', 'counterparty',)


class UserAsClientCreateUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
    )
    class Meta:
        model = User
        fields = ('email', 'counterparty')

    def create(self, validated_data):
        user = User.objects.create(
            login=validated_data['counterparty'].inn,
            name=validated_data['counterparty'].name,
            email=validated_data['email'],
            is_staff=False,
            is_active=True,
            is_approved=False,
            counterparty=validated_data['counterparty'],
        )
        #user.set_password(validated_data['password'])
        user.save()
        return user


class ClientSignUpSerializer(serializers.ModelSerializer):
    token = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password])

    class Meta:
        model = User
        fields = ('password', 'token')

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])


class ClientSignUpValidateTokenSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate_token(self, value):
        try:
            token = TokenSignup.objects.get(key=value)
        except TokenSignup.DoesNotExist:
            raise serializers.ValidationError('Invalid token')
        # check if expire
        return value


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


#########################
# SIMPLEJWT SERIALIZERS #
#########################

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        if not self.user.is_approved:
            raise AuthenticationFailed("Учетная запись не подтверждена.", code='authorization')

        if not self.user.is_active:
            raise AuthenticationFailed("Учетная запись заблокирована.", code='authorization')

        return data