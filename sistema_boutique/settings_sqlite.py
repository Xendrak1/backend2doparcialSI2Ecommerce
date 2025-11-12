# Configuración alternativa con SQLite (más simple para desarrollo)

# Copia esto y reemplaza la sección DATABASES en settings.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


