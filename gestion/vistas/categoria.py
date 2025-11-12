from rest_framework import viewsets
from gestion.models import Categoria
from gestion.serializadores.categoria import CategoriaSerializer

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
