from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import RegisterView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    # Devuelve los tokens "access" y "refresh"
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # Renueva el access token a partir del refresh token
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
