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

<<<<<<< HEAD
from rest_framework import viewsets, status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from .models import Carrito, ItemCarrito, Pedido, ItemPedido
from .serializers import CarritoSerializer, ItemCarritoSerializer

class CarritoDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
        serializer = CarritoSerializer(carrito)
        return Response(serializer.data)

class AgregarItemCarritoView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ItemCarritoSerializer

    def perform_create(self, serializer):
        carrito, _ = Carrito.objects.get_or_create(usuario=self.request.user)
        producto = serializer.validated_data['producto']
        cantidad = serializer.validated_data['cantidad']
        
        # Validar stock
        if cantidad > producto.stock:
            raise serializers.ValidationError("No hay suficiente stock disponible.")

        # Si el producto ya está en el carrito, actualizar cantidad
        item, created = ItemCarrito.objects.get_or_create(carrito=carrito, producto=producto)
        if not created:
            item.cantidad += cantidad
            if item.cantidad > producto.stock:
                raise serializers.ValidationError("La cantidad total supera el stock disponible.")
            item.save()
        else:
            serializer.save(carrito=carrito)

class FinalizarCompraView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            carrito = Carrito.objects.get(usuario=request.user)
        except Carrito.DoesNotExist:
            return Response({"error": "No tienes un carrito activo."}, status=status.HTTP_400_BAD_REQUEST)

        items = carrito.items.all()
        if not items.exists():
            return Response({"error": "El carrito está vacío."}, status=status.HTTP_400_BAD_REQUEST)

        # e.ii) Operación dentro de una transacción atómica
        try:
            with transaction.atomic():
                total_pedido = 0
                for item in items:
                    if item.cantidad > item.producto.stock:
                        raise ValueError(f"Stock insuficiente para el producto {item.producto.nombre}")
                    total_pedido += item.cantidad * item.producto.precio

                # Crear el pedido
                pedido = Pedido.objects.create(usuario=request.user, total=total_pedido, estado='pendiente')

                # Crear ítems del pedido y descontar stock
                for item in items:
                    ItemPedido.objects.create(
                        pedido=pedido,
                        producto=item.producto,
                        cantidad=item.cantidad,
                        precio_unitario=item.producto.precio
                    )
                    item.producto.stock -= item.cantidad
                    item.producto.save()

                # Vaciar el carrito
                items.delete()

                return Response({"mensaje": "Compra finalizada con éxito", "pedido_id": pedido.id}, status=status.HTTP_201_CREATED)
        
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class HistorialPedidosView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # e.iii) Un usuario solo puede ver sus propios pedidos y nadie más
        return Pedido.objects.filter(usuario=self.request.user)
    
    # Serializador básico para listar pedidos (puedes crearlo en serializers.py)
    # serializer_class = PedidoSerializer
=======
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
>>>>>>> 203f5b15f623e7978912f665dbd8f9d47779e807
