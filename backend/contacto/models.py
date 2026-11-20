from django.db import models


class Mensaje(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    mensaje = models.TextField()
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado']
        verbose_name_plural = 'mensajes'

    def __str__(self):
        return f'{self.nombre} <{self.email}>'
