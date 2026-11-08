from django.conf import settings
from django.db import models

from productos.models import Producto


class Pedido(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        PAGADO = 'pagado', 'Pagado'
        ENVIADO = 'enviado', 'Enviado'
        CANCELADO = 'cancelado', 'Cancelado'

    # PROTECT: no se puede borrar un usuario que tiene pedidos (se pierde el historial).
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='pedidos'
    )
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.PENDIENTE)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado', '-id']

    def __str__(self):
        return f'Pedido #{self.pk} de {self.usuario} ({self.estado})'


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    # Si más adelante se borra el producto, el pedido conserva nombre y precio.
    producto = models.ForeignKey(
        Producto, null=True, blank=True, on_delete=models.SET_NULL, related_name='items_pedido'
    )
    nombre_producto = models.CharField(max_length=200)
    # Precio al momento de la compra: no cambia si el producto cambia de precio.
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.PositiveIntegerField()

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.cantidad} x {self.nombre_producto}'

    @property
    def subtotal(self):
        return self.precio_unitario * self.cantidad
