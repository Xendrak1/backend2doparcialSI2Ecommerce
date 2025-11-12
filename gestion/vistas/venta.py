from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
import logging
from gestion.models import Venta, VentaDetalle, Cliente, Sucursal, Producto, ProductoVariante, Stock, Usuario, ApiToken
from gestion.serializadores.venta import VentaSerializer
from gestion.services.push_notifications import send_push_to_usuario

logger = logging.getLogger(__name__)

class VentaViewSet(viewsets.ModelViewSet):
    queryset = Venta.objects.select_related('cliente', 'sucursal').all().order_by('-fecha', '-id')
    serializer_class = VentaSerializer
    
    def get_queryset(self):
        """
        Si el usuario es cliente, solo mostrar sus propias ventas.
        Si es admin/vendedor, mostrar todas.
        """
        qs = super().get_queryset()
        # Obtener el usuario autenticado desde el token
        auth_header = self.request.headers.get("Authorization", "")
        if auth_header.startswith("Token "):
            token = auth_header.split(" ", 1)[1].strip()
            try:
                from gestion.models import ApiToken, Usuario
                tok = ApiToken.objects.select_related("usuario__rol").get(key=token)
                usuario = tok.usuario
                rol_nombre = usuario.rol.nombre.lower() if usuario.rol else ""
                # Si es cliente, filtrar por su email
                if rol_nombre == "cliente":
                    # Buscar el cliente por email del usuario
                    from gestion.models import Cliente
                    try:
                        cliente = Cliente.objects.get(email=usuario.email)
                        qs = qs.filter(cliente=cliente)
                    except Cliente.DoesNotExist:
                        # Si no existe cliente, no mostrar nada
                        qs = qs.none()
            except:
                pass
        return qs


