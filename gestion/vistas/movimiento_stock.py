from rest_framework import viewsets
from gestion.models import MovimientoStock
from gestion.serializadores.movimiento_stock import MovimientoStockSerializer

class MovimientoStockViewSet(viewsets.ModelViewSet):
    queryset = MovimientoStock.objects.all()
    serializer_class = MovimientoStockSerializer
