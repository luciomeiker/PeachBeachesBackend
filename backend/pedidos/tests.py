from decimal import Decimal

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from carrito.models import Carrito, ItemCarrito
from productos.models import Categoria, Producto

from .models import ItemPedido, Pedido


class PedidoTests(APITestCase):
    def setUp(self):
        categoria = Categoria.objects.create(nombre='Playa')
        self.sombrilla = Producto.objects.create(
            nombre='Sombrilla', descripcion='d', marca='SolMar',
            precio=Decimal('1000.00'), stock=5, categoria=categoria,
        )
        self.reposera = Producto.objects.create(
            nombre='Reposera', descripcion='d', marca='Costa',
            precio=Decimal('2500.50'), stock=3, categoria=categoria,
        )
        self.usuario = User.objects.create_user('ana', 'ana@example.com', 'Clave-Ana-2026')
        self.otro = User.objects.create_user('beto', 'beto@example.com', 'Clave-Beto-2026')
        self.client.force_authenticate(self.usuario)

    def llenar_carrito(self, usuario=None):
        carrito, _ = Carrito.objects.get_or_create(usuario=usuario or self.usuario)
        ItemCarrito.objects.create(carrito=carrito, producto=self.sombrilla, cantidad=2)
        ItemCarrito.objects.create(carrito=carrito, producto=self.reposera, cantidad=1)
        return carrito

    def comprar(self):
        return self.client.post('/api/pedidos/checkout/')

    def test_finalizar_compra_crea_pedido_descuenta_stock_y_vacia_carrito(self):
        carrito = self.llenar_carrito()
        respuesta = self.comprar()
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(respuesta.data['estado'], 'pendiente')
        self.assertEqual(Decimal(respuesta.data['total']), Decimal('4500.50'))
        self.assertEqual(len(respuesta.data['items']), 2)

        self.sombrilla.refresh_from_db()
        self.reposera.refresh_from_db()
        self.assertEqual(self.sombrilla.stock, 3)
        self.assertEqual(self.reposera.stock, 2)
        self.assertEqual(carrito.items.count(), 0)
        self.assertEqual(Pedido.objects.filter(usuario=self.usuario).count(), 1)

    def test_finalizar_compra_con_carrito_vacio_da_400(self):
        respuesta = self.comprar()
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Pedido.objects.count(), 0)

    def test_si_falta_stock_no_cambia_nada(self):
        carrito = self.llenar_carrito()
        # Otro cliente se llevó stock después de que se llenó el carrito.
        self.reposera.stock = 0
        self.reposera.save()
        respuesta = self.comprar()
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('stock', respuesta.data['errores'])
        self.sombrilla.refresh_from_db()
        self.assertEqual(self.sombrilla.stock, 5)         # no se descontó nada
        self.assertEqual(carrito.items.count(), 2)        # el carrito sigue intacto
        self.assertEqual(Pedido.objects.count(), 0)
        self.assertEqual(ItemPedido.objects.count(), 0)

    def test_el_pedido_guarda_el_precio_del_momento_de_la_compra(self):
        self.llenar_carrito()
        pedido_id = self.comprar().data['id']
        self.sombrilla.precio = Decimal('9999.00')
        self.sombrilla.save()
        respuesta = self.client.get(f'/api/pedidos/{pedido_id}/')
        precios = {i['nombre_producto']: Decimal(i['precio_unitario']) for i in respuesta.data['items']}
        self.assertEqual(precios['Sombrilla'], Decimal('1000.00'))
        self.assertEqual(Decimal(respuesta.data['total']), Decimal('4500.50'))

    def test_checkout_requiere_autenticacion(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.comprar().status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.get('/api/pedidos/').status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cada_usuario_ve_solo_sus_pedidos(self):
        self.llenar_carrito()
        pedido_de_ana = self.comprar().data['id']

        self.client.force_authenticate(self.otro)
        listado = self.client.get('/api/pedidos/')
        self.assertEqual(listado.status_code, status.HTTP_200_OK)
        self.assertEqual(listado.data['count'], 0)
        detalle = self.client.get(f'/api/pedidos/{pedido_de_ana}/')
        self.assertEqual(detalle.status_code, status.HTTP_404_NOT_FOUND)

        self.client.force_authenticate(self.usuario)
        listado = self.client.get('/api/pedidos/')
        self.assertEqual(listado.data['count'], 1)
