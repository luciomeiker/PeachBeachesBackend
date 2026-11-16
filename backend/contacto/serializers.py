from rest_framework import serializers

from .models import Mensaje


class MensajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mensaje
        fields = ('id', 'nombre', 'email', 'mensaje', 'creado')
        read_only_fields = ('id', 'creado')

    def validate_nombre(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError('El nombre debe tener al menos 2 caracteres.')
        return value

    def validate_mensaje(self, value):
        value = value.strip()
        if len(value) < 10:
            raise serializers.ValidationError('El mensaje debe tener al menos 10 caracteres.')
        return value
