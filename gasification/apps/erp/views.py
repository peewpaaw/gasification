from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from .models import Counterparty, ConstructionObject
from .serializers import CounterpartySerializer, ConstructionObjectSerializer


class CounterpartyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Counterparty.objects.all()
    serializer_class = CounterpartySerializer
    permission_classes = [IsAdminUser]


class ConstructionObjectViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ConstructionObjectSerializer

    def get_queryset(self):
        queryset = ConstructionObject.objects.all()
        if self.request.user.is_authenticated and not self.request.user.is_staff:
            queryset = queryset.filter(counterparty=self.request.user.counterparty)
        return queryset
