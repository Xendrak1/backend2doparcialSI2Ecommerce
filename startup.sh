#!/bin/bash
# Script de inicio para Azure App Service

# Aplicar migraciones
python manage.py migrate --noinput

# Recopilar archivos estáticos (si los hay)
python manage.py collectstatic --noinput || true

# Iniciar Gunicorn
# Azure usa la variable PORT automáticamente
gunicorn sistema_boutique.wsgi --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120

