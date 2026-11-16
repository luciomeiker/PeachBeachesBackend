from rest_framework import serializers
from .models import Carrito, ItemCarrito

class ItemCarritoSerializer(serializers.ModelSerializer):
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = ItemCarrito
        fields = ['id', 'producto', 'cantidad', 'subtotal']

    def get_subtotal(self, obj):
        return obj.cantidad * obj.producto.precio

    def validate(self, data):
        # d.iii) Validar que la cantidad solicitada no supere el stock disponible
        producto = data['producto']
        cantidad = data['cantidad']
        if cantidad > producto.stock:
            raise serializers.ValidationError(f"Stock insuficiente. Stock disponible: {producto.stock}")
        return data

class CarritoSerializer(serializers.ModelSerializer):
    items = ItemCarritoSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Carrito
        fields = ['id', 'usuario', 'items', 'total']

    def get_total(self, obj):
        return sum(item.cantidad * item.producto.precio for item in obj.items.all())