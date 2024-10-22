from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import UserViewSet


urlpatterns = [
    path('me', UserViewSet.as_view({'get': 'list'})),
    # path('sign-up/', UserSignupView.as_view()),
]

urlpatterns += [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    #path(r'password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset'))
]