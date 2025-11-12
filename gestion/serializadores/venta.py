from rest_framework import serializers
from gestion.models import Venta

class VentaSerializer(serializers.ModelSerializer):
    # Campos adicionales para mostrar nombres en lugar de solo IDs
    cliente_nombre = serializers.SerializerMethodField()
    sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)
    
    class Meta:
        model = Venta
        fields = '__all__'
    
    def get_cliente_nombre(self, obj):
        """Retorna el nombre completo del cliente"""
        if obj.cliente:
            nombre = obj.cliente.nombre or ''
            apellido = obj.cliente.apellido or ''
            return f"{nombre} {apellido}".strip() or obj.cliente.email or 'Sin nombre'
        return None
