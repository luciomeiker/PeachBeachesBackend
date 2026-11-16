from django.contrib import admin

from .models import ItemPedido, Pedido


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ('subtotal',)


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'estado', 'total', 'creado')
    list_filter = ('estado', 'creado')
    search_fields = ('usuario__username', 'usuario__email')
    inlines = [ItemPedidoInline]
