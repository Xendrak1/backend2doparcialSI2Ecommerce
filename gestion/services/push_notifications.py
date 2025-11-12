import json
import logging
import os
from typing import Any, Dict, Iterable, Optional, Tuple, List

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


def _sanitize_tokens(tokens: Iterable[str]) -> List[str]:
    """
    Normaliza un iterable de tokens eliminando vacíos y duplicados.
    """
    if not tokens:
        return []
    vistos = set()
    resultado = []
    for token in tokens:
        token_clean = (token or "").strip()
        if not token_clean or token_clean in vistos:
            continue
        resultado.append(token_clean)
        vistos.add(token_clean)
    return resultado


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


def send_push_to_tokens(
    tokens: Iterable[str],
    title: str,
    body: str,
    data: Optional[Dict[str, Any]] = None,
) -> Tuple[int, int]:
    """
    Envía una notificación push a múltiples tokens.
    Retorna (éxitos, fallidos).
    """
    tokens_list = _sanitize_tokens(tokens)
    if not tokens_list:
        return 0, 0

    app = _initialize_firebase_app()
    if not app or messaging is None:
        logger.warning("Firebase Admin SDK no está inicializado. No se pueden enviar notificaciones masivas.")
        return 0, len(tokens_list)

    payload_data = {k: str(v) for k, v in (data or {}).items()}

    try:
        # Preferir MulticastMessage para eficiencia
        multicast = messaging.MulticastMessage(
            notification=messaging.Notification(title=title, body=body),
            data=payload_data,
            tokens=tokens_list,
        )
        response = messaging.send_multicast(multicast, app=app)
        failed = sum(1 for r in response.responses if not r.success)
        if failed:
            logger.warning("Algunas notificaciones fallaron: %s fallos", failed)
        return response.success_count, failed
    except AttributeError:
        # Implementación alternativa si la versión de firebase_admin no soporta send_multicast
        successes = 0
        failures = 0
        for token in tokens_list:
            ok, _ = send_push_to_token(token, title, body, data)
            if ok:
                successes += 1
            else:
                failures += 1
        return successes, failures
    except Exception as exc:  # pragma: no cover
        logger.error("Error enviando notificaciones masivas: %s", exc)
        return 0, len(tokens_list)


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
    success, failed = send_push_to_tokens([usuario.fcm_token], title, body, data)
    return (success == 1), None if failed == 0 else "failed"


def send_push_to_usuarios(
    usuarios: Iterable[Usuario],
    title: str,
    body: str,
    data: Optional[Dict[str, Any]] = None,
) -> Tuple[int, int]:
    """
    Envía una notificación push a un conjunto de usuarios.
    Retorna (éxitos, fallos).
    """
    tokens = [getattr(u, "fcm_token", None) for u in usuarios]
    return send_push_to_tokens(tokens, title, body, data)


