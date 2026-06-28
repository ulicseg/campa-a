# Despliegue en PythonAnywhere

Guía para publicar la app en `https://mapacalor.pythonanywhere.com`
(usuario `mapacalor`, proyecto en `/home/mapacalor/campa-a`).

La configuración de producción se controla por **variables de entorno**, que se
definen en el archivo WSGI (ver `deploy/pythonanywhere_wsgi.py`):

| Variable | Producción |
|---|---|
| `DJANGO_DEBUG` | `False` |
| `DJANGO_SECRET_KEY` | una clave larga y secreta (generada) |
| `DJANGO_ALLOWED_HOSTS` | `mapacalor.pythonanywhere.com` |

---

## 1. Subir el código (consola Bash de PythonAnywhere)

```bash
cd ~
git clone https://github.com/ulicseg/campa-a.git
```

Queda en `/home/mapacalor/campa-a`.

## 2. Crear el virtualenv e instalar dependencias

Django 6 requiere Python 3.12+.

```bash
mkvirtualenv --python=/usr/bin/python3.13 mapacalor
pip install -r /home/mapacalor/campa-a/requirements.txt
```

Anotá la ruta del virtualenv (suele ser `/home/mapacalor/.virtualenvs/mapacalor`).

## 3. Generar la SECRET_KEY

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Guardá el resultado para el paso 5.

## 4. Crear la Web App (pestaña "Web" del panel)

1. **Add a new web app** → **Manual configuration** → **Python 3.13**.
2. En **Virtualenv**, poné la ruta del paso 2:
   `/home/mapacalor/.virtualenvs/mapacalor`

## 5. Configurar el archivo WSGI

En la pestaña Web, link **WSGI configuration file**
(`/var/www/mapacalor_pythonanywhere_com_wsgi.py`): borrá todo y pegá el
contenido de `deploy/pythonanywhere_wsgi.py`, reemplazando
`PEGAR_AQUI_UNA_CLAVE_LARGA_Y_SECRETA` por la clave del paso 3.

## 6. Mapear los archivos estáticos (pestaña "Web" → Static files)

| URL | Directory |
|---|---|
| `/static/` | `/home/mapacalor/campa-a/staticfiles` |

## 7. Inicializar la base de datos y los datos (consola Bash)

```bash
cd /home/mapacalor/campa-a
export DJANGO_DEBUG=False
export DJANGO_ALLOWED_HOSTS=mapacalor.pythonanywhere.com
export DJANGO_SECRET_KEY="la-misma-clave-del-wsgi"

python manage.py migrate
python manage.py seed_parcelas          # carga las 64 parcelas
python manage.py collectstatic --noinput
python manage.py crear_jefe admin --password "ELEGI_UNA_CONTRASEÑA"
```

## 8. Recargar

En la pestaña Web, botón verde **Reload**. Entrá a
`https://mapacalor.pythonanywhere.com` y logueate con el jefe creado.
Desde "Encuestadores" creás las cuentas operativas.

---

## Actualizar el sitio (deploys posteriores)

```bash
cd /home/mapacalor/campa-a
git pull
workon mapacalor
pip install -r requirements.txt          # si cambiaron dependencias
python manage.py migrate                  # si hay migraciones nuevas
python manage.py collectstatic --noinput  # si cambiaron estáticos
```

Y **Reload** en la pestaña Web.

## Auditoría

Los accesos a datos sensibles (Ley 25.326) se registran en
`/home/mapacalor/campa-a/audit.log`.
