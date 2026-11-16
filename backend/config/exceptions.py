from rest_framework.views import exception_handler


def manejador_errores(exc, context):
    """
    Deja todos los errores de la API con el mismo formato:

        {"status": 400, "mensaje": "texto claro", "errores": {...} o null}

    Los errores no controlados (500) los sigue manejando Django.
    """
    response = exception_handler(exc, context)
    if response is None:
        return None

    data = response.data
    if isinstance(data, dict) and 'detail' in data:
        mensaje = str(data['detail'])
        errores = {k: v for k, v in data.items() if k != 'detail'} or None
    elif response.status_code == 400:
        mensaje = 'Los datos enviados no son válidos.'
        errores = data
    else:
        mensaje = str(data)
        errores = None

    response.data = {
        'status': response.status_code,
        'mensaje': mensaje,
        'errores': errores,
    }
    return response
