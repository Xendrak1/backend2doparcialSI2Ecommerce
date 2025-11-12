# Configurar Firebase en Azure para Notificaciones Push

## Paso 1: Obtener las Credenciales de Firebase

1. Ve a [Firebase Console](https://console.firebase.google.com/)
2. Selecciona tu proyecto (o créalo si no existe)
3. Ve a **Configuración del proyecto** (⚙️) > **Cuentas de servicio**
4. Haz clic en **Generar nueva clave privada**
5. Se descargará un archivo JSON (ej: `boutique-firebase-adminsdk-xxxxx.json`)

## Paso 2: Configurar en Azure App Service

### Opción A: Variable de Entorno JSON (Recomendado)

1. Abre el archivo JSON descargado
2. Copia **TODO el contenido** del JSON (desde `{` hasta `}`)
3. En Azure Portal:
   - Ve a tu **App Service** (backend)
   - **Configuración** > **Variables de aplicación**
   - Haz clic en **+ Nueva configuración de aplicación**
   - **Nombre**: `FIREBASE_CREDENTIALS_JSON`
   - **Valor**: Pega el contenido completo del JSON (en una sola línea o con saltos de línea)
   - Haz clic en **Aceptar** y luego **Guardar**

### Opción B: Variable de Entorno con Ruta de Archivo

Si prefieres subir el archivo al servidor:

1. Sube el archivo JSON a tu App Service (usando FTP o Kudu)
2. En Azure Portal:
   - **Configuración** > **Variables de aplicación**
   - **Nombre**: `FIREBASE_CREDENTIALS_FILE`
   - **Valor**: `/home/site/wwwroot/firebase-credentials.json` (ruta completa al archivo)
   - Guarda

## Paso 3: Verificar la Configuración

1. Reinicia tu App Service en Azure Portal
2. Revisa los logs de aplicación:
   - En Azure Portal > **App Service** > **Registro de aplicaciones** > **Log stream**
   - Deberías ver: `"Firebase inicializado desde FIREBASE_CREDENTIALS_JSON"`

## Paso 4: Probar las Notificaciones

1. Inicia sesión en la app Flutter (esto guardará el token FCM)
2. Desde la web, ve a **Notificaciones** y envía una notificación de prueba
3. Revisa los logs para ver:
   - `"Enviando notificación. Usuario: ..., Tokens encontrados: X"`
   - `"Notificación enviada por ... Éxitos=X, Fallos=Y"`

## Estructura del JSON de Firebase

El archivo JSON debería verse así:

```json
{
  "type": "service_account",
  "project_id": "tu-proyecto-firebase",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xxxxx@tu-proyecto.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
```

## Solución de Problemas

### Error: "Firebase no configurado"
- Verifica que la variable de entorno esté configurada correctamente
- Asegúrate de que el JSON esté completo (sin cortes)
- Reinicia el App Service después de agregar la variable

### Error: "firebase_admin no está instalado"
- Verifica que `firebase-admin==6.5.0` esté en `requirements.txt`
- Revisa que el deployment haya instalado las dependencias

### Notificaciones no llegan
- Verifica que los usuarios tengan tokens FCM guardados (revisa la tabla `Usuario` en la BD)
- Revisa los logs para ver si hay errores de Firebase
- Verifica que el proyecto Firebase tenga Cloud Messaging habilitado

## Notas Importantes

⚠️ **Seguridad**: 
- El archivo JSON contiene credenciales sensibles
- NO lo subas a GitHub
- Mantén la variable de entorno protegida en Azure

✅ **Mejores Prácticas**:
- Usa la variable `FIREBASE_CREDENTIALS_JSON` (más seguro que archivo)
- Reinicia el App Service después de cambiar variables de entorno
- Revisa los logs regularmente para detectar problemas

