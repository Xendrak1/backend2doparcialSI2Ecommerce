from rest_framework import viewsets
from gestion.models import ProductoVariante
from gestion.serializadores.producto_variante import ProductoVarianteSerializer

class ProductoVarianteViewSet(viewsets.ModelViewSet):
    queryset = ProductoVariante.objects.select_related('producto').all()
    serializer_class = ProductoVarianteSerializer
