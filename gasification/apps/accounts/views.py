from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import User
from .serializers import UserSerializer, UserInfoSerializer


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserInfoSerializer

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

