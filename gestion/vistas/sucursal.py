from rest_framework import viewsets
from gestion.models import Sucursal
from gestion.serializadores.sucursal import SucursalSerializer

class SucursalViewSet(viewsets.ModelViewSet):
    queryset = Sucursal.objects.all()
    serializer_class = SucursalSerializer
