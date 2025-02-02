from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import UserAsClientViewSet, UserAsStaffViewSet, UserMeView, CustomTokenObtainPairView
from .views import ClientSignUpView, send_task_view, ClientSignUpValidateTokenView


router = DefaultRouter()
router.register(r'clients', UserAsClientViewSet, basename='clients')
router.register(r'staff', UserAsStaffViewSet, basename='staff')

urlpatterns = router.urls

urlpatterns += [
    path('me/', UserMeView.as_view(), name='me'),
    path('signup/confirm/', ClientSignUpView.as_view(), name='signup'),
    path('signup/validate_token/', ClientSignUpValidateTokenView.as_view(), name='validate_token'),
    path('test-task/', send_task_view)
]

# TOKEN
urlpatterns += [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# PASSWORD RESET
urlpatterns += [
    path(r'password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset'))
]