from rest_framework import viewsets
from gestion.models import ProductoImagen
from gestion.serializadores.producto_imagen import ProductoImagenSerializer

class ProductoImagenViewSet(viewsets.ModelViewSet):
    queryset = ProductoImagen.objects.all()
    serializer_class = ProductoImagenSerializer
