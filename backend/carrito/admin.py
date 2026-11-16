from django.contrib import admin

from .models import Carrito, ItemCarrito


class ItemCarritoInline(admin.TabularInline):
    model = ItemCarrito
    extra = 0


@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'actualizado')
    search_fields = ('usuario__username', 'usuario__email')
    inlines = [ItemCarritoInline]
