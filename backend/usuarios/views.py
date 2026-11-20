from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.permissions import AllowAny

from .serializers import RegisterSerializer


class RegisterView(generics.CreateAPIView):
    """Registro de usuarios nuevos (público)."""

    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    # Sin autenticación: un token vencido en el navegador no debe bloquear el registro.
    authentication_classes = ()
    serializer_class = RegisterSerializer
