from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management import call_command
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Categoria, Producto


class ProductoTests(APITestCase):
    def setUp(self):
        self.playa = Categoria.objects.create(nombre='Playa')
        self.ropa = Categoria.objects.create(nombre='Ropa')
        self.sombrilla = self.crear('Sombrilla', 'SolMar', '18000.00', 10, self.playa)
        self.reposera = self.crear('Reposera', 'Costa', '30000.00', 5, self.playa)
        self.malla = self.crear('Malla entera', 'Oleaje', '20000.00', 8, self.ropa)
        self.admin = User.objects.create_user('admin', 'admin@example.com', 'Clave-Admin-2026', is_staff=True)
        self.comun = User.objects.create_user('comun', 'comun@example.com', 'Clave-Comun-2026')

    def crear(self, nombre, marca, precio, stock, categoria):
        return Producto.objects.create(
            nombre=nombre, descripcion=f'{nombre} de prueba', marca=marca,
            precio=Decimal(precio), stock=stock, categoria=categoria,
        )

    def nombres(self, respuesta):
        return [p['nombre'] for p in respuesta.data['results']]

    def datos_nuevo(self):
        return {
            'nombre': 'Gorra', 'descripcion': 'Gorra de algodón', 'marca': 'Costa',
            'precio': '7500.00', 'stock': 20, 'categoria': self.ropa.id,
        }

    def test_listado_es_publico_y_paginado(self):
        respuesta = self.client.get('/api/productos/')
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data['count'], 3)
        self.assertIn('results', respuesta.data)

    def test_detalle_es_publico(self):
        respuesta = self.client.get(f'/api/productos/{self.sombrilla.id}/')
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data['categoria_nombre'], 'Playa')

    def test_filtro_por_categoria(self):
        respuesta = self.client.get('/api/productos/', {'categoria': self.ropa.id})
        self.assertEqual(self.nombres(respuesta), ['Malla entera'])

    def test_filtro_por_rango_de_precio(self):
        respuesta = self.client.get('/api/productos/', {'precio_min': '19000', 'precio_max': '25000'})
        self.assertEqual(self.nombres(respuesta), ['Malla entera'])

    def test_busqueda_por_nombre(self):
        respuesta = self.client.get('/api/productos/', {'search': 'repos'})
        self.assertEqual(self.nombres(respuesta), ['Reposera'])

    def test_ordenamiento_por_precio(self):
        respuesta = self.client.get('/api/productos/', {'ordering': '-precio'})
        self.assertEqual(self.nombres(respuesta), ['Reposera', 'Malla entera', 'Sombrilla'])

    def test_crear_producto_sin_login_da_401(self):
        respuesta = self.client.post('/api/productos/', self.datos_nuevo(), format='json')
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_usuario_comun_no_puede_crear_ni_borrar(self):
        self.client.force_authenticate(self.comun)
        respuesta = self.client.post('/api/productos/', self.datos_nuevo(), format='json')
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)
        respuesta = self.client.delete(f'/api/productos/{self.sombrilla.id}/')
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Producto.objects.filter(id=self.sombrilla.id).exists())

    def test_admin_puede_crear_editar_y_eliminar(self):
        self.client.force_authenticate(self.admin)
        respuesta = self.client.post('/api/productos/', self.datos_nuevo(), format='json')
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        id_nuevo = respuesta.data['id']
        respuesta = self.client.patch(f'/api/productos/{id_nuevo}/', {'stock': 99}, format='json')
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(Producto.objects.get(id=id_nuevo).stock, 99)
        respuesta = self.client.delete(f'/api/productos/{id_nuevo}/')
        self.assertEqual(respuesta.status_code, status.HTTP_204_NO_CONTENT)

    def test_no_acepta_precio_cero_ni_stock_negativo(self):
        self.client.force_authenticate(self.admin)
        datos = self.datos_nuevo()
        datos.update(precio='0', stock=-1)
        respuesta = self.client.post('/api/productos/', datos, format='json')
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('precio', respuesta.data['errores'])
        self.assertIn('stock', respuesta.data['errores'])

    def test_comando_cargar_productos_carga_al_menos_10_sin_duplicar(self):
        Producto.objects.all().delete()
        call_command('cargar_productos', verbosity=0)
        cantidad = Producto.objects.count()
        self.assertGreaterEqual(cantidad, 10)
        call_command('cargar_productos', verbosity=0)
        self.assertEqual(Producto.objects.count(), cantidad)
