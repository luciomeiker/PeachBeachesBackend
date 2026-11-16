<<<<<<< HEAD

from django.contrib import admin
from .models import Mensaje

@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'correo', 'creado_en')
    search_fields = ('nombre', 'correo')
=======
from django.contrib import admin

from .models import Mensaje


@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'creado')
    search_fields = ('nombre', 'email', 'mensaje')
    list_filter = ('creado',)
    readonly_fields = ('creado',)
>>>>>>> 203f5b15f623e7978912f665dbd8f9d47779e807
