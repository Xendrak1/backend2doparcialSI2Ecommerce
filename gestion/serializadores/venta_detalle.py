from rest_framework import serializers
from gestion.models import VentaDetalle

class VentaDetalleSerializer(serializers.ModelSerializer):
    producto_variante = serializers.SerializerMethodField()
    
    class Meta:
        model = VentaDetalle
        fields = '__all__'
    
    def get_producto_variante(self, obj):
        """Incluir información completa del producto variante"""
        if obj.producto_variante:
            return {
                'id': obj.producto_variante.id,
                'nombre': obj.producto_variante.producto.nombre if obj.producto_variante.producto else None,
                'talla': obj.producto_variante.talla,
                'color': obj.producto_variante.color,
                'producto': {
                    'id': obj.producto_variante.producto.id if obj.producto_variante.producto else None,
                    'nombre': obj.producto_variante.producto.nombre if obj.producto_variante.producto else None,
                } if obj.producto_variante.producto else None
            }
        return None
