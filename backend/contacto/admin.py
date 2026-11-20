from django.contrib import admin

from .models import Mensaje


@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'creado')
    search_fields = ('nombre', 'email', 'mensaje')
    list_filter = ('creado',)
    readonly_fields = ('creado',)
