from rest_framework import serializers

from apps.accounts.serializers import UserAsClientViewSerializer

from .models import OrderType, Order, OrderStatusHistory, ORDER_STATUSES, ALLOWED_STATUS_TRANSITIONS


class OrderTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderType
        fields = ('order_type', 'guid')


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusHistory
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"
        extra_kwargs = {'created_by': {'default': serializers.CurrentUserDefault()}}


class OrderListRetrieveSerializer(serializers.ModelSerializer):
    order_type = OrderTypeSerializer()
    created_by = UserAsClientViewSerializer()
    status = serializers.SerializerMethodField()
    status_history = serializers.SerializerMethodField()

    def get_status(self, obj):
        serializer = OrderStatusHistorySerializer(obj.get_current_status())
        return serializer.data

    def get_status_history(self, obj):
        status_history = OrderStatusHistory.objects.filter(order=obj)
        serializer = OrderStatusHistorySerializer(status_history, many=True)
        return serializer.data

    class Meta:
        model = Order
        fields = ('id', 'construction_object', 'order_type', 'on_date', 'applicant',
                  'created_by', 'status', 'status_history', 'created_at')


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('status', 'on_date', 'employee')

    def validate(self, attrs):
        if attrs['new_status'] == 'on_confirm':
            if not attrs.get('on_date', None):
                raise serializers.ValidationError(f"Field `on_date` is required for the status `on_confirm`")
        return attrs

    def validate_status(self, value):
        if value not in ALLOWED_STATUS_TRANSITIONS[self.instance.status]:
            raise serializers.ValidationError(
                f"Invalid status transition from {self.instance.status} to {value}"
            )
        return value


class OrderAcceptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('employee',)


class OrderOnConfirmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('on_date', 'employee')


class OrderCancelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order

