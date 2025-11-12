from rest_framework import serializers
from gestion.models import ProductoVariante

class ProductoVarianteSerializer(serializers.ModelSerializer):
    # Campo adicional para mostrar el nombre del producto
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    
    class Meta:
        model = ProductoVariante
        fields = '__all__'
