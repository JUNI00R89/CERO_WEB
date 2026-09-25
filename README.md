# Cero

Plataforma de gestión de finanzas personales con API REST documentada y frontend integrado.

## Descripción

Cero permite a los usuarios administrar cuentas, categorías, movimientos, presupuestos y metas de ahorro de forma segura. Incluye autenticación JWT, control de permisos por rol (admin/usuario) y protección de propiedad de datos.

## Tecnologías

### Backend
- **Python** — lenguaje principal
- **FastAPI** — framework web async
- **SQLAlchemy 2.0** — ORM y manejo de base de datos
- **Pydantic** — validación y serialización de datos
- **PyJWT + bcrypt** — autenticación JWT y hash de contraseñas
- **Uvicorn** — servidor ASGI
- **SQLite / PostgreSQL** — base de datos

### Frontend
- **React** (Vite) — interfaz SPA
- **Axios** — cliente HTTP
- **React Router** — rutas y navegación

## Estructura

```
CERO/
├── backend/
│   ├── main.py              ← Punto de entrada y configuración
│   ├── config.py            ← Variables de entorno centralizadas
│   ├── database.py          ← Conexión y get_db()
│   ├── roles.py             ← Constantes de roles
│   ├── models/              ← Modelos SQLAlchemy
│   ├── schemas/             ← Schemas Pydantic (Create/Update/Out)
│   ├── routers/             ← Endpoints HTTP
│   ├── controllers/         ← Lógica CRUD
│   ├── services/            ← Servicios reutilizables (JWT, passwords)
│   ├── dependencies/        ← Autenticación y permisos
│   ├── exceptions/          ← Excepciones propias del dominio
│   ├── handlers/            ← Handlers globales de errores
│   ├── test_parte7.py       ← Pruebas automatizadas
│   ├── requirements.txt     ← Dependencias Python
│   ├── .env.example         ← Plantilla de variables de entorno
│   └── .gitignore
├── frontend/
│   ├── src/                 ← Código React
│   ├── dist/                ← Build de producción (servido por FastAPI)
│   ├── package.json         ← Dependencias Node
│   └── vite.config.js
└── README.md
```

## Requisitos

- Python 3.10+
- Node.js 18+ (solo para reconstruir el frontend)

## Instalación

```bash
cd backend
pip install -r requirements.txt
```

## Configuración

Copia `.env.example` a `.env` y completa las credenciales:

```bash
# SQLite (desarrollo)
DATABASE_URL=sqlite:///./cero.db

# PostgreSQL (producción)
# DATABASE_URL=postgresql+psycopg://usuario:contrasena@localhost:5432/cero

SECRET_KEY=tu-clave-secreta-larga-aqui
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Ejecución

```bash
cd backend
python -m uvicorn main:app --reload
```

- **API + Frontend:** http://localhost:8000
- **Swagger (docs):** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health check:** http://localhost:8000/health

> Si ejecutas solo el backend sin frontend compilado, la API funciona normalmente desde `/docs`.

## Recursos de la API

| Recurso | Endpoint | Descripción |
|---|---|---|
| Autenticación | `POST /login` | Inicio de sesión, devuelve JWT |
| Usuarios | `GET/POST/PUT/DELETE /usuarios` | CRUD de usuarios |
| Usuarios (me) | `GET /usuarios/me` | Perfil del usuario autenticado |
| Cuentas | `GET/POST/PUT/DELETE /cuentas` | CRUD de cuentas financieras |
| Categorías | `GET/POST/PUT/DELETE /categorias` | CRUD de categorías |
| Movimientos | `GET/POST/PUT/DELETE /movimientos` | CRUD de movimientos |
| Presupuestos | `GET/POST/PUT/DELETE /presupuestos` | CRUD de presupuestos |
| Metas de ahorro | `GET/POST/PUT/DELETE /metas-ahorro` | CRUD de metas de ahorro |

Todos los endpoints de listado admiten filtros, ordenamiento y paginación.

## Autenticación

1. `POST /login` con `{"correo": "...", "password": "..."}`
2. Se recibe un `access_token` (JWT, expira en 30 min por defecto)
3. Enviar el header `Authorization: Bearer <token>` en las peticiones autenticadas

## Roles

- **admin** — acceso total a todos los recursos y gestión de usuarios
- **usuario** — solo accede a sus propios datos

El rol está contenido en el JWT y se valida en cada petición protegida.

## Pruebas

```bash
cd backend
python test_parte7.py
```

Incluye 34 pruebas automatizadas que verifican:
- Login y validación de JWT
- Permisos por rol (admin/usuario)
- Aislamiento de datos entre usuarios
- Protección de propiedad de recursos
- Respuestas de error consistentes

## Seguridad

- Las contraseñas se almacenan hasheadas con bcrypt
- Las variables sensibles (`SECRET_KEY`, credenciales de BD) están en `.env` (nunca en el código)
- `.env` está excluido en `.gitignore`
- Los errores internos nunca exponen trazas (tracebacks)
- Las rutas privadas rechazan accesos sin token válido
