from rest_framework import viewsets
from gestion.models import Pago
from gestion.serializadores.pago import PagoSerializer

class PagoViewSet(viewsets.ModelViewSet):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer
