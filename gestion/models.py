from django.db import models

# ================== CATEGORÍA ==================
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        managed = True
        db_table = 'categoria'

# ================== PRODUCTO ==================
class Producto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    codigo_base = models.CharField(max_length=50, blank=True, null=True)
    precio_base = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.CharField(max_length=20, default='activo')

    def __str__(self):
        return self.nombre

    class Meta:
        managed = True
        db_table = 'producto'

class ProductoVariante(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=50, unique=True)  # SKU
    talla = models.CharField(max_length=20, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    modelo = models.CharField(max_length=50, blank=True, null=True)
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    codigo_barras = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.producto.nombre} - {self.codigo}"

    class Meta:
        managed = True
        db_table = 'producto_variante'

class ProductoImagen(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    url = models.TextField()

    class Meta:
        managed = True
        db_table = 'producto_imagen'

# ================== SUCURSAL Y STOCK ==================
class Sucursal(models.Model):
    nombre = models.CharField(max_length=100)
    ubicacion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        managed = True
        db_table = 'sucursal'


class Stock(models.Model):
    producto_variante = models.ForeignKey(ProductoVariante, on_delete=models.CASCADE)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=0)

    class Meta:
        managed = True
        db_table = 'stock'

class MovimientoStock(models.Model):
    producto_variante = models.ForeignKey(ProductoVariante, on_delete=models.CASCADE)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    tipo_movimiento = models.CharField(max_length=20) 
    cantidad = models.IntegerField()
    fecha = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'movimiento_stock'

# ================== CLIENTES Y VENTAS ==================
class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=120, blank=True, null=True)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    documento = models.CharField(max_length=50, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    class Meta:
        managed = True
        db_table = 'cliente'

class Venta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    tipo_pago = models.CharField(max_length=20)  # contado/credito
    canal_venta = models.CharField(max_length=20, blank=True, null=True)  # tienda/online
    estado = models.CharField(max_length=20, default='pendiente')
    estado_pago = models.CharField(max_length=20, default='pendiente')
    fecha = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'venta'

class VentaDetalle(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto_variante = models.ForeignKey(ProductoVariante, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        managed = True
        db_table = 'venta_detalle'

class Pago(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_pago = models.DateField()
    metodo = models.CharField(max_length=30, blank=True, null=True)
    estado = models.CharField(max_length=20, default='procesado')

    class Meta:
        managed = True
        db_table = 'pago'


# ================== USUARIOS Y ROLES ==================
class Rol(models.Model):
    nombre = models.CharField(max_length=50)
    permisos = models.JSONField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'rol'


class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.CharField(max_length=120, unique=True)
    password_hash = models.TextField()
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    fcm_token = models.CharField(max_length=512, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'usuario'


# ================== TOKENS DE API (Auth simple) ==================
class ApiToken(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='tokens')
    key = models.CharField(max_length=64, unique=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'api_token'
