"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]

from django.urls import path

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rutas de usuarios (auth y registro)
    path('api/auth/', include('usuarios.urls')),
    
    # Rutas de productos y categorías
    path('api/', include('productos.urls')),
    
    # Rutas de carrito y pedidos
    path('api/', include('pedidos.urls')),
    
    # Si habías agregado la de contacto en otra app, la incluís acá también:
    # path('api/', include('contacto.urls')),
]


urlpatterns = [
    # Carrito
    path('carrito/', CarritoDetailView.as_view(), name='carrito-detail'),
    path('carrito/agregar/', AgregarItemCarritoView.as_view(), name='carrito-agregar'),
    
    # Pedidos / Checkout
    path('pedidos/checkout/', FinalizarCompraView.as_view(), name='finalizar-compra'),
    path('pedidos/', HistorialPedidosView.as_view(), name='historial-pedidos'),
]
