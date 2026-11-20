from django.urls import path

from .views import MensajeCreateView

urlpatterns = [
    path('', MensajeCreateView.as_view(), name='contacto'),
]
