from django.shortcuts import render

class HistorialPedidosView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PedidoSerializer  # 👈 Acá lo vinculamos
    
    def get_queryset(self):
        # e.iii) Un usuario solo puede ver sus propios pedidos y nadie más
        return Pedido.objects.filter(usuario=self.request.user)