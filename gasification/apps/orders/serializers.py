from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.erp.serializers import ConstructionObjectSimpleSerializer

from .models import OrderType, Order, OrderStatusHistory, ORDER_STATUSES, OrderConfig, OrderConfigException
from .services.order_config import order_can_be_created, order_creating_is_available


##########################
# ORDER TYPE SERIALIZERS #
##########################

class OrderTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderType
        fields = ('id', 'order_type', 'guid')


####################################
# ORDER STATUS HISTORY SERIALIZERS #
####################################

class OrderStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusHistory
        fields = "__all__"


#####################
# ORDER SERIALIZERS #
#####################


class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('construction_object', 'selected_date', 'applicant', 'order_type')


class OrderCreateSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    def validate(self, attrs):
        if not order_creating_is_available():
            raise ValidationError({'selected_date': f"Прием заявок закрыт."})
        if not order_can_be_created(attrs['selected_date']):
            raise ValidationError({"selected_date": f"Превышен лимит заявок на дату `{attrs['selected_date']}`"})
        return attrs

    class Meta:
        model = Order
        fields = ('construction_object', 'selected_date', 'applicant', 'order_type', 'created_by')


class OrderListRetrieveSerializer(serializers.ModelSerializer):
    construction_object = ConstructionObjectSimpleSerializer()
    order_type = OrderTypeSerializer()
    status_history = serializers.SerializerMethodField()

    def get_status_history(self, obj):
        status_history = OrderStatusHistory.objects.filter(order=obj).order_by('-created_at')
        serializer = OrderStatusHistorySerializer(status_history, many=True)
        return serializer.data

    class Meta:
        model = Order
        fields = ('id', 'construction_object', 'order_type', 'applicant',
                  'selected_date', 'on_date', 'status_history', 'created_at')


class OrderOnConfirmSerializer(serializers.Serializer):
    on_date = serializers.DateField()

    def validate_on_date(self, value):
        print('validate `on_date`!')
        return value


############################
# ORDER CONFIG SERIALIZERS #
############################

class OrderConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderConfig
        fields = "__all__"


class OrderConfigUpdateSerializer(serializers.ModelSerializer):
    updated_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = OrderConfig
        fields = ('order_count_per_day', 'order_count_friday',
                  'time_start', 'time_end', 'updated_by')


class OrderConfigExceptionCreateSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = OrderConfigException
        fields = ('on_date', 'order_count_per_day', 'created_by')


class OrderConfigStatsQuerySerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
