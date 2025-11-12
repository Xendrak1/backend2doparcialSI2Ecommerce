from rest_framework import viewsets
from gestion.models import VentaDetalle
from gestion.serializadores.venta_detalle import VentaDetalleSerializer

class VentaDetalleViewSet(viewsets.ModelViewSet):
    queryset = VentaDetalle.objects.select_related('venta', 'producto_variante__producto').all()
    serializer_class = VentaDetalleSerializer
