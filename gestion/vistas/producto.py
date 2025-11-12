from rest_framework import viewsets
from django.db.models import Min, Max
from gestion.models import Producto, ProductoVariante
from gestion.serializadores.producto import ProductoSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    
    def get_queryset(self):
        """Optimizar consultas prefetching variantes"""
        return Producto.objects.prefetch_related('productovariante_set').all()
