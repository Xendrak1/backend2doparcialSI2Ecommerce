from rest_framework import viewsets
from gestion.models import Rol
from gestion.serializadores.rol import RolSerializer

class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
