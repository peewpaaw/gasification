from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import User
from .serializers import UserAsClientViewSerializer, UserAsClientCreateSerializer, UserInfoSerializer, \
    UserAsStaffViewSerializer, UserAsStaffCreateSerializer


class UserAsClientViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve',):
            return UserAsClientViewSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return UserAsClientCreateSerializer

    def get_queryset(self):
        return User.objects.filter(is_staff=False)


class UserAsStaffViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve',):
            return UserAsStaffViewSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return UserAsStaffCreateSerializer

    def get_queryset(self):
        return User.objects.filter(is_staff=True)


class UserMeView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserInfoSerializer

    def get(self, request):
        serializer_data = UserInfoSerializer(self.request.user).data
        return Response(serializer_data, status=status.HTTP_200_OK)


