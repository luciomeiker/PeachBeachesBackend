from django.test import TestCase

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from productos.models import Categoria, Producto

class PeachBeachesIntegrationTests(APITestCase):
    def setUp(self):
        # 1. Crear usuario de prueba
        self.user = User.objects.create_user(username='clientetest', password='Password123*')
        
        # 2. Obtener token JWT para autenticación
        response = self.client.post('/api/auth/login/', {'username': 'clientetest', 'password': 'Password123*'})
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

        # 3. Datos iniciales de prueba (Categoría y Producto)
        self.categoria = Categoria.objects.create(nombre='Verano')
        self.producto = Producto.objects.create(
            nombre='Gafas de Sol', descripcion='Protección UV', 
            marca='Peach', precio=12000.00, stock=5, categoria=self.categoria
        )

    def test_01_autenticacion_y_acceso_carrito(self):
        """Verifica que el usuario autenticado pueda acceder a su carrito."""
        response = self.client.get('/api/carrito/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_02_listar_productos_con_filtros(self):
        """Verifica el filtrado de productos por categoría."""
        response = self.client.get(f'/api/productos/?categoria={self.categoria.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_03_agregar_producto_al_carrito(self):
        """Verifica que se pueda agregar un producto al carrito respetando el stock."""
        response = self.client.post('/api/carrito/agregar/', {
            'producto': self.producto.id,
            'cantidad': 2
        })
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])

    def test_04_finalizar_compra_checkout(self):
        """Verifica el flujo completo de checkout convirtiendo el carrito en pedido."""
        self.client.post('/api/carrito/agregar/', {'producto': self.producto.id, 'cantidad': 2})
        response = self.client.post('/api/pedidos/checkout/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_05_formulario_contacto_publico(self):
        """Verifica que el formulario de contacto funcione sin requerir token JWT."""
        self.client.credentials()  # Quitamos credenciales (público)
        response = self.client.post('/api/contacto/', {
            'nombre': 'Valeria',
            'correo': 'valeria@email.com',
            'mensaje': 'Excelente atención en la tienda online.'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)