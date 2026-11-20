
from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import FinalizarCompraView, PedidoViewSet

router = SimpleRouter()
router.register(r'', PedidoViewSet, basename='pedido')

urlpatterns = [
    # Va antes del router para que "checkout" no se interprete como un ID.
    path('checkout/', FinalizarCompraView.as_view(), name='pedido-checkout'),
    path('', include(router.urls)),
]
