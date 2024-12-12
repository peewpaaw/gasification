from datetime import datetime, timedelta

from apps.orders.models import OrderConfig, OrderConfigException, Order


def get_order_count_per_day_for_period(start_date, end_date):
    order_config = OrderConfig.objects.order_by('-created_at').first()

    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    result = _get_order_count_per_day_for_period(start_date, end_date, order_config)

    return result


def _get_order_count_per_day_for_period(start_date, end_date, order_config):
    result = []

    current_date = start_date
    while current_date <= end_date:
        date_dict = dict()
        date_dict["date"] = datetime.strftime(current_date, '%Y-%m-%d')
        date_dict["order_count"] = _get_order_count_per_day_on_date(current_date, order_config=order_config)
        result.append(date_dict)
        current_date += timedelta(days=1)
    return result


def _get_order_count_per_day_on_date(date: datetime, order_config: OrderConfig) -> int:
    exception_date = OrderConfigException.objects.filter(on_date=date)
    if exception_date.exists():
        return exception_date.first().order_count_per_day
    # Monday - Thursday
    if date.weekday() in [0, 1, 2, 3]:
        return order_config.order_count_per_day
    # Friday
    if date.weekday() in [4]:
        return order_config.order_count_friday
    # Saturday, Sunday
    if date.weekday() in [5, 6] and not order_config.weekend_disabled:
        return order_config.order_count_friday
    return 0

def order_can_be_created(on_date):
    order_count = Order.objects.filter(selected_date=on_date).count()
    if order_count < _get_order_count_per_day_on_date(on_date, OrderConfig.get_related_config()):
        return True
    return False

def order_creating_is_available():
    order_config = OrderConfig.get_related_config()
    if order_config.time_start <= datetime.now().time() <= order_config.time_end:
        return True
    return False