class POSCheckout(APIView):
    """
    Crea una venta + detalles para el POS.
    Body esperado:
    {
      "cliente": <id opcional>,
      "cliente_email": "<email opcional>",
      "sucursal": <id sucursal, default 1>,
      "tipo_pago": "contado"|"credito",
      "items": [ { "producto": <id>, "cantidad": <int>, "precio": <decimal> } ]
    }
    """
    @transaction.atomic
    def post(self, request):
        data = request.data or {}
        items = data.get("items") or []
        if not items:
            return Response({"detail": "items es requerido"}, status=status.HTTP_400_BAD_REQUEST)

        # Cliente
        cliente = None
        cliente_id = data.get("cliente")
        cliente_email = data.get("cliente_email")
        if cliente_id:
            try:
                cliente = Cliente.objects.get(id=cliente_id)
            except Cliente.DoesNotExist:
                return Response({"detail": "cliente no encontrado"}, status=status.HTTP_400_BAD_REQUEST)
        elif cliente_email:
            cliente, _ = Cliente.objects.get_or_create(email=cliente_email, defaults={"nombre": cliente_email})
        else:
            cliente, _ = Cliente.objects.get_or_create(email="mostrador@local", defaults={"nombre": "Mostrador"})

        # Sucursal
        sucursal_id = data.get("sucursal") or 1
        try:
            sucursal = Sucursal.objects.get(id=sucursal_id)
        except Sucursal.DoesNotExist:
            return Response({"detail": "sucursal no encontrada"}, status=status.HTTP_400_BAD_REQUEST)

        tipo_pago = data.get("tipo_pago") or "contado"
        total = 0

        # Si el tipo de pago es QR, la venta queda pendiente hasta verificación
        # Si es contado, se marca como completada y pagada inmediatamente
        if tipo_pago.lower() == "qr":
            estado_venta = "pendiente"
            estado_pago_venta = "pendiente"
        else:
            estado_venta = "completado"
            estado_pago_venta = "pagado"

        venta = Venta.objects.create(
            cliente=cliente,
            sucursal=sucursal,
            total=0,
            tipo_pago=tipo_pago,
            canal_venta="tienda",
            estado=estado_venta,
            estado_pago=estado_pago_venta,
            fecha=timezone.now(),
        )

        detalles_resp = []
        for it in items:
            # Aceptar producto_variante (preferido) o producto (compatibilidad)
            producto_variante_id = it.get("producto_variante")
            producto_id = it.get("producto")
            cantidad = int(it.get("cantidad") or 1)
            precio = float(it.get("precio") or 0)
            
            variante = None
            if producto_variante_id:
                # Si se envía producto_variante, usarlo directamente
                try:
                    variante = ProductoVariante.objects.get(id=producto_variante_id)
                    prod = variante.producto
                except ProductoVariante.DoesNotExist:
                    transaction.set_rollback(True)
                    return Response({"detail": f"producto_variante {producto_variante_id} no existe"}, status=status.HTTP_400_BAD_REQUEST)
            elif producto_id:
                # Compatibilidad: si se envía producto, buscar o crear variante
                try:
                    prod = Producto.objects.get(id=producto_id)
                except Producto.DoesNotExist:
                    transaction.set_rollback(True)
                    return Response({"detail": f"producto {producto_id} no existe"}, status=status.HTTP_400_BAD_REQUEST)
                
                # Seleccionar o crear variante
                variante = ProductoVariante.objects.filter(producto=prod).first()
                if not variante:
                    variante = ProductoVariante.objects.create(
                        producto=prod,
                        codigo=f"POS-{prod.id}-{timezone.now().strftime('%H%M%S%f')}",
                        talla="",
                        color="",
                        modelo="POS",
                        precio=precio,
                        codigo_barras=f"POS{prod.id}{timezone.now().strftime('%H%M%S')}",
                    )
            else:
                transaction.set_rollback(True)
                return Response({"detail": "cada item requiere producto_variante o producto"}, status=status.HTTP_400_BAD_REQUEST)

            # Validar y actualizar stock ANTES de crear el detalle de venta
            stock, created = Stock.objects.get_or_create(
                producto_variante=variante,
                sucursal=sucursal,
                defaults={'cantidad': 0}
            )
            
            stock_antes = stock.cantidad
            logger.info(f"Stock antes de venta: Producto={prod.nombre}, Variante={variante.id}, Sucursal={sucursal.nombre}, Stock={stock_antes}, Cantidad solicitada={cantidad}")
            
            # Validar stock disponible
            if stock.cantidad < cantidad:
                transaction.set_rollback(True)
                error_msg = f"Stock insuficiente para {prod.nombre} en {sucursal.nombre}. Disponible: {stock.cantidad}, Solicitado: {cantidad}"
                logger.warning(error_msg)
                return Response({
                    "detail": error_msg
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Restar la cantidad del stock
            stock.cantidad -= cantidad
            stock.save(update_fields=['cantidad'])
            logger.info(f"Stock actualizado: Producto={prod.nombre}, Variante={variante.id}, Sucursal={sucursal.nombre}, Stock anterior={stock_antes}, Stock nuevo={stock.cantidad}")
            
            # Crear el detalle de venta después de validar y actualizar el stock
            subtotal = precio * cantidad
            total += subtotal
            det = VentaDetalle.objects.create(
                venta=venta,
                producto_variante=variante,
                cantidad=cantidad,
                precio=precio,
                subtotal=subtotal,
            )
            
            detalles_resp.append({
                "id": det.id,
                "producto": prod.nombre,
                "cantidad": cantidad,
                "precio": precio,
                "subtotal": subtotal,
            })

        venta.total = total
        venta.save(update_fields=["total"])

        return Response({
            "venta_id": venta.id,
            "total": total,
            "items": detalles_resp,
        }, status=status.HTTP_201_CREATED)


class OnlineCheckout(APIView):
    """
    Crea una venta ONLINE (pedido) con estado pendiente.
    Body:
    { cliente?, cliente_email?, items:[{producto,cantidad,precio}], tipo_pago? }
    """
    @transaction.atomic
    def post(self, request):
        data = request.data or {}
        items = data.get("items") or []
        if not items:
            return Response({"detail": "items es requerido"}, status=status.HTTP_400_BAD_REQUEST)

        # Intentar identificar al usuario autenticado (para clientes)
        usuario_autenticado = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Token "):
            token = auth_header.split(" ", 1)[1].strip()
            try:
                tok = ApiToken.objects.select_related("usuario__rol").get(key=token)
                usuario_autenticado = tok.usuario
            except ApiToken.DoesNotExist:
                usuario_autenticado = None

        cliente = None
        cliente_id = data.get("cliente")
        cliente_email_data = data.get("cliente_email")
        cliente_nombre_data = data.get("cliente_nombre") or data.get("cliente_name")
        if cliente_id:
            try:
                cliente = Cliente.objects.get(id=cliente_id)
            except Cliente.DoesNotExist:
                return Response({"detail": "cliente no encontrado"}, status=status.HTTP_400_BAD_REQUEST)

        if cliente is None:
            cliente_email = None
            cliente_nombre = None

            if (
                usuario_autenticado
                and usuario_autenticado.rol
                and usuario_autenticado.rol.nombre
                and usuario_autenticado.rol.nombre.lower() == "cliente"
            ):
                cliente_email = usuario_autenticado.email
                cliente_nombre = usuario_autenticado.nombre
            elif cliente_email_data:
                cliente_email = cliente_email_data
                cliente_nombre = cliente_nombre_data or cliente_email_data

            if cliente_email:
                cliente, _ = Cliente.objects.get_or_create(
                    email=cliente_email, defaults={"nombre": cliente_nombre or cliente_email}
                )
            else:
                cliente, _ = Cliente.objects.get_or_create(
                    email="online@cliente", defaults={"nombre": "Cliente Online"}
                )
        # Sucursal genérica 1
        try:
            sucursal = Sucursal.objects.get(id=data.get("sucursal") or 1)
        except Sucursal.DoesNotExist:
            return Response({"detail": "sucursal no encontrada"}, status=status.HTTP_400_BAD_REQUEST)

        tipo_pago = data.get("tipo_pago") or "qr"
        total = 0
        venta = Venta.objects.create(
            cliente=cliente,
            sucursal=sucursal,
            total=0,
            tipo_pago=tipo_pago,
            canal_venta="online",
            estado="pendiente",
            estado_pago="pendiente",
            fecha=timezone.now(),
        )

        for it in items:
            producto_id = it.get("producto")
            cantidad = int(it.get("cantidad") or 1)
            precio = float(it.get("precio") or 0)
            if not producto_id:
                transaction.set_rollback(True)
                return Response({"detail": "cada item requiere producto"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                prod = Producto.objects.get(id=producto_id)
            except Producto.DoesNotExist:
                transaction.set_rollback(True)
                return Response({"detail": f"producto {producto_id} no existe"}, status=status.HTTP_400_BAD_REQUEST)
            # Variante fallback
            variante = ProductoVariante.objects.filter(producto=prod).first()
            if not variante:
                variante = ProductoVariante.objects.create(
                    producto=prod,
                    codigo=f"ON-{prod.id}-{timezone.now().strftime('%H%M%S%f')}",
                    talla="",
                    color="",
                    modelo="ONLINE",
                    precio=precio,
                    codigo_barras=f"ON{prod.id}{timezone.now().strftime('%H%M%S')}",
                )
            subtotal = precio * cantidad
            total += subtotal
            VentaDetalle.objects.create(
                venta=venta, producto_variante=variante, cantidad=cantidad, precio=precio, subtotal=subtotal
            )
        venta.total = total
        venta.save(update_fields=["total"])
        return Response({"venta_id": venta.id, "total": total}, status=status.HTTP_201_CREATED)


class ConfirmarPagoVenta(APIView):
    """
    Confirma pago de una venta (marca pagado y completado).
    """
    def post(self, request):
        venta_id = request.data.get("venta_id")
        if not venta_id:
            return Response({"detail": "venta_id requerido"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            venta = Venta.objects.get(id=venta_id)
        except Venta.DoesNotExist:
            return Response({"detail": "venta no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        venta.estado_pago = "pagado"
        venta.estado = "completado"
        venta.save(update_fields=["estado_pago", "estado"])

        # Intentar notificar al cliente si existe un usuario con ese email
        cliente_email = venta.cliente.email if venta.cliente else None
        if cliente_email:
            usuario = Usuario.objects.filter(email=cliente_email).first()
            if usuario:
                ok, detail = send_push_to_usuario(
                    usuario,
                    title="Pago confirmado ✅",
                    body=f"Tu pedido #{venta.id} fue confirmado. ¡Gracias por tu compra!",
                    data={
                        "venta_id": str(venta.id),
                        "tipo": "confirmacion_pago",
                    },
                )
                if not ok:
                    logger.warning("No se pudo enviar push a %s: %s", cliente_email, detail)
            else:
                logger.info("No se encontró usuario asociado al email %s para notificar", cliente_email)
        else:
            logger.info("La venta %s no tiene email de cliente para notificar", venta.id)

        return Response({"ok": True}, status=status.HTTP_200_OK)
