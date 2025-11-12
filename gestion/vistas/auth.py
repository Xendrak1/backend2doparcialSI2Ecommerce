from django.utils.crypto import get_random_string
from django.db import transaction
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from gestion.models import Usuario, Rol, ApiToken, Cliente


def build_user_payload(usuario: Usuario):
    permisos = usuario.rol.permisos or []
    return {
        "id": usuario.id,
        "name": usuario.nombre,
        "email": usuario.email,
        "role": usuario.rol.nombre.lower(),
        "permissions": permisos if isinstance(permisos, list) else [],
    }


class RegisterView(APIView):
    @transaction.atomic
    def post(self, request):
        data = request.data or {}
        nombre = data.get("nombre") or data.get("name") or ""
        email = data.get("email")
        password = data.get("password")
        rol_nombre = (data.get("rol") or data.get("role") or "cliente").lower()
        if not email or not password:
            return Response({"detail": "email y password son requeridos"}, status=status.HTTP_400_BAD_REQUEST)
        rol, _ = Rol.objects.get_or_create(nombre=rol_nombre, defaults={"permisos": []})
        if Usuario.objects.filter(email=email).exists():
            return Response({"detail": "email ya registrado"}, status=status.HTTP_400_BAD_REQUEST)
        user = Usuario.objects.create(
            nombre=nombre or email.split("@")[0],
            email=email,
            password_hash=make_password(password),
            rol=rol,
        )
        # Si es cliente, generar un Cliente (para relacionar ventas)
        if rol_nombre == "cliente":
            Cliente.objects.get_or_create(email=email, defaults={"nombre": nombre or email})
        return Response(build_user_payload(user), status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        data = request.data or {}
        email = data.get("email")
        password = data.get("password")
        if not email or not password:
            return Response({"detail": "email y password son requeridos"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = Usuario.objects.select_related("rol").get(email=email)
        except Usuario.DoesNotExist:
            return Response({"detail": "credenciales inválidas"}, status=status.HTTP_400_BAD_REQUEST)
        # Entorno de prueba: aceptar hash válido O coincidencia directa en texto plano
        if not (check_password(password, user.password_hash) or user.password_hash == password):
            return Response({"detail": "credenciales inválidas"}, status=status.HTTP_400_BAD_REQUEST)
        # Crear token (uno por sesión)
        token = get_random_string(48)
        ApiToken.objects.create(usuario=user, key=token)
        payload = build_user_payload(user)
        return Response({"token": token, "user": payload}, status=status.HTTP_200_OK)


class MeView(APIView):
    def get(self, request):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Token "):
            return Response({"detail": "no autorizado"}, status=status.HTTP_401_UNAUTHORIZED)
        token = auth.split(" ", 1)[1].strip()
        try:
            tok = ApiToken.objects.select_related("usuario__rol").get(key=token)
        except ApiToken.DoesNotExist:
            return Response({"detail": "no autorizado"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(build_user_payload(tok.usuario), status=status.HTTP_200_OK)


class LogoutView(APIView):
    def post(self, request):
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Token "):
            token = auth.split(" ", 1)[1].strip()
            ApiToken.objects.filter(key=token).delete()
        return Response({"ok": True}, status=status.HTTP_200_OK)


class BootstrapView(APIView):
    """
    SOLO DESARROLLO: crea roles básicos y 3 usuarios de ejemplo si no existen.
    admin: admin@demo.com / admin123
    vendedor: vendedor@demo.com / vendedor123
    cliente: cliente@demo.com / cliente123
    """
    def post(self, request):
        created = []
        for rname, permisos in [
            ("admin", ["*"]),
            ("vendedor", ["dashboard:ver", "productos:leer", "ventas:pos", "clientes:*", "stock:mov", "reportes:ver"]),
            ("cliente", ["productos:leer", "ventas:online"]),
        ]:
            Rol.objects.get_or_create(nombre=rname, defaults={"permisos": permisos})
        def ensure_user(email, name, rol, password):
            if Usuario.objects.filter(email=email).exists():
                return False
            u = Usuario.objects.create(
                nombre=name,
                email=email,
                password_hash=make_password(password),
                rol=Rol.objects.get(nombre=rol),
            )
            if rol == "cliente":
                Cliente.objects.get_or_create(email=email, defaults={"nombre": name})
            return True
        if ensure_user("admin@demo.com", "Admin Demo", "admin", "admin123"):
            created.append("admin@demo.com")
        if ensure_user("vendedor@demo.com", "Vendedor Demo", "vendedor", "vendedor123"):
            created.append("vendedor@demo.com")
        if ensure_user("cliente@demo.com", "Cliente Demo", "cliente", "cliente123"):
            created.append("cliente@demo.com")
        return Response({"created": created}, status=status.HTTP_200_OK)

