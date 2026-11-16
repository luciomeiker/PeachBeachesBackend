from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Mensaje
from .serializers import MensajeSerializer

class MensajeCreateView(generics.CreateAPIView):
    queryset = Mensaje.objects.all()
    serializer_class = MensajeSerializer
    permission_classes = [AllowAny]