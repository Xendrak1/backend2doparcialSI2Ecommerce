from django.urls import path, include
from rest_framework.routers import DefaultRouter

from gestion.vistas.categoria import CategoriaViewSet
from gestion.vistas.producto import ProductoViewSet
from gestion.vistas.producto_variante import ProductoVarianteViewSet
from gestion.vistas.producto_imagen import ProductoImagenViewSet
from gestion.vistas.sucursal import SucursalViewSet
from gestion.vistas.stock import StockViewSet
from gestion.vistas.movimiento_stock import MovimientoStockViewSet
from gestion.vistas.cliente import ClienteViewSet
from gestion.vistas.venta import VentaViewSet
from gestion.vistas.venta import POSCheckout, OnlineCheckout, ConfirmarPagoVenta
from gestion.vistas.venta_detalle import VentaDetalleViewSet
from gestion.vistas.pago import PagoViewSet
from gestion.vistas.rol import RolViewSet
from gestion.vistas.usuario import UsuarioViewSet
from gestion.vistas.reportes import (
    ReporteResumen,
    VentasPorDia,
    TopProductos,
    MixPago,
    StockBajo,
    ExportResumenPDF,
    ExportResumenExcel,
    PronosticoVentas,
)
from gestion.vistas.auth import LoginView, RegisterView, LogoutView, MeView, BootstrapView
from gestion.vistas.upload import UploadImageView

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet)
router.register(r'productos', ProductoViewSet)
router.register(r'producto_variantes', ProductoVarianteViewSet)
router.register(r'producto_imagenes', ProductoImagenViewSet)
router.register(r'sucursales', SucursalViewSet)
router.register(r'stocks', StockViewSet)
router.register(r'movimientos_stock', MovimientoStockViewSet)
router.register(r'clientes', ClienteViewSet)
router.register(r'ventas', VentaViewSet)
router.register(r'venta_detalles', VentaDetalleViewSet)
router.register(r'pagos', PagoViewSet)
router.register(r'roles', RolViewSet)
router.register(r'usuarios', UsuarioViewSet)

urlpatterns = [
    # Endpoints de reportes (agregaciones)
    path('reportes/resumen/', ReporteResumen.as_view(), name='reporte-resumen'),
    path('reportes/ventas-por-dia/', VentasPorDia.as_view(), name='reporte-ventas-por-dia'),
    path('reportes/top-productos/', TopProductos.as_view(), name='reporte-top-productos'),
    path('reportes/mix-pago/', MixPago.as_view(), name='reporte-mix-pago'),
    path('reportes/stock-bajo/', StockBajo.as_view(), name='reporte-stock-bajo'),
    path('reportes/export/pdf/', ExportResumenPDF.as_view(), name='reporte-export-pdf'),
    path('reportes/export/excel/', ExportResumenExcel.as_view(), name='reporte-export-excel'),
    path('reportes/pronostico/', PronosticoVentas.as_view(), name='reporte-pronostico'),
    # POS
    path('ventas/pos_checkout/', POSCheckout.as_view(), name='pos-checkout'),
    path('ventas/online_checkout/', OnlineCheckout.as_view(), name='online-checkout'),
    path('ventas/confirmar_pago/', ConfirmarPagoVenta.as_view(), name='confirmar-pago'),
    # Auth simple basada en tokens
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
    path('auth/me/', MeView.as_view(), name='auth-me'),
    path('auth/bootstrap/', BootstrapView.as_view(), name='auth-bootstrap'),
    # Uploads (solo dev)
    path('upload/image/', UploadImageView.as_view(), name='upload-image'),
    # Router (al final para evitar que tome rutas como ventas/<pk>=pos_checkout)
    path('', include(router.urls)),
]
