from rest_framework import viewsets
from gestion.models import Stock
from gestion.serializadores.stock import StockSerializer

class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.select_related(
        'producto_variante__producto',
        'sucursal'
    ).all()
    serializer_class = StockSerializer
