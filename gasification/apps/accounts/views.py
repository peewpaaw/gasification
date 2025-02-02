from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView

from ..utils.paginations import CustomPageNumberPagination

from .services.notifications import send_signup_confirmation_email

from .models import User, TokenSignup
from .serializers import UserAsClientListRetrieveSerializer, UserAsClientCreateUpdateSerializer, UserInfoSerializer, \
    UserAsStaffViewSerializer, UserAsStaffCreateSerializer, ClientSignUpSerializer, ClientSignUpValidateTokenSerializer, \
    CustomTokenObtainPairSerializer


class UserAsClientViewSet(viewsets.ModelViewSet):
    """
        API endpoints for clients
    """
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAdminUser]
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve',):
            return UserAsClientListRetrieveSerializer
        return UserAsClientCreateUpdateSerializer

    def get_queryset(self):
        return User.objects.filter(is_staff=False)

    @swagger_auto_schema(tags=['clients'], operation_summary="Получение списка пользователей")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['clients'], operation_summary="Получение детальной информации о пользователе")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=['clients'], operation_summary="Создание нового пользователя администратором")
    def create(self, request, *args, **kwargs):
        """
            Пользователю будет выслан сгенерированный токен для `/accounts/sign-up/confirm`.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            TokenSignup.objects.create(user=obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=['clients'],
        operation_summary="Повторная отправка письма для подтверждения регистрации",
        request_body=no_body
    )
    @action(detail=True, url_path='resend-signup-email', methods=['post'], permission_classes=[IsAdminUser])
    def resend_signup_confirmation_email(self, request, pk):
        instance = self.get_object()
        if instance.is_approved:
            return Response({"detail": "User is already registered."}, status=status.HTTP_400_BAD_REQUEST)
        token = TokenSignup.objects.filter(user=instance)
        if not token.exists():
            return Response({"detail": "User has no active token."}, status=status.HTTP_400_BAD_REQUEST)
        send_signup_confirmation_email(token.first())
        return Response({"detail": "Email sent."}, status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=['clients'], operation_summary="Обновление пользователя")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['clients'], operation_summary="Блокирует пользователя")
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response({"detail": "User has been deactivated."}, status=status.HTTP_204_NO_CONTENT)


class UserAsStaffViewSet(viewsets.ModelViewSet):
    """
        API endpoints for staff
    """
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAdminUser]
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve',):
            return UserAsStaffViewSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return UserAsStaffCreateSerializer

    def get_queryset(self):
        return User.objects.filter(is_staff=True)

    @swagger_auto_schema(tags=['staff'], operation_summary="Получение списка пользователей")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['staff'], operation_summary="Получение детальной информации о пользователе")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=['staff'], operation_summary="Создание пользователя")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(tags=['staff'], operation_summary="Обновление пользователя")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['staff'], operation_summary="Удаление пользователя")
    def destroy(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


class UserMeView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserInfoSerializer

    @swagger_auto_schema(operation_summary="Получение информации по текущему пользователю")
    def get(self, request):
        serializer_data = UserInfoSerializer(self.request.user).data
        return Response(serializer_data, status=status.HTTP_200_OK)


class ClientSignUpView(APIView):
    """Sign-up confirmations"""
    serializer_class = ClientSignUpSerializer

    @swagger_auto_schema(request_body=ClientSignUpSerializer)
    def post(self, request):
        """
            Подтверждение регистрации клиентом

            Токен высылается пользователю после создания клиента администратором.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = TokenSignup.objects.filter(key=serializer.validated_data['token']).first()

        if not token:
            return Response({"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

        token.user.set_password(serializer.validated_data['password'])
        token.user.is_approved = True
        token.user.save()

        TokenSignup.objects.filter(user=token.user).delete()
        return Response({"status": "OK"}, status=status.HTTP_200_OK)


class ClientSignUpValidateTokenView(APIView):
    serializer_class = ClientSignUpValidateTokenSerializer

    @swagger_auto_schema(request_body=ClientSignUpValidateTokenSerializer)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = TokenSignup.objects.get(key=serializer.validated_data['token'])
        response = {
            "status": "OK",
            "name": token.user.name,
            "email": token.user.email,
        }
        return Response(response, status=status.HTTP_200_OK)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@api_view(['GET'])
def send_task_view(request, *args, **kwargs):
    """
        Тестовая задача для Celery
    """
    from apps.services.tasks import test_task
    test_task.delay()
    return Response({"status": "OK"}, status=status.HTTP_200_OK)
