from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CounterpartyViewSet, ConstructionObjectViewSet
from .views import CounterpartyUploadView, ConstructionObjectUploadView


router = DefaultRouter()
router.register(r'counterparties', CounterpartyViewSet, basename='counterparties')
router.register(r'construction-objects', ConstructionObjectViewSet, basename='objects')

urlpatterns = router.urls

urlpatterns += [
    path('upload/counterparties/', CounterpartyUploadView.as_view()),
    path('upload/construction-objects/', ConstructionObjectUploadView.as_view()),
]