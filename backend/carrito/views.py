from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Carrito
from .serializers import CarritoSerializer

class CarritoViewSet(viewsets.ModelViewSet):
    queryset = Carrito.objects.all()
    serializer_class = CarritoSerializer
    
    # 👇 AQUÍ ES DONDE VA LA CONFIGURACIÓN DEL PASO 4
    permission_classes = [IsAuthenticated]

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