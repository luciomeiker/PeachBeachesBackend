from decimal import Decimal

from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from carrito.models import Carrito, ItemCarrito
from productos.models import Producto

from .models import ItemPedido, Pedido
from .serializers import PedidoSerializer


class PedidoViewSet(viewsets.ReadOnlyModelViewSet):
    """Historial de pedidos del usuario autenticado (solo ve los suyos)."""

    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):  # generación del esquema Swagger
            return Pedido.objects.none()
        return Pedido.objects.filter(usuario=self.request.user).prefetch_related('items')


class FinalizarCompraView(APIView):
    """
    Convierte el carrito en un pedido, descuenta el stock y vacía el carrito.

    Todo ocurre dentro de transaction.atomic(): si algo falla a mitad de camino
    (por ejemplo, no alcanza el stock de un producto) se deshacen TODOS los
    cambios. Sin la transacción podría quedar un pedido creado sin descontar
    stock, o stock descontado sin pedido. Además select_for_update() bloquea
    las filas de los productos para que dos compras simultáneas no vendan la
    misma unidad dos veces.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses={201: PedidoSerializer})
    def post(self, request):
        with transaction.atomic():
            carrito = Carrito.objects.filter(usuario=request.user).first()
            items = []
            if carrito:
                items = list(
                    ItemCarrito.objects.filter(carrito=carrito)
                    .select_related('producto')
                    .order_by('producto_id')
                )
            if not items:
                raise serializers.ValidationError({'carrito': 'El carrito está vacío.'})

            # Bloquea los productos (siempre en el mismo orden para evitar bloqueos cruzados).
            productos = {
                p.id: p
                for p in Producto.objects.select_for_update()
                .filter(id__in=[i.producto_id for i in items])
                .order_by('id')
            }

            # Se revisa el stock real, ya con los productos bloqueados.
            sin_stock = [
                f'"{productos[i.producto_id].nombre}": pediste {i.cantidad} '
                f'y hay {productos[i.producto_id].stock}.'
                for i in items
                if i.cantidad > productos[i.producto_id].stock
            ]
            if sin_stock:
                raise serializers.ValidationError({'stock': sin_stock})

            pedido = Pedido.objects.create(usuario=request.user, total=Decimal('0.00'))
            total = Decimal('0.00')
            for item in items:
                producto = productos[item.producto_id]
                ItemPedido.objects.create(
                    pedido=pedido,
                    producto=producto,
                    nombre_producto=producto.nombre,
                    precio_unitario=producto.precio,  # precio al momento de la compra
                    cantidad=item.cantidad,
                )
                producto.stock -= item.cantidad
                producto.save(update_fields=['stock'])
                total += producto.precio * item.cantidad

            pedido.total = total
            pedido.save(update_fields=['total'])
            carrito.items.all().delete()  # vacía el carrito

        return Response(PedidoSerializer(pedido).data, status=status.HTTP_201_CREATED)
