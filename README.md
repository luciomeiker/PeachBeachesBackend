# PeachBeachesBackend

Backend del ecommerce **Peach Beaches** (Django + Django REST Framework + PostgreSQL).
Integrantes: Maximo Libasci, Misael Poblete y Lucio Trafian.

## Puesta en marcha (local)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1          # Linux/Mac: source venv/bin/activate
cd backend
pip install -r requirements.txt
copy .env.example .env               # Linux/Mac: cp .env.example .env  (y completar tus valores)
```

1. Crear el usuario y la base en PostgreSQL (una sola vez, desde `psql` como `postgres`):
   ```sql
   CREATE USER peachbeaches WITH PASSWORD 'tu_clave_local' CREATEDB;
   CREATE DATABASE peachbeach OWNER peachbeaches;
   ```
   `CREATEDB` hace falta para que `manage.py test` pueda crear la base de pruebas.
2. Completar `backend/.env` con esos mismos datos (el `.env` **no se sube a Git**).
3. Crear tablas y cargar datos de ejemplo:
   ```powershell
   python manage.py migrate
   python manage.py cargar_productos      # 12 productos y 4 categorías de ejemplo
   python manage.py createsuperuser       # para entrar a /admin/
   python manage.py runserver
   ```

## Tests

```powershell
python manage.py test
```

## Endpoints

| Método | Ruta | Descripción | Requiere login |
|---|---|---|---|
| POST | `/api/auth/register/` | Registro de usuario | No |
| POST | `/api/auth/login/` | Login: devuelve `access` y `refresh` | No |
| POST | `/api/auth/login/refresh/` | Renueva el `access` | No |
| GET | `/api/productos/` | Lista paginada. Filtros: `categoria`, `precio_min`, `precio_max`, `search`, `ordering` | No |
| GET | `/api/productos/<id>/` | Detalle de un producto | No |
| POST / PUT / PATCH / DELETE | `/api/productos/`, `/api/productos/<id>/` | Crear, editar, eliminar | Solo admin |
| GET | `/api/categorias/` y `/api/categorias/<id>/` | Categorías (escritura solo admin) | No |
| GET | `/api/carrito/` | Ver el carrito con subtotales y total | Sí |
| DELETE | `/api/carrito/` | Vaciar el carrito | Sí |
| POST | `/api/carrito/items/` | Agregar producto `{producto, cantidad}` | Sí |
| PATCH | `/api/carrito/items/<id>/` | Cambiar cantidad `{cantidad}` | Sí |
| DELETE | `/api/carrito/items/<id>/` | Quitar un ítem | Sí |
| POST | `/api/pedidos/checkout/` | Finalizar compra | Sí |
| GET | `/api/pedidos/` y `/api/pedidos/<id>/` | Historial propio | Sí |
| POST | `/api/contacto/` | Guardar mensaje `{nombre, email, mensaje}` | No |
| GET | `/api/docs/` | Documentación Swagger | No |

Los endpoints protegidos se llaman con el header `Authorization: Bearer <access>`.

Los errores tienen siempre el mismo formato:
```json
{"status": 400, "mensaje": "Los datos enviados no son válidos.", "errores": {"campo": ["detalle"]}}
```

## Decisiones técnicas

- **Contraseñas:** Django las guarda hasheadas con **PBKDF2-SHA256** (cientos de miles de iteraciones y una sal aleatoria por usuario). Un hash no se puede revertir, así que si se filtra la base no se exponen las contraseñas, y nunca se guardan en texto plano.
- **`transaction.atomic()` en el checkout:** crear el pedido, descontar el stock y vaciar el carrito son varios pasos que deben ocurrir todos o ninguno. Si uno falla, se deshacen los demás. Además `select_for_update()` bloquea los productos para que dos compras simultáneas no vendan la misma unidad.
- **Precio histórico:** cada ítem del pedido guarda el precio unitario del momento de la compra.

## Variables de entorno

Ver `backend/.env.example`. En producción se cargan desde el panel del servicio
(`DEBUG=False`, `SECRET_KEY`, `ALLOWED_HOSTS`, datos de la base con `DB_SSLMODE=require`,
`CORS_ALLOWED_ORIGINS` con el dominio del frontend y `CSRF_TRUSTED_ORIGINS` con el del backend).
