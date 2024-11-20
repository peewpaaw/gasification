from django.contrib import admin

from .models import OrderType, Order, OrderStatusHistory, OrderConfig, OrderConfigException

# Register your models here.


class OrderStatusHistoryInlineAdmin(admin.StackedInline):
    model = OrderStatusHistory


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'status', 'created_at', 'created_by')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderStatusHistoryInlineAdmin]
    list_display = ('id', 'on_date', 'construction_object', 'order_type')


@admin.register(OrderType)
class OrderTypeAdmin(admin.ModelAdmin):
    list_display = ('order_type',)


@admin.register(OrderConfig)
class OrderConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_count_per_day', 'order_count_friday', 'weekend_disabled')


@admin.register(OrderConfigException)
class OrderConfigExceptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'on_date', 'order_count_per_day', 'created_at', 'created_by')
