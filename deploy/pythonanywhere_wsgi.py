# Contenido para el archivo WSGI de PythonAnywhere.
# En la pestaña "Web" de PythonAnywhere, editá el archivo
#   /var/www/mapacalor_pythonanywhere_com_wsgi.py
# y reemplazá TODO su contenido por esto (ajustando la SECRET_KEY).

import os
import sys

path = "/home/mapacalor/campa-a"
if path not in sys.path:
    sys.path.insert(0, path)

os.environ["DJANGO_SETTINGS_MODULE"] = "campana.settings"
os.environ["DJANGO_DEBUG"] = "False"
# Generá una clave con:
#   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
os.environ["DJANGO_SECRET_KEY"] = "PEGAR_AQUI_UNA_CLAVE_LARGA_Y_SECRETA"
os.environ["DJANGO_ALLOWED_HOSTS"] = "mapacalor.pythonanywhere.com"

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
