from rest_framework import serializers

from productos.models import Producto

from .models import Carrito, ItemCarrito


class ProductoResumenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ('id', 'nombre', 'marca', 'precio', 'imagen', 'stock')


class ItemCarritoSerializer(serializers.ModelSerializer):
    producto = ProductoResumenSerializer(read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = ItemCarrito
        fields = ('id', 'producto', 'cantidad', 'subtotal')


class CarritoSerializer(serializers.ModelSerializer):
    items = ItemCarritoSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = Carrito
        fields = ('id', 'items', 'total')


class AgregarItemSerializer(serializers.Serializer):
    producto = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all())
    cantidad = serializers.IntegerField(min_value=1, default=1)


class ActualizarItemSerializer(serializers.Serializer):
    cantidad = serializers.IntegerField(min_value=1)
