from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import OrderViewSet, OrderConfigView, get_config_state_view, set_exception_date_view, OrderTypeViewSet

router = DefaultRouter()
router.register(r'', OrderViewSet, basename='orders')
router.register('order-types', OrderTypeViewSet, basename='order-types')

urlpatterns = router.urls

urlpatterns += [
    #path('config/test', OrderConfigView.as_view(), name='config-counts'),
    path('config/stats/', get_config_state_view, name='config-stats'),
    path('config/set-exception-date', set_exception_date_view, name='config-set-exception'),
    path('config/setup', OrderConfigView.as_view())
]
