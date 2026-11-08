from rest_framework.permissions import SAFE_METHODS, BasePermission


class EsAdminOSoloLectura(BasePermission):
    """
    Cualquiera puede listar y ver el detalle (GET, HEAD, OPTIONS).
    Crear, editar y eliminar queda reservado a administradores (is_staff).
    """

    message = 'Solo un administrador puede realizar esta acción.'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)
