from django.urls import path

from .views import AgregarItemView, CarritoView, ItemCarritoDetalleView

urlpatterns = [
    path('', CarritoView.as_view(), name='carrito'),
    path('items/', AgregarItemView.as_view(), name='carrito-agregar'),
    path('items/<int:pk>/', ItemCarritoDetalleView.as_view(), name='carrito-item'),
]
