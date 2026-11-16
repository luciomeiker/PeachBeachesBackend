from rest_framework import serializers
from .models import Mensaje

class MensajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mensaje
        fields = ['id', 'nombre', 'correo', 'mensaje', 'creado_en']
        read_only_fields = ['id', 'creado_en']

    def validate_mensaje(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("El mensaje debe contener al menos 10 caracteres.")
        return value