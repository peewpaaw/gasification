from datetime import datetime, timedelta

from apps.orders.models import OrderConfig, OrderConfigException


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
    if date.weekday() in [1, 2, 3, 4]:
        return order_config.order_count_per_day
    if date.weekday() in [5]:
        return order_config.order_count_friday
    if date.weekday() in [6, 7] and not order_config.weekend_disabled:
        return order_config.order_count_friday
    return 0
