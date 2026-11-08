"""
Rutas principales del proyecto.

    /admin/            panel de administración de Django
    /api/auth/         registro y login (JWT)
    /api/productos/    productos y /api/categorias/
    /api/carrito/      carrito del usuario autenticado
    /api/pedidos/      historial y finalización de compra
    /api/contacto/     formulario de contacto
    /api/docs/         documentación Swagger (drf-spectacular)
"""
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('usuarios.urls')),
    path('api/', include('productos.urls')),
    path('api/carrito/', include('carrito.urls')),
    path('api/pedidos/', include('pedidos.urls')),
    path('api/contacto/', include('contacto.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
