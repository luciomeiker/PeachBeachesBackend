
"""
Rutas principales del proyecto.
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Usuarios
    path('api/auth/', include('usuarios.urls')),

    # Productos y categorías
    path('api/', include('productos.urls')),

    # Carrito
    path('api/carrito/', include('carrito.urls')),

    # Pedidos
    path('api/pedidos/', include('pedidos.urls')),

    # Contacto
    path('api/contacto/', include('contacto.urls')),

    # Documentación
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
