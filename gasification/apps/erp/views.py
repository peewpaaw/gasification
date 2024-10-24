from rest_framework import viewsets

from .models import Counterparty, ConstructionObject
from .serializers import CounterpartySerializer, ConstructionObjectSerializer


class CounterpartyViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        return CounterpartySerializer

    def get_queryset(self):
        return Counterparty.objects.all()


class ConstructionObjectViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        return ConstructionObjectSerializer

    def get_queryset(self):
        return ConstructionObject.objects.all()
