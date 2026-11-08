from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Carrito, ItemCarrito
from .serializers import (
    ActualizarItemSerializer,
    AgregarItemSerializer,
    CarritoSerializer,
)


def obtener_carrito(usuario):
    carrito, _ = Carrito.objects.get_or_create(usuario=usuario)
    return carrito


def respuesta_carrito(carrito, codigo=status.HTTP_200_OK):
    """Devuelve el carrito actualizado con subtotales por ítem y total general."""
    carrito = Carrito.objects.prefetch_related('items__producto').get(pk=carrito.pk)
    return Response(CarritoSerializer(carrito).data, status=codigo)


def validar_stock(producto, cantidad_total):
    """La cantidad pedida no puede superar el stock disponible."""
    if producto.stock <= 0:
        raise serializers.ValidationError({'cantidad': f'"{producto.nombre}" no tiene stock disponible.'})
    if cantidad_total > producto.stock:
        raise serializers.ValidationError({
            'cantidad': f'Solo hay {producto.stock} unidades disponibles de "{producto.nombre}".'
        })


class CarritoView(APIView):
    """GET: ver el carrito. DELETE: vaciarlo."""

    permission_classes = [IsAuthenticated]

    @extend_schema(responses=CarritoSerializer)
    def get(self, request):
        return respuesta_carrito(obtener_carrito(request.user))

    @extend_schema(responses=CarritoSerializer)
    def delete(self, request):
        carrito = obtener_carrito(request.user)
        carrito.items.all().delete()
        return respuesta_carrito(carrito)


class AgregarItemView(APIView):
    """POST: agrega un producto (si ya estaba, suma la cantidad)."""

    permission_classes = [IsAuthenticated]

    @extend_schema(request=AgregarItemSerializer, responses={201: CarritoSerializer})
    def post(self, request):
        serializer = AgregarItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        producto = serializer.validated_data['producto']
        cantidad = serializer.validated_data['cantidad']

        carrito = obtener_carrito(request.user)
        item = ItemCarrito.objects.filter(carrito=carrito, producto=producto).first()
        nueva_cantidad = (item.cantidad if item else 0) + cantidad
        validar_stock(producto, nueva_cantidad)

        if item:
            item.cantidad = nueva_cantidad
            item.save(update_fields=['cantidad'])
        else:
            ItemCarrito.objects.create(carrito=carrito, producto=producto, cantidad=nueva_cantidad)
        return respuesta_carrito(carrito, status.HTTP_201_CREATED)


class ItemCarritoDetalleView(APIView):
    """PATCH/PUT: cambia la cantidad. DELETE: quita el ítem."""

    permission_classes = [IsAuthenticated]

    def get_item(self, request, pk):
        # Solo se buscan ítems del carrito del usuario: los de otros dan 404.
        return get_object_or_404(
            ItemCarrito.objects.select_related('producto', 'carrito'),
            pk=pk,
            carrito__usuario=request.user,
        )

    @extend_schema(request=ActualizarItemSerializer, responses=CarritoSerializer)
    def patch(self, request, pk):
        item = self.get_item(request, pk)
        serializer = ActualizarItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cantidad = serializer.validated_data['cantidad']
        validar_stock(item.producto, cantidad)
        item.cantidad = cantidad
        item.save(update_fields=['cantidad'])
        return respuesta_carrito(item.carrito)

    @extend_schema(request=ActualizarItemSerializer, responses=CarritoSerializer)
    def put(self, request, pk):
        return self.patch(request, pk)

    @extend_schema(responses=CarritoSerializer)
    def delete(self, request, pk):
        item = self.get_item(request, pk)
        carrito = item.carrito
        item.delete()
        return respuesta_carrito(carrito)
