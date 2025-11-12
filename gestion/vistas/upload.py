import os
from uuid import uuid4
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class UploadImageView(APIView):
    """
    Subida simple de imágenes (entorno de desarrollo).
    FormData: image (archivo)
    Respuesta: { url: '/media/products/<archivo>' }
    """
    def post(self, request):
        file = request.FILES.get("image")
        if not file:
            return Response({"detail": "archivo 'image' requerido"}, status=status.HTTP_400_BAD_REQUEST)
        products_dir = os.path.join(settings.MEDIA_ROOT, "products")
        os.makedirs(products_dir, exist_ok=True)
        name, ext = os.path.splitext(file.name)
        safe_name = f"{uuid4().hex}{ext or '.jpg'}"
        fs = FileSystemStorage(location=products_dir, base_url=settings.MEDIA_URL + "products/")
        filename = fs.save(safe_name, file)
        url = fs.url(filename)
        return Response({"url": url}, status=status.HTTP_201_CREATED)


