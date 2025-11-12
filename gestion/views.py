from django.http import JsonResponse
from .models import Categoria, Producto, ProductoImagen, Sucursal, Stock, Cliente, Venta, VentaDetalle, Pago, Usuario, Rol, ProductoVariante, MovimientoStock

def categorias(request):
    return JsonResponse(list(Categoria.objects.values()), safe=False)

def productos(request):
    return JsonResponse(list(Producto.objects.values()), safe=False)

def producto_variantes(request):
    return JsonResponse(list(ProductoVariante.objects.values()), safe=False)

def producto_imagen(request):
    return JsonResponse(list(ProductoImagen.objects.values()), safe=False)

def sucursales(request):
    return JsonResponse(list(Sucursal.objects.values()), safe=False)

def stocks(request):
    return JsonResponse(list(Stock.objects.values()), safe=False)

def movimientos_stock(request):
    return JsonResponse(list(MovimientoStock.objects.values()), safe=False)

def clientes(request):
    return JsonResponse(list(Cliente.objects.values()), safe=False)

def ventas(request):
    return JsonResponse(list(Venta.objects.values()), safe=False)

def venta_detalles(request):
    return JsonResponse(list(VentaDetalle.objects.values()), safe=False)

def pagos(request):
    return JsonResponse(list(Pago.objects.values()), safe=False)

def usuarios(request):
    return JsonResponse(list(Usuario.objects.values()), safe=False)

def roles(request):
    return JsonResponse(list(Rol.objects.values()), safe=False)

