from rest_framework import viewsets
from gestion.models import Usuario
from gestion.serializadores.usuario import UsuarioSerializer

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
