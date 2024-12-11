from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema, no_body

from apps.utils.permissions import IsOwner

from apps.orders.services.order_status_flow import (order_accept, order_cancel,
                                                    order_on_confirm, order_agree, order_reject)
from apps.orders.services.order_config import get_order_count_per_day_for_period

from .filters import OrderFilter
from .models import Order, OrderConfig, OrderConfigException, OrderType
from .serializers import OrderListRetrieveSerializer, OrderOnConfirmSerializer, OrderCreateSerializer, \
    OrderUpdateSerializer, OrderConfigSerializer, OrderConfigExceptionCreateSerializer, OrderConfigStatsQuerySerializer, \
    OrderConfigUpdateSerializer, OrderTypeSerializer


class OrderViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, ]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['selected_date', 'on_date', 'created_at']
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

        queryset = Order.objects.all().order_by('-on_date', '-selected_date')
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
            Отправка заявки на согласование клиенту с новой датой.

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

    @swagger_auto_schema(request_body=no_body)
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


class OrderTypeViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = OrderType.objects.all()
    serializer_class = OrderTypeSerializer


class OrderConfigView(APIView):
    my_instance = OrderConfig.objects.all()

    @swagger_auto_schema(
        tags=['config'],
    )
    def get(self, request, *args, **kwargs):
        """
            Получение базовых ограничений по количеству заявок

            Действуют в течение всего времени, кроме дней, заданных через `/set-exception-date`
        """
        serializer_class = OrderConfigSerializer
        serializer = serializer_class(self.my_instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=['config'],
        request_body=OrderConfigUpdateSerializer,
    )
    def put(self, request, *args, **kwargs):
        """
            Изменение базовых ограничений по количеству заявок

            Действуют в течение всего времени, кроме дней, заданных через `/set-exception-date`
        """
        serializer_class = OrderConfigUpdateSerializer
        serializer = serializer_class(self.my_instance.first(), data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    tags=['config'],
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'start_date',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=True  # This makes the parameter required
        ),
        openapi.Parameter(
            'end_date',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=True  # This makes the parameter required
        ),
    ]
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_config_state_view(request, *args, **kwargs):
    """
        Получение статистики по допустимому количеству заявок

        Возвращает максимально допустимое количество заявок на каждую дату из периода (для календаря спец-ов СЗ)
    """
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if not start_date or not end_date:
        return Response({"detail": "Required parameters in the query string are missing"},
                        status=status.HTTP_400_BAD_REQUEST)

    result = get_order_count_per_day_for_period(start_date=start_date, end_date=end_date)

    return Response({"result": result}, status=status.HTTP_200_OK)


@swagger_auto_schema(
    tags=['config'],
    method='post',
    request_body=OrderConfigExceptionCreateSerializer,
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def set_exception_date_view(request, *args, **kwargs):
    """
        Устанавливает ограничения по количеству заявок на отдельные даты

        Используем для сокращенных дней, выходных дней (устанавливаем 0)
    """
    serializer_class = OrderConfigExceptionCreateSerializer
    serializer_params = {
        "data": request.data,
        "context": {"request": request},
    }

    # if exception exist for this date -> updating
    if request.data.get('on_date'):
        existing_exception = OrderConfigException.objects.filter(on_date=request.data['on_date'])
        if existing_exception:
            serializer_params['instance'] = existing_exception.first()

    serializer = serializer_class(**serializer_params)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
