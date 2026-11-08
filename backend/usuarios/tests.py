from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

CLAVE = 'Clave-Segura-2026'


class AutenticacionTests(APITestCase):
    url_registro = '/api/auth/register/'
    url_login = '/api/auth/login/'

    def datos(self, **cambios):
        datos = {
            'username': 'maria',
            'email': 'maria@example.com',
            'password': CLAVE,
            'first_name': 'María',
            'last_name': 'Pérez',
        }
        datos.update(cambios)
        return datos

    def test_registro_exitoso_guarda_contrasena_hasheada(self):
        respuesta = self.client.post(self.url_registro, self.datos(), format='json')
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('password', respuesta.data)
        usuario = User.objects.get(username='maria')
        self.assertNotEqual(usuario.password, CLAVE)   # no queda en texto plano
        self.assertIn('$', usuario.password)           # formato "algoritmo$iteraciones$sal$hash"
        self.assertTrue(usuario.check_password(CLAVE))

    def test_registro_rechaza_email_duplicado(self):
        User.objects.create_user('otro', 'maria@example.com', CLAVE)
        respuesta = self.client.post(self.url_registro, self.datos(email='MARIA@example.com'), format='json')
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', respuesta.data['errores'])

    def test_registro_rechaza_contrasenas_debiles(self):
        for clave in ('12345678', 'corta', 'password'):
            respuesta = self.client.post(self.url_registro, self.datos(password=clave), format='json')
            self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST, clave)
            self.assertIn('password', respuesta.data['errores'])
        self.assertFalse(User.objects.filter(username='maria').exists())

    def test_login_devuelve_access_y_refresh(self):
        User.objects.create_user('maria', 'maria@example.com', CLAVE)
        respuesta = self.client.post(self.url_login, {'username': 'maria', 'password': CLAVE}, format='json')
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertIn('access', respuesta.data)
        self.assertIn('refresh', respuesta.data)

    def test_login_con_credenciales_incorrectas_da_401(self):
        User.objects.create_user('maria', 'maria@example.com', CLAVE)
        respuesta = self.client.post(self.url_login, {'username': 'maria', 'password': 'incorrecta'}, format='json')
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(respuesta.data['status'], 401)
        self.assertIn('mensaje', respuesta.data)

    def test_token_permite_acceder_a_endpoint_protegido(self):
        User.objects.create_user('maria', 'maria@example.com', CLAVE)
        tokens = self.client.post(self.url_login, {'username': 'maria', 'password': CLAVE}, format='json').data
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        self.assertEqual(self.client.get('/api/carrito/').status_code, status.HTTP_200_OK)
