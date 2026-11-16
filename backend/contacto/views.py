<<<<<<< HEAD
from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Mensaje
from .serializers import MensajeSerializer

class MensajeCreateView(generics.CreateAPIView):
    queryset = Mensaje.objects.all()
    serializer_class = MensajeSerializer
    permission_classes = [AllowAny]
=======
from rest_framework import generics
from rest_framework.permissions import AllowAny

from .serializers import MensajeSerializer


class MensajeCreateView(generics.CreateAPIView):
    """Guarda los mensajes del formulario de contacto (público)."""

    serializer_class = MensajeSerializer
    permission_classes = (AllowAny,)
    authentication_classes = ()
>>>>>>> 203f5b15f623e7978912f665dbd8f9d47779e807
