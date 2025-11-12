import json
import logging
import os
from typing import Any, Dict, Optional, Tuple

try:
    import firebase_admin
    from firebase_admin import credentials, messaging
except ImportError:  # pragma: no cover
    firebase_admin = None  # type: ignore
    credentials = None  # type: ignore
    messaging = None  # type: ignore

from gestion.models import Usuario

logger = logging.getLogger(__name__)


def _initialize_firebase_app() -> Optional["firebase_admin.App"]:
    """
    Inicializa Firebase Admin SDK usando credenciales configuradas en variables de entorno.
    - FIREBASE_CREDENTIALS_JSON: JSON del service account.
    - FIREBASE_CREDENTIALS_FILE: Ruta al archivo JSON del service account.
    """
    if firebase_admin is None:
        logger.warning("firebase_admin no está instalado. Ejecute 'pip install firebase-admin'.")
        return None

    if firebase_admin._apps:  # type: ignore[attr-defined]
        return firebase_admin.get_app()  # type: ignore[attr-defined]

    json_credentials = os.getenv("FIREBASE_CREDENTIALS_JSON")
    file_credentials = os.getenv("FIREBASE_CREDENTIALS_FILE")

    if json_credentials:
        try:
            cred_dict = json.loads(json_credentials)
            cred = credentials.Certificate(cred_dict)
            app = firebase_admin.initialize_app(cred)
            logger.info("Firebase inicializado desde FIREBASE_CREDENTIALS_JSON")
            return app
        except Exception as exc:  # pragma: no cover - logging y retorno
            logger.error("No se pudo inicializar Firebase con FIREBASE_CREDENTIALS_JSON: %s", exc)
            return None

    if file_credentials and os.path.exists(file_credentials):
        try:
            cred = credentials.Certificate(file_credentials)
            app = firebase_admin.initialize_app(cred)
            logger.info("Firebase inicializado desde FIREBASE_CREDENTIALS_FILE=%s", file_credentials)
            return app
        except Exception as exc:  # pragma: no cover
            logger.error("No se pudo inicializar Firebase con archivo %s: %s", file_credentials, exc)
            return None

    logger.warning(
        "Firebase no configurado. Defina FIREBASE_CREDENTIALS_JSON "
        "o FIREBASE_CREDENTIALS_FILE en las variables de entorno."
    )
    return None


def send_push_to_token(
    token: str,
    title: str,
    body: str,
    data: Optional[Dict[str, Any]] = None,
) -> Tuple[bool, Optional[str]]:
    """
    Envía una notificación push a un token específico.
    Retorna (éxito, detalle/respuesta).
    """
    app = _initialize_firebase_app()
    if not app or messaging is None:
        return False, "firebase_not_initialized"

    try:
        message = messaging.Message(
            token=token,
            notification=messaging.Notification(title=title, body=body),
            data={k: str(v) for k, v in (data or {}).items()},
        )
        response = messaging.send(message, app=app)
        logger.info("Notificación enviada a %s: %s", token, response)
        return True, response
    except Exception as exc:  # pragma: no cover
        logger.error("Error enviando push notification: %s", exc)
        return False, str(exc)


def send_push_to_usuario(
    usuario: Usuario,
    title: str,
    body: str,
    data: Optional[Dict[str, Any]] = None,
) -> Tuple[bool, Optional[str]]:
    """
    Envía una notificación a un usuario (utilizando su campo fcm_token).
    """
    if not usuario or not usuario.fcm_token:
        logger.warning("Usuario %s sin fcm_token, no se envía push", usuario.email if usuario else "desconocido")
        return False, "user_without_token"
    return send_push_to_token(usuario.fcm_token, title, body, data)


