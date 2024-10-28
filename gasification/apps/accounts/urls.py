from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import UserAsClientViewSet, UserMeView


router = DefaultRouter()
router.register(r'clients', UserAsClientViewSet, basename='users')

urlpatterns = router.urls


urlpatterns += [
    path('me/', UserMeView.as_view()),
]

urlpatterns += [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns += [
    path(r'password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset'))
]