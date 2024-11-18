import django_filters

from apps.orders.models import ORDER_STATUSES


class OrderFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=ORDER_STATUSES, method='filter_status')

    def filter_status(self, queryset, name, value):
        queryset = queryset.model.objects.get_by_status(value)
        return queryset