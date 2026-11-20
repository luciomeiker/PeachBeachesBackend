from decimal import Decimal

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from productos.models import Producto
    
from productos.models import Producto


class Carrito(models.Model):
    """Cada usuario autenticado tiene un único carrito."""

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carrito'
    )
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Carrito de {self.usuario}'

    @property
    def total(self):
        return sum((item.subtotal for item in self.items.all()), Decimal('0.00'))


class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

<<<<<<< HEAD
    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"


class Pedido(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('enviado', 'Enviado'),
        ('cancelado', 'Cancelado'),
    )
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.username}"

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2) # e.i) Precio al momento de la compra
=======
    class Meta:
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=['carrito', 'producto'], name='unico_producto_por_carrito'
            ),
        ]

    def __str__(self):
        return f'{self.cantidad} x {self.producto}'

    @property
    def subtotal(self):
        return self.producto.precio * self.cantidad
>>>>>>> 203f5b15f623e7978912f665dbd8f9d47779e807
