# Backend - Sistema de Gestión E-commerce

Backend Django REST Framework para el sistema de gestión de e-commerce.

## Tecnologías

- Django 5.2.7
- Django REST Framework 3.16.1
- PostgreSQL (Azure)
- Python 3.10+

## Configuración

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

Copia `.env.example` a `.env` y configura las credenciales de tu base de datos:

```env
PGDATABASE=ecommerce
PGUSER=tu_usuario
PGPASSWORD=tu_contraseña
PGHOST=tu_host.postgres.database.azure.com
PGPORT=5432

SECRET_KEY=tu_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 3. Aplicar migraciones

```bash
python manage.py migrate
```

### 4. Crear superusuario (opcional)

```bash
python manage.py createsuperuser
```

### 5. Ejecutar servidor

```bash
python manage.py runserver
```

## Estructura del Proyecto

```
sistema_boutique/
├── gestion/              # App principal
│   ├── models.py         # Modelos de base de datos
│   ├── serializadores/   # Serializers DRF
│   ├── vistas/           # ViewSets y vistas API
│   └── migrations/       # Migraciones de BD
├── sistema_boutique/     # Configuración Django
│   ├── settings.py       # Configuración principal
│   └── urls.py           # URLs principales
└── manage.py             # Script de gestión Django
```

## API Endpoints

- `/api/auth/` - Autenticación
- `/api/productos/` - Gestión de productos
- `/api/clientes/` - Gestión de clientes
- `/api/ventas/` - Gestión de ventas
- `/api/stocks/` - Gestión de inventario
- `/api/reportes/` - Reportes y exportaciones

## Deployment

Para deployment en Azure, configura las variables de entorno en Azure Portal (App Service Configuration).

**IMPORTANTE**: Nunca subas el archivo `.env` con credenciales reales a Git.

