from rest_framework import viewsets
from gestion.models import Cliente
from gestion.serializadores.cliente import ClienteSerializer

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all().order_by('nombre')
    serializer_class = ClienteSerializer
