from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from .models import Counterparty, ConstructionObject
from .serializers import CounterpartySerializer, ConstructionObjectSerializer


class CounterpartyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        return CounterpartySerializer

    def get_queryset(self):
        return Counterparty.objects.all()


class ConstructionObjectViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return ConstructionObjectSerializer

    def get_queryset(self):
        queryset = ConstructionObject.objects.all()
        if self.request.user.is_authenticated and not self.request.user.is_staff:
            queryset = queryset.filter(counterparty=self.request.user.client.counterparty)
        return queryset
