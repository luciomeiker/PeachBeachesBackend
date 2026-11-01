from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Carrito
from .serializers import CarritoSerializer

class CarritoViewSet(viewsets.ModelViewSet):
    queryset = Carrito.objects.all()
    serializer_class = CarritoSerializer
    
    # 👇 AQUÍ ES DONDE VA LA CONFIGURACIÓN DEL PASO 4
    permission_classes = [IsAuthenticated]
