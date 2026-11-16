<<<<<<< HEAD
path('contacto/', MensajeCreateView.as_view(), name='contacto-create'),
=======
from django.urls import path

from .views import MensajeCreateView

urlpatterns = [
    path('', MensajeCreateView.as_view(), name='contacto'),
]
>>>>>>> 203f5b15f623e7978912f665dbd8f9d47779e807
