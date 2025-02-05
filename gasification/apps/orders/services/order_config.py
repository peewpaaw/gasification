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
    """Returns the maximum allowed number of Orders per day"""
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

def order_can_be_created(on_date) -> bool:
    """Check if order can be created: compares the maximum number of Orders"""
    order_count = Order.objects.filter(selected_date=on_date).count()
    if order_count < _get_order_count_per_day_on_date(on_date, OrderConfig.get_related_config()):
        return True
    return False

def order_creating_is_available() -> bool:
    """Check if Order acceptance is available"""
    order_config = OrderConfig.get_related_config()
    if order_config.time_start <= datetime.now().time() <= order_config.time_end:
        return True
    return False

def get_available_dates() -> list:
    """Returns the list of dates available for Orders"""
    order_config = OrderConfig.get_related_config()

    start_date = datetime.now().date() + timedelta(days=order_config.min_date)
    end_date = datetime.now().date() + timedelta(days=order_config.max_date)
    period = get_stats_structure(start_date, end_date)
    result = []
    for item in period:
        if _get_order_count_per_day_on_date(item, order_config) > get_active_order_count_on_date(item):
            result.append(datetime.strftime(item, '%Y-%m-%d'))
    return result

def get_stats_structure(start_date, end_date):
    result = []
    current_date = start_date
    while current_date <= end_date:
        result.append(current_date)
        current_date += timedelta(days=1)
    return result

def get_active_order_count_on_date(on_date) -> int:
    """Returns the number of active Orders"""
    accepted = Order.objects.get_by_statuses(statuses=['accepted'])\
                .filter(on_date=on_date).count()
    in_process = Order.objects.get_by_statuses(statuses=['created', 'on_confirm'])\
                    .filter(selected_date=on_date).count()
    return accepted + in_process