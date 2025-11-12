from rest_framework import serializers
from gestion.models import ProductoImagen

class ProductoImagenSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoImagen
        fields = '__all__'
