from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from apps.utils.permissions import IsOwner

from .models import Order
from .serializers import OrderSerializer, OrderListRetrieveSerializer


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve', ):
            return OrderListRetrieveSerializer
        return OrderSerializer

    def get_queryset(self):
        queryset = Order.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(created_by=self.request.user)
        return queryset

    @action(detail=True, url_path='accept', methods=['path', 'put'], permission_classes=[IsAdminUser])
    def accept(self, request, pk):
        instance = self.get_object()
        instance.accept(self.request.user)
        return Response({'success': True}, status=status.HTTP_200_OK)

    @action(detail=True, url_path='cancel', methods=['path', 'put'],
            permission_classes=[IsAdminUser, IsOwner])
    def cancel(self, request, pk):
        instance = self.get_object()
        instance.cancel(self.request.user)
        return Response({'success': True}, status=status.HTTP_200_OK)
