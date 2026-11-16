from decimal import Decimal

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from productos.models import Categoria, Producto

from .models import Carrito, ItemCarrito


class CarritoTests(APITestCase):
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

    def agregar(self, producto, cantidad):
        return self.client.post(
            '/api/carrito/items/', {'producto': producto.id, 'cantidad': cantidad}, format='json'
        )

    def test_carrito_requiere_autenticacion(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get('/api/carrito/').status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            self.client.post('/api/carrito/items/', {'producto': self.sombrilla.id}, format='json').status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_carrito_nuevo_esta_vacio(self):
        respuesta = self.client.get('/api/carrito/')
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data['items'], [])
        self.assertEqual(Decimal(respuesta.data['total']), Decimal('0.00'))

    def test_agregar_producto_devuelve_subtotal_y_total(self):
        self.agregar(self.sombrilla, 2)
        respuesta = self.agregar(self.reposera, 1)
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(respuesta.data['items']), 2)
        subtotales = {i['producto']['nombre']: Decimal(i['subtotal']) for i in respuesta.data['items']}
        self.assertEqual(subtotales['Sombrilla'], Decimal('2000.00'))
        self.assertEqual(subtotales['Reposera'], Decimal('2500.50'))
        self.assertEqual(Decimal(respuesta.data['total']), Decimal('4500.50'))

    def test_agregar_el_mismo_producto_suma_la_cantidad(self):
        self.agregar(self.sombrilla, 2)
        respuesta = self.agregar(self.sombrilla, 1)
        self.assertEqual(len(respuesta.data['items']), 1)
        self.assertEqual(respuesta.data['items'][0]['cantidad'], 3)

    def test_no_se_puede_superar_el_stock(self):
        respuesta = self.agregar(self.sombrilla, 6)  # stock = 5
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cantidad', respuesta.data['errores'])
        self.agregar(self.sombrilla, 4)
        respuesta = self.agregar(self.sombrilla, 2)  # 4 + 2 > 5
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ItemCarrito.objects.get().cantidad, 4)

    def test_actualizar_cantidad(self):
        item_id = self.agregar(self.sombrilla, 1).data['items'][0]['id']
        respuesta = self.client.patch(f'/api/carrito/items/{item_id}/', {'cantidad': 4}, format='json')
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(respuesta.data['total']), Decimal('4000.00'))
        respuesta = self.client.patch(f'/api/carrito/items/{item_id}/', {'cantidad': 9}, format='json')
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_eliminar_item_y_vaciar_carrito(self):
        self.agregar(self.sombrilla, 1)
        item_id = self.agregar(self.reposera, 1).data['items'][1]['id']
        respuesta = self.client.delete(f'/api/carrito/items/{item_id}/')
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(respuesta.data['items']), 1)
        respuesta = self.client.delete('/api/carrito/')
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data['items'], [])
        self.assertEqual(ItemCarrito.objects.count(), 0)

    def test_no_se_puede_tocar_el_item_de_otro_usuario(self):
        item_id = self.agregar(self.sombrilla, 1).data['items'][0]['id']
        self.client.force_authenticate(self.otro)
        respuesta = self.client.delete(f'/api/carrito/items/{item_id}/')
        self.assertEqual(respuesta.status_code, status.HTTP_404_NOT_FOUND)
        respuesta = self.client.patch(f'/api/carrito/items/{item_id}/', {'cantidad': 2}, format='json')
        self.assertEqual(respuesta.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(ItemCarrito.objects.count(), 1)
        self.assertEqual(Carrito.objects.get(usuario=self.usuario).items.count(), 1)
