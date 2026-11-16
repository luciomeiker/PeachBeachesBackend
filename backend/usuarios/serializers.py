from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    # write_only: la contraseña se recibe pero nunca se devuelve en la respuesta.
    password = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'first_name', 'last_name')
        read_only_fields = ('id',)

    def validate_email(self, value):
        # El correo debe ser único (sin distinguir mayúsculas de minúsculas).
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Este correo electrónico ya está registrado.')
        return value

    def validate(self, attrs):
        # Aplica los AUTH_PASSWORD_VALIDATORS de settings.py (largo mínimo,
        # contraseña común, solo números, parecida al usuario/correo).
        usuario = User(
            username=attrs.get('username', ''),
            email=attrs.get('email', ''),
            first_name=attrs.get('first_name', ''),
            last_name=attrs.get('last_name', ''),
        )
        try:
            validate_password(attrs['password'], user=usuario)
        except DjangoValidationError as error:
            raise serializers.ValidationError({'password': list(error.messages)})
        return attrs

    def create(self, validated_data):
        # create_user hashea la contraseña (PBKDF2-SHA256 por defecto en Django);
        # nunca se guarda en texto plano.
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password'],
        )
