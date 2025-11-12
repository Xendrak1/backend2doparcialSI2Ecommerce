from django.contrib import admin
from .models import *

### INLINE para ver imágenes dentro del producto
class ProductoImagenInline(admin.TabularInline):
    model = ProductoImagen
    extra = 1
    fields = ('url',)
    readonly_fields = ()

### CATEGORÍAS
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion')
    search_fields = ('nombre',)

### PRODUCTOS
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'categoria', 'precio_base', 'estado')
    search_fields = ('nombre', 'codigo_base')
    list_filter = ('estado', 'categoria')
    inlines = [ProductoImagenInline]
    list_per_page = 20

### VARIANTES
@admin.register(ProductoVariante)
class ProductoVarianteAdmin(admin.ModelAdmin):
    list_display = ('id', 'producto', 'codigo', 'talla', 'color', 'modelo', 'precio', 'codigo_barras')
    search_fields = ('codigo', 'producto__nombre')
    list_filter = ('talla', 'color', 'modelo')
    list_per_page = 20

### SUCURSALES
@admin.register(Sucursal)
class SucursalAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'ubicacion')
    search_fields = ('nombre',)

### STOCK
@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('id', 'producto_variante', 'sucursal', 'cantidad')
    search_fields = ('producto_variante__codigo', 'sucursal__nombre')
    list_filter = ('sucursal',)
    list_per_page = 20

### MOVIMIENTOS DE STOCK
@admin.register(MovimientoStock)
class MovimientoStockAdmin(admin.ModelAdmin):
    list_display = ('id', 'producto_variante', 'sucursal', 'tipo_movimiento', 'cantidad', 'fecha')
    list_filter = ('tipo_movimiento', 'sucursal')
    search_fields = ('producto_variante__codigo',)
    list_per_page = 25

### CLIENTES
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'apellido', 'email', 'telefono', 'documento')
    search_fields = ('nombre', 'apellido', 'email', 'documento')
    list_per_page = 20

### VENTAS
@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'sucursal', 'total', 'tipo_pago', 'estado', 'estado_pago', 'fecha')
    list_filter = ('tipo_pago', 'estado', 'estado_pago', 'sucursal')
    search_fields = ('cliente__nombre', 'cliente__apellido')
    date_hierarchy = 'fecha'
    list_per_page = 20

### DETALLES DE VENTA
@admin.register(VentaDetalle)
class VentaDetalleAdmin(admin.ModelAdmin):
    list_display = ('id', 'venta', 'producto_variante', 'cantidad', 'precio', 'subtotal')
    search_fields = ('venta__id', 'producto_variante__codigo')
    list_per_page = 25

### PAGOS
@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'venta', 'monto', 'metodo', 'estado', 'fecha_pago')
    list_filter = ('estado', 'metodo')
    search_fields = ('venta__id',)
    list_per_page = 20

### ROLES
@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'permisos')

### USUARIOS (internos del sistema, NO los de Django)
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'email', 'rol_id')
    search_fields = ('nombre', 'email')
