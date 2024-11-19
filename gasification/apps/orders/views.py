import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from apps.utils.permissions import IsOwner

from apps.orders.services.order_status_flow import (order_accept, order_cancel,
                                                    order_on_confirm, order_agree, order_reject)

from .filters import OrderFilter
from .models import Order
from .serializers import OrderListRetrieveSerializer, OrderOnConfirmSerializer, OrderCreateSerializer, \
    OrderUpdateSerializer



class OrderViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
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

    @swagger_auto_schema(request_body=no_body)
    @action(detail=True, url_path='accept', methods=['post'], permission_classes=[IsAdminUser])
    def accept(self, request, pk):
        """
            Подтверждение заявки спец-ом СЗ.

            Заявка получит статус `accepted` на выбранную клиентом дату (`selected_date`).
        """
        instance = self.get_object()
        if order_accept(instance, self.request.user):
            return Response({'success': True}, status=status.HTTP_200_OK)
        return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, url_path='on_confirm', methods=['post'], permission_classes=[IsAdminUser])
    def on_confirm(self, request, pk):
        """
            Подтверждение переноса заявки на новую дату клиентом.

            От клиента потребуется `/agree` или `/reject`
        """
        instance = self.get_object()
        serializer = OrderOnConfirmSerializer(data=self.request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if order_on_confirm(instance, self.request.user, on_date=serializer.validated_data['on_date']):
            return Response({'success': True}, status=status.HTTP_200_OK)
        return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=no_body)
    @action(detail=True, url_path='cancel', methods=['post'], permission_classes=[IsOwner])
    def cancel(self, request, pk):
        """
            Отмена заявки клиентом.

            Отменяем только заявки со статусом `created`?
        """
        instance = self.get_object()
        if order_cancel(instance, self.request.user):
            return Response({'success': True}, status=status.HTTP_200_OK)
        return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=no_body)
    @action(detail=True, url_path='agree', methods=['post'], permission_classes=[IsOwner])
    def agree(self, request, pk):
        """
            Подтверждение переноса заявки на новую дату клиентом.

            Заявка получит статус `accepted` на предложенную спец-ом СЗ дату.
        """
        instance = self.get_object()
        if order_agree(instance, self.request.user):
            return Response({'success': True}, status=status.HTTP_200_OK)
        return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, url_path='reject', methods=['post'], permission_classes=[IsOwner])
    def reject(self, request, pk):
        """
            Отклонение переноса заявки на новую дату клиентом.

            Заявка получит статус `accepted` на первоначально выбранную клиентом дату (`selected_date`).
        """
        instance = self.get_object()
        if order_reject(instance, self.request.user):
            return Response({'success': True}, status=status.HTTP_200_OK)
        return Response({'success': False}, status=status.HTTP_200_OK)
