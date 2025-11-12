import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sistema_boutique.settings")
django.setup()

from django.db import connections
from django.db.utils import OperationalError

db_conn = connections['default']
try:
    c = db_conn.cursor()
    c.execute("SELECT 1;")
    print("✅ Conexión exitosa a PostgreSQL")
except OperationalError as e:
    print("❌ Error de conexión:", e)
