from django.db import models

<<<<<<< HEAD
class Mensaje(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField()
    mensaje = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mensaje de {self.nombre} ({self.correo})"
=======

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
>>>>>>> 203f5b15f623e7978912f665dbd8f9d47779e807
