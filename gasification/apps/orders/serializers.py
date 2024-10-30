from rest_framework import serializers

from apps.accounts.serializers import UserAsClientViewSerializer

from .models import OrderType, Order, OrderStatusHistory


class OrderTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderType
        fields = ('order_type', 'guid')


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
        fields = ('construction_object', 'order_type', 'on_date', 'applicant',
                  'created_by', 'status', 'status_history', 'created_at')


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusHistory
        fields = "__all__"
