from rest_framework import generics
from rest_framework.permissions import AllowAny

from .serializers import MensajeSerializer


class MensajeCreateView(generics.CreateAPIView):
    """Guarda los mensajes del formulario de contacto (público)."""

    serializer_class = MensajeSerializer
    permission_classes = (AllowAny,)
    authentication_classes = ()
