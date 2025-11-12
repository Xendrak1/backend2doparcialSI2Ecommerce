from rest_framework import serializers
from gestion.models import Stock

class StockSerializer(serializers.ModelSerializer):
    # Campos adicionales para mostrar nombres en lugar de solo IDs
    producto = serializers.SerializerMethodField()
    producto_variante_id = serializers.IntegerField(source='producto_variante.id', read_only=True)
    sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)
    sucursal_id = serializers.IntegerField(source='sucursal.id', read_only=True)
    
    class Meta:
        model = Stock
        fields = ['id', 'producto_variante', 'producto_variante_id', 'producto', 'sucursal', 'sucursal_id', 'sucursal_nombre', 'cantidad']
        read_only_fields = ['producto_variante_id', 'producto', 'sucursal_id', 'sucursal_nombre']
    
    def get_producto(self, obj):
        # Retornar el nombre del producto desde producto_variante.producto.nombre
        if obj.producto_variante and obj.producto_variante.producto:
            return obj.producto_variante.producto.nombre
        return None
