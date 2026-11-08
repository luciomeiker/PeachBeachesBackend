from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from .filters import ProductoFilter
from .models import Categoria, Producto
from .permissions import EsAdminOSoloLectura
from .serializers import CategoriaSerializer, ProductoSerializer


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all().order_by('nombre')
    serializer_class = CategoriaSerializer
    permission_classes = [EsAdminOSoloLectura]


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.select_related('categoria').order_by('id')
    serializer_class = ProductoSerializer
    permission_classes = [EsAdminOSoloLectura]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductoFilter           # categoria, precio_min, precio_max
    search_fields = ['nombre', 'marca']        # ?search=sombrilla
    ordering_fields = ['precio', 'nombre', 'stock']  # ?ordering=-precio
