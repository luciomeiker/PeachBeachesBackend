import django_filters

from .models import Producto


class ProductoFilter(django_filters.FilterSet):
    # /api/productos/?precio_min=1000&precio_max=5000&categoria=2
    precio_min = django_filters.NumberFilter(field_name='precio', lookup_expr='gte')
    precio_max = django_filters.NumberFilter(field_name='precio', lookup_expr='lte')

    class Meta:
        model = Producto
        fields = ['categoria']
