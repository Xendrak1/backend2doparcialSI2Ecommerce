from rest_framework import serializers
from gestion.models import MovimientoStock

class MovimientoStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovimientoStock
        fields = '__all__'
