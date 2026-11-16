from rest_framework import serializers

from .models import ItemPedido, Pedido


class ItemPedidoSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = ItemPedido
        fields = ('id', 'producto', 'nombre_producto', 'precio_unitario', 'cantidad', 'subtotal')


class PedidoSerializer(serializers.ModelSerializer):
    items = ItemPedidoSerializer(many=True, read_only=True)

    class Meta:
        model = Pedido
        fields = ('id', 'estado', 'total', 'creado', 'items')
