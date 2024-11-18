import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from apps.utils.permissions import IsOwner

from apps.orders.services.order_status_flow import order_accept

from .filters import OrderFilter
from .models import Order
from .serializers import OrderListRetrieveSerializer, OrderOnConfirmSerializer, OrderCreateSerializer, \
    OrderUpdateSerializer



class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    filter_backends = [DjangoFilterBackend, SearchFilter,]
    filterset_class = OrderFilter

    def get_serializer_class(self):
        if self.action in ('create',):
            return OrderCreateSerializer
        if self.action in ('update', 'partial_update'):
            return OrderUpdateSerializer
        if self.action in ('list', 'retrieve',):
            return OrderListRetrieveSerializer
        if self.action == 'on_confirm':
            return OrderOnConfirmSerializer
        if self.action in ('accept', 'cancel', 'agree', 'disagree'):
            return None

        return None

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Order.objects.none()

        queryset = Order.objects.all()

        if not self.request.user.is_staff:
           queryset = queryset.filter(created_by=self.request.user)
        return queryset

    @swagger_auto_schema(request_body=no_body, operation_description="accept description", operation_summary="summary")
    @action(detail=True, url_path='accept', methods=['post'], permission_classes=[IsAdminUser])
    def accept(self, request, pk):
        instance = self.get_object()
        if order_accept(instance, self.request.user):
            return Response({'success': True}, status=status.HTTP_200_OK)
        return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, url_path='on_confirm', methods=['post'], permission_classes=[IsAdminUser])
    def on_confirm(self, request, pk):
        instance = self.get_object()
        return Response({'success': True}, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=no_body)
    @action(detail=True, url_path='cancel', methods=['post'], permission_classes=[IsOwner])
    def cancel(self, request, pk):
        instance = self.get_object()
        return Response({'success': True}, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=no_body)
    @action(detail=True, url_path='agree', methods=['post'], permission_classes=[IsOwner])
    def agree(self, request, pk):
        """
            Подтверждение переноса заявки на новую дату клиентом.

            Заявка получит статус "accepted" на предложенную дату.
        """
        instance = self.get_object()
        return Response({'success': True}, status=status.HTTP_200_OK)

    @action(detail=True, url_path='disagree', methods=['post'], permission_classes=[IsOwner])
    def disagree(self, request, pk):
        instance = self.get_object()
        return Response({'success': True}, status=status.HTTP_200_OK)
