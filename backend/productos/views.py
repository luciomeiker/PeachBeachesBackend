from django.shortcuts import render
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Categoria, Producto
from .serializers import CategoriaSerializer, ProductoSerializer

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all().order_by('id')
    serializer_class = ProductoSerializer
    
    # Habilitamos los backends de filtrado, búsqueda y ordenamiento
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    # c.iii) Filtro por categoría y rango de precio
    filterset_fields = ['categoria', 'precio'] 
    
    # c.iii) Búsqueda por nombre (también puedes incluir descripción si gustas)
    search_fields = ['nombre', 'marca']
    
    # c.iii) Ordenamiento por precio, nombre, etc.
    ordering_fields = ['precio', 'nombre', 'stock']