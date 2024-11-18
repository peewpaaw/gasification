from rest_framework import serializers

from apps.erp.serializers import ConstructionObjectSimpleSerializer

from .models import OrderType, Order, OrderStatusHistory, ORDER_STATUSES


##########################
# ORDER TYPE SERIALIZERS #
##########################

class OrderTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderType
        fields = ('order_type', 'guid')


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
