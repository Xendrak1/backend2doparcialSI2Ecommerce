from rest_framework import serializers
from gestion.models import Producto, ProductoVariante

class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    precio = serializers.SerializerMethodField()
    precio_min = serializers.SerializerMethodField()
    precio_max = serializers.SerializerMethodField()
    
    class Meta:
        model = Producto
        fields = '__all__'
    
    def _get_variantes(self, obj):
        """Obtener variantes de forma optimizada"""
        # Intentar usar variantes prefetched
        if hasattr(obj, '_prefetched_objects_cache') and 'productovariante_set' in obj._prefetched_objects_cache:
            return list(obj._prefetched_objects_cache['productovariante_set'])
        # Fallback: consulta directa
        return list(ProductoVariante.objects.filter(producto=obj))
    
    def get_precio(self, obj):
        """Retorna precio_base como precio (compatibilidad) o precio mínimo de variantes"""
        variantes = self._get_variantes(obj)
        if variantes:
            precios = [float(v.precio) for v in variantes if v.precio]
            if precios:
                return min(precios)
        # Si no hay variantes o no tienen precio, usar precio_base
        return float(obj.precio_base) if obj.precio_base else 0.0
    
    def get_precio_min(self, obj):
        """Precio mínimo de todas las variantes"""
        variantes = self._get_variantes(obj)
        if variantes:
            precios = [float(v.precio) for v in variantes if v.precio]
            if precios:
                return min(precios)
        return float(obj.precio_base) if obj.precio_base else 0.0
    
    def get_precio_max(self, obj):
        """Precio máximo de todas las variantes"""
        variantes = self._get_variantes(obj)
        if variantes:
            precios = [float(v.precio) for v in variantes if v.precio]
            if precios:
                return max(precios)
        return float(obj.precio_base) if obj.precio_base else 0.0
