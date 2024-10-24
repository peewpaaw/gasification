from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CounterpartyViewSet, ConstructionObjectViewSet


router = DefaultRouter()
router.register(r'counterparties', CounterpartyViewSet, basename='counterparties')
router.register(r'construction-objects', ConstructionObjectViewSet, basename='objects')

urlpatterns = router.urls

urlpatterns += [
    # path('me', UserViewSet.as_view({'get': 'list'})),
]