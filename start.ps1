# 🚀 Script de Inicio Rápido - Backend Django
# Ejecuta este script para iniciar el backend rápidamente

Write-Host "🚀 Iniciando Backend del Sistema Boutique..." -ForegroundColor Green
Write-Host ""

# Verificar si estamos en el directorio correcto
if (-Not (Test-Path "manage.py")) {
    Write-Host "❌ Error: Este script debe ejecutarse desde la carpeta 'sistema_boutique'" -ForegroundColor Red
    Write-Host "   Usa: cd sistema_boutique" -ForegroundColor Yellow
    exit 1
}

# Activar entorno virtual
Write-Host "📦 Activando entorno virtual..." -ForegroundColor Cyan
if (Test-Path ".\env\Scripts\Activate.ps1") {
    & .\env\Scripts\Activate.ps1
} else {
    Write-Host "❌ No se encontró el entorno virtual en .\env\" -ForegroundColor Red
    Write-Host "   Crea uno con: python -m venv env" -ForegroundColor Yellow
    exit 1
}

# Verificar si existen las dependencias
Write-Host "🔍 Verificando dependencias..." -ForegroundColor Cyan
pip list | Select-String "Django" | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "📥 Instalando dependencias..." -ForegroundColor Cyan
    pip install -r requirements.txt
}

# Aplicar migraciones
Write-Host "🗄️  Aplicando migraciones de base de datos..." -ForegroundColor Cyan
python manage.py makemigrations
python manage.py migrate

Write-Host ""
Write-Host "✅ ¡Configuración completa!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Iniciando servidor en http://localhost:8000 ..." -ForegroundColor Green
Write-Host "   Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
Write-Host ""

# Iniciar servidor
python manage.py runserver
