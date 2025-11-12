import logging
from typing import List

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from gestion.models import ApiToken, Usuario
from gestion.services.push_notifications import send_push_to_usuarios

logger = logging.getLogger(__name__)


def _usuario_puede_enviar(usuario: Usuario) -> bool:
    if not usuario or not usuario.rol:
        return False
    rol_nombre = (usuario.rol.nombre or "").strip().lower()
    if rol_nombre == "admin":
        return True

    permisos = usuario.rol.permisos or []
    if isinstance(permisos, list):
        permisos_normalizados = {str(p).strip().lower() for p in permisos}
        return "*" in permisos_normalizados or "notificaciones:enviar" in permisos_normalizados
    if isinstance(permisos, str):
        permisos_lower = permisos.strip().lower()
        return permisos_lower == "*" or permisos_lower == "notificaciones:enviar"
    return False


class NotificacionGlobalView(APIView):
    """
    Permite a un administrador enviar notificaciones push personalizadas
    a todos los usuarios con token FCM, o filtrados por rol.
    """

    def post(self, request):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Token "):
            return Response({"detail": "no autorizado"}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth.split(" ", 1)[1].strip()
        try:
            tok = ApiToken.objects.select_related("usuario__rol").get(key=token)
        except ApiToken.DoesNotExist:
            return Response({"detail": "no autorizado"}, status=status.HTTP_401_UNAUTHORIZED)

        usuario = tok.usuario
        if not _usuario_puede_enviar(usuario):
            return Response({"detail": "sin permisos para enviar notificaciones"}, status=status.HTTP_403_FORBIDDEN)

        data = request.data or {}
        titulo = data.get("titulo") or data.get("title")
        mensaje = data.get("mensaje") or data.get("message")
        if not titulo or not mensaje:
            return Response({"detail": "titulo y mensaje son requeridos"}, status=status.HTTP_400_BAD_REQUEST)

        roles_raw = data.get("roles") or []
        if isinstance(roles_raw, str):
            roles_raw = [roles_raw]
        roles_filtrados: List[str] = [
            str(r).strip().lower()
            for r in roles_raw
            if str(r).strip()
        ]

        extra_data = data.get("data") or {}
        if not isinstance(extra_data, dict):
            extra_data = {}

        usuarios = Usuario.objects.exclude(fcm_token__isnull=True).exclude(fcm_token="")
        if roles_filtrados:
            usuarios = usuarios.filter(rol__nombre__in=roles_filtrados)

        total_destinatarios = usuarios.count()
        if total_destinatarios == 0:
            logger.info(
                "Notificación global omitida: sin destinatarios para roles=%s",
                roles_filtrados or ["todos"],
            )
            return Response(
                {
                    "ok": False,
                    "detail": "No hay usuarios con tokens FCM disponibles para los filtros proporcionados.",
                    "sent": 0,
                    "failed": 0,
                    "total": 0,
                    "roles": roles_filtrados,
                },
                status=status.HTTP_200_OK,
            )

        enviados, fallidos = send_push_to_usuarios(usuarios, titulo, mensaje, extra_data)
        logger.info(
            "Notificación enviada por %s (%s). Éxitos=%s, Fallos=%s, Total=%s, Roles=%s",
            usuario.email,
            usuario.rol.nombre if usuario.rol else "sin rol",
            enviados,
            fallidos,
            total_destinatarios,
            roles_filtrados or ["todos"],
        )

        return Response(
            {
                "ok": True,
                "sent": enviados,
                "failed": fallidos,
                "total": total_destinatarios,
                "roles": roles_filtrados,
            },
            status=status.HTTP_200_OK,
        )



