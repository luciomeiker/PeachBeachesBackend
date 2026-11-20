from rest_framework import status
from rest_framework.test import APITestCase

from .models import Mensaje


class ContactoTests(APITestCase):
    url = '/api/contacto/'

    def datos(self, **cambios):
        datos = {'nombre': 'Lucía', 'email': 'lucia@example.com', 'mensaje': 'Hola, quisiera más información.'}
        datos.update(cambios)
        return datos

    def test_guarda_el_mensaje_sin_necesidad_de_login(self):
        respuesta = self.client.post(self.url, self.datos(), format='json')
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Mensaje.objects.count(), 1)
        self.assertEqual(Mensaje.objects.get().email, 'lucia@example.com')

    def test_rechaza_datos_invalidos(self):
        casos = {
            'email': self.datos(email='no-es-un-email'),
            'nombre': self.datos(nombre=' '),
            'mensaje': self.datos(mensaje='corto'),
        }
        for campo, datos in casos.items():
            respuesta = self.client.post(self.url, datos, format='json')
            self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST, campo)
            self.assertIn(campo, respuesta.data['errores'])
        self.assertEqual(Mensaje.objects.count(), 0)

    def test_solo_acepta_post(self):
        self.assertEqual(self.client.get(self.url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
