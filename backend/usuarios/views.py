<<<<<<< HEAD
from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from .serializers import RegisterSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer
=======
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
>>>>>>> 203f5b15f623e7978912f665dbd8f9d47779e807
