# Plataforma de Gestión Territorial y Encuestas — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Django web app for territorial canvassing and political surveys, with an interactive SVG heat map (Jefe de Campaña) and a restricted data-entry interface (Encuestador), legally hardened per Ley 25.326.

**Architecture:** Single Django project, four apps (`usuarios`, `territorio`, `encuestas`, `dashboard`). Personal data (`Familia`) and the sensitive vote (`Voto`) live in separate tables; analytics queries only touch `Voto`+`Parcela`. The heat map is server-rendered inline SVG (64 polygons parsed from `coordenadas.md`), colored by majority party and opacity by dominance. RBAC enforced via view mixins.

**Tech Stack:** Django (latest stable), SQLite, Chart.js (CDN), vanilla JS for map interaction. No DRF, no frontend build. Deploy: PythonAnywhere free tier.

## Global Constraints

- Database: **SQLite** (`db.sqlite3`), default Django config. No other DB engine.
- Vote choices, exact codes: `PJ`, `UCR`, `Otro`, `Indeciso`, `No contesta`.
- Heat-map colors: `PJ`→`#1f4e9c` (azul), `UCR`→`#c62828` (rojo), `Otro`→`#2e7d32` (verde), `Indeciso`→`#757575` (gris), `No contesta`→`#e0e0e0` (gris muy claro).
- Empty parcela (0 votes) → **transparent** (no fill).
- Opacity = dominance fraction (`max_count/total`), floored at `0.35`, rounded to 2 decimals.
- Tie-break for majority, fixed order: `PJ > UCR > Otro > Indeciso > No contesta`.
- Consent checkbox **exact text**: `"Confirmo que el vecino fue informado de que estos datos son para uso estadístico y de campaña"`. Validated server-side; record cannot save without it `True`.
- `Familia` + `Voto` always saved inside `transaction.atomic()`.
- Encuestador: only sees/loads/edits within assigned parcelas; edits/deletes only own records. Jefe: full access, can load in any parcela.
- Tests run with `python manage.py test`.
- Commit after every task (frequent commits).

---

## File Structure

```
campana/                     # Django project package
  settings.py                # SQLite, apps, templates, static, auth redirects
  urls.py                    # root URLconf
usuarios/
  models.py                  # PerfilUsuario (rol, parcelas M2M)
  mixins.py                  # JefeRequiredMixin, EncuestadorRequiredMixin
  views.py                   # login redirect, gestión de encuestadores
  forms.py                   # EncuestadorForm
  urls.py
territorio/
  models.py                  # Parcela (numero, coords, svg_points)
  management/commands/seed_parcelas.py
encuestas/
  models.py                  # Familia, Voto
  forms.py                   # FamiliaForm (consent + parcela queryset)
  services.py                # crear_relevamiento() atomic helper
  views.py                   # cargar, mis cargas, editar, borrar
  urls.py
dashboard/
  aggregation.py             # resumen_parcela(), color/opacity/majority
  kpis.py                    # calcular_kpis()
  views.py                   # dashboard, detalle nominal
  urls.py
templates/
  base.html, registration/login.html
  dashboard/dashboard.html, dashboard/_detalle.html
  encuestas/cargar.html, encuestas/mis_cargas.html
  usuarios/gestion.html
static/img/mapa_unidas.jpeg
```

---

### Task 1: Project scaffold & settings

**Files:**
- Create: `campana/settings.py`, `campana/urls.py`, `manage.py`, `requirements.txt`
- Create: `templates/base.html`
- Test: `core/tests/test_smoke.py`

**Interfaces:**
- Produces: a runnable Django project named `campana`; apps `usuarios`, `territorio`, `encuestas`, `dashboard` registered; `LOGIN_URL`, `LOGIN_REDIRECT_URL='/'`, templates dir and static dir configured.

- [ ] **Step 1: Create the project and apps**

```bash
python -m venv .venv && source .venv/Scripts/activate   # Windows Git Bash
pip install django
django-admin startproject campana .
python manage.py startapp usuarios
python manage.py startapp territorio
python manage.py startapp encuestas
python manage.py startapp dashboard
pip freeze > requirements.txt
```

- [ ] **Step 2: Register apps and configure settings**

In `campana/settings.py`, set `INSTALLED_APPS` to include `'usuarios'`, `'territorio'`, `'encuestas'`, `'dashboard'`. Add:

```python
TEMPLATES[0]["DIRS"] = [BASE_DIR / "templates"]
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
LANGUAGE_CODE = "es-ar"
TIME_ZONE = "America/Argentina/Cordoba"
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "login"
```

- [ ] **Step 3: Write the smoke test**

```python
# core/tests/test_smoke.py
from django.test import TestCase

class SmokeTest(TestCase):
    def test_settings_have_apps(self):
        from django.conf import settings
        for app in ["usuarios", "territorio", "encuestas", "dashboard"]:
            self.assertIn(app, settings.INSTALLED_APPS)
```

(Create empty `core/__init__.py` and `core/tests/__init__.py`.)

- [ ] **Step 4: Run the test**

Run: `python manage.py test core`
Expected: PASS (1 test).

- [ ] **Step 5: Create base template**

```html
<!-- templates/base.html -->
{% load static %}
<!doctype html><html lang="es"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{% block title %}Gestión Territorial{% endblock %}</title>
{% block head %}{% endblock %}
</head><body>{% block content %}{% endblock %}</body></html>
```

- [ ] **Step 6: Commit**

```bash
git init && git add -A
git commit -m "feat: scaffold Django project with four apps"
```

---

### Task 2: Parcela model

**Files:**
- Modify: `territorio/models.py`
- Test: `territorio/tests/test_models.py`

**Interfaces:**
- Produces: `Parcela(numero: int unique, coords: str)`, property `svg_points -> str` converting `"x1,y1,x2,y2"` into `"x1,y1 x2,y2"` for SVG `<polygon points>`.

- [ ] **Step 1: Write the failing test**

```python
# territorio/tests/test_models.py
from django.test import TestCase
from territorio.models import Parcela

class ParcelaModelTest(TestCase):
    def test_svg_points_groups_into_xy_pairs(self):
        p = Parcela(numero=1, coords="265,366,332,324,370,386")
        self.assertEqual(p.svg_points, "265,366 332,324 370,386")

    def test_numero_is_unique(self):
        Parcela.objects.create(numero=1, coords="1,2,3,4")
        with self.assertRaises(Exception):
            Parcela.objects.create(numero=1, coords="5,6,7,8")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python manage.py test territorio`
Expected: FAIL (`cannot import name 'Parcela'` or attribute error).

- [ ] **Step 3: Implement the model**

```python
# territorio/models.py
from django.db import models

class Parcela(models.Model):
    numero = models.PositiveIntegerField(unique=True)
    coords = models.TextField(help_text="Pares x,y separados por coma, del image map.")

    class Meta:
        ordering = ["numero"]

    def __str__(self):
        return f"Cuadra {self.numero}"

    @property
    def svg_points(self):
        nums = self.coords.split(",")
        pairs = [f"{nums[i]},{nums[i+1]}" for i in range(0, len(nums) - 1, 2)]
        return " ".join(pairs)
```

- [ ] **Step 4: Make migrations and run tests**

Run: `python manage.py makemigrations territorio && python manage.py test territorio`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: add Parcela model with svg_points"
```

---

### Task 3: seed_parcelas management command

**Files:**
- Create: `territorio/management/__init__.py`, `territorio/management/commands/__init__.py`, `territorio/management/commands/seed_parcelas.py`
- Move asset: `mapa unidas.jpeg` → `static/img/mapa_unidas.jpeg`; keep `coordenadas.md` at repo root.
- Test: `territorio/tests/test_seed.py`

**Interfaces:**
- Consumes: `Parcela` from Task 2; the `<area ... alt="N" ... coords="...">` lines in `coordenadas.md`.
- Produces: management command `seed_parcelas` creating exactly 64 `Parcela` rows (idempotent: `update_or_create` by `numero`).

- [ ] **Step 1: Write the failing test**

```python
# territorio/tests/test_seed.py
from django.test import TestCase
from django.core.management import call_command
from territorio.models import Parcela

class SeedParcelasTest(TestCase):
    def test_seed_creates_64_parcelas(self):
        call_command("seed_parcelas")
        self.assertEqual(Parcela.objects.count(), 64)
        self.assertTrue(Parcela.objects.filter(numero=1).exists())
        self.assertTrue(Parcela.objects.filter(numero=64).exists())

    def test_seed_is_idempotent(self):
        call_command("seed_parcelas")
        call_command("seed_parcelas")
        self.assertEqual(Parcela.objects.count(), 64)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python manage.py test territorio.tests.test_seed`
Expected: FAIL (`Unknown command: 'seed_parcelas'`).

- [ ] **Step 3: Implement the command**

```python
# territorio/management/commands/seed_parcelas.py
import re
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand
from territorio.models import Parcela

AREA_RE = re.compile(r'alt="(\d+)"[^>]*coords="([\d,]+)"')

class Command(BaseCommand):
    help = "Carga las 64 parcelas desde coordenadas.md (idempotente)."

    def handle(self, *args, **options):
        path = Path(settings.BASE_DIR) / "coordenadas.md"
        text = path.read_text(encoding="utf-8")
        count = 0
        for numero, coords in AREA_RE.findall(text):
            Parcela.objects.update_or_create(
                numero=int(numero), defaults={"coords": coords}
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f"{count} parcelas cargadas."))
```

- [ ] **Step 4: Run tests**

Run: `python manage.py test territorio`
Expected: PASS (all territorio tests).

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: seed_parcelas command parses coordenadas.md"
```

---

### Task 4: PerfilUsuario model

**Files:**
- Modify: `usuarios/models.py`
- Test: `usuarios/tests/test_models.py`

**Interfaces:**
- Consumes: `Parcela`, Django `User`.
- Produces: `PerfilUsuario(user: OneToOne, rol: "encuestador"|"jefe", parcelas: M2M[Parcela])`; constants `ROL_ENCUESTADOR="encuestador"`, `ROL_JEFE="jefe"`; helpers `user.perfil.es_jefe`, `user.perfil.es_encuestador`.

- [ ] **Step 1: Write the failing test**

```python
# usuarios/tests/test_models.py
from django.test import TestCase
from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario
from territorio.models import Parcela

class PerfilTest(TestCase):
    def test_perfil_roles_and_parcelas(self):
        u = User.objects.create_user("ana", password="x")
        p = Parcela.objects.create(numero=12, coords="1,2,3,4")
        perfil = PerfilUsuario.objects.create(user=u, rol=PerfilUsuario.ROL_ENCUESTADOR)
        perfil.parcelas.add(p)
        self.assertTrue(perfil.es_encuestador)
        self.assertFalse(perfil.es_jefe)
        self.assertIn(p, perfil.parcelas.all())
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python manage.py test usuarios`
Expected: FAIL (`cannot import name 'PerfilUsuario'`).

- [ ] **Step 3: Implement the model**

```python
# usuarios/models.py
from django.contrib.auth.models import User
from django.db import models
from territorio.models import Parcela

class PerfilUsuario(models.Model):
    ROL_ENCUESTADOR = "encuestador"
    ROL_JEFE = "jefe"
    ROLES = [(ROL_ENCUESTADOR, "Encuestador"), (ROL_JEFE, "Jefe de Campaña")]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    rol = models.CharField(max_length=20, choices=ROLES)
    parcelas = models.ManyToManyField(Parcela, blank=True, related_name="encuestadores")

    @property
    def es_jefe(self):
        return self.rol == self.ROL_JEFE

    @property
    def es_encuestador(self):
        return self.rol == self.ROL_ENCUESTADOR

    def __str__(self):
        return f"{self.user.username} ({self.get_rol_display()})"
```

- [ ] **Step 4: Migrate and run tests**

Run: `python manage.py makemigrations usuarios && python manage.py test usuarios`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: add PerfilUsuario with rol and parcelas"
```

---

### Task 5: Familia & Voto models + atomic service

**Files:**
- Modify: `encuestas/models.py`
- Create: `encuestas/services.py`
- Test: `encuestas/tests/test_models.py`

**Interfaces:**
- Consumes: `Parcela`, `User`.
- Produces:
  - `Familia(numero_familia, nombre_familia, integrantes:int, contacto_1='', contacto_2='', parcela:FK, cargada_por:FK User, fecha:auto, consentimiento_informado:bool=False)`.
  - `Voto(familia: OneToOne, intencion: choice)`; `Voto.INTENCIONES` list with codes `PJ/UCR/Otro/Indeciso/No contesta`.
  - `crear_relevamiento(*, datos_familia: dict, intencion: str, parcela, usuario) -> Familia` — wraps both writes in `transaction.atomic()`.

- [ ] **Step 1: Write the failing test**

```python
# encuestas/tests/test_models.py
from django.test import TestCase
from django.contrib.auth.models import User
from territorio.models import Parcela
from encuestas.models import Familia, Voto
from encuestas.services import crear_relevamiento

class RelevamientoTest(TestCase):
    def setUp(self):
        self.u = User.objects.create_user("ana", password="x")
        self.p = Parcela.objects.create(numero=12, coords="1,2,3,4")

    def test_crear_relevamiento_writes_both_tables(self):
        fam = crear_relevamiento(
            datos_familia={"numero_familia": "5", "nombre_familia": "Pérez",
                           "integrantes": 4, "consentimiento_informado": True},
            intencion="PJ", parcela=self.p, usuario=self.u,
        )
        self.assertEqual(Familia.objects.count(), 1)
        self.assertEqual(Voto.objects.count(), 1)
        self.assertEqual(fam.voto.intencion, "PJ")
        self.assertEqual(fam.cargada_por, self.u)

    def test_rollback_when_intencion_invalid(self):
        with self.assertRaises(Exception):
            crear_relevamiento(
                datos_familia={"numero_familia": "5", "nombre_familia": "Pérez",
                               "integrantes": 4, "consentimiento_informado": True},
                intencion="NO_EXISTE", parcela=self.p, usuario=self.u,
            )
        self.assertEqual(Familia.objects.count(), 0)
        self.assertEqual(Voto.objects.count(), 0)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python manage.py test encuestas`
Expected: FAIL (import error).

- [ ] **Step 3: Implement models**

```python
# encuestas/models.py
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from territorio.models import Parcela

class Familia(models.Model):
    numero_familia = models.CharField(max_length=20)
    nombre_familia = models.CharField(max_length=120)
    integrantes = models.PositiveIntegerField(default=1)
    contacto_1 = models.CharField(max_length=60, blank=True)
    contacto_2 = models.CharField(max_length=60, blank=True)
    parcela = models.ForeignKey(Parcela, on_delete=models.PROTECT, related_name="familias")
    cargada_por = models.ForeignKey(User, on_delete=models.PROTECT, related_name="familias_cargadas")
    fecha = models.DateTimeField(auto_now_add=True)
    consentimiento_informado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre_familia} (cuadra {self.parcela.numero})"

class Voto(models.Model):
    INTENCIONES = [("PJ", "PJ"), ("UCR", "UCR"), ("Otro", "Otro"),
                   ("Indeciso", "Indeciso"), ("No contesta", "No contesta")]
    familia = models.OneToOneField(Familia, on_delete=models.CASCADE, related_name="voto")
    intencion = models.CharField(max_length=20, choices=INTENCIONES)

    def clean(self):
        valid = {c for c, _ in self.INTENCIONES}
        if self.intencion not in valid:
            raise ValidationError({"intencion": "Intención inválida."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
```

- [ ] **Step 4: Implement the atomic service**

```python
# encuestas/services.py
from django.db import transaction
from encuestas.models import Familia, Voto

@transaction.atomic
def crear_relevamiento(*, datos_familia, intencion, parcela, usuario):
    familia = Familia.objects.create(parcela=parcela, cargada_por=usuario, **datos_familia)
    Voto.objects.create(familia=familia, intencion=intencion)
    return familia
```

- [ ] **Step 5: Migrate and run tests**

Run: `python manage.py makemigrations encuestas && python manage.py test encuestas`
Expected: PASS (2 tests, rollback verified).

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "feat: Familia/Voto models with atomic crear_relevamiento"
```

---

### Task 6: Auth, role mixins & role-based redirect

**Files:**
- Create: `usuarios/mixins.py`, `templates/registration/login.html`
- Modify: `usuarios/views.py`, `usuarios/urls.py`, `campana/urls.py`
- Test: `usuarios/tests/test_access.py`

**Interfaces:**
- Consumes: `PerfilUsuario`.
- Produces:
  - `JefeRequiredMixin`, `EncuestadorRequiredMixin` (LoginRequired + role check → 403 via `PermissionDenied`).
  - View `post_login_redirect` at name `home` (`/`): jefe → `dashboard`, encuestador → `cargar_familia`.
  - `login`/`logout` wired via `django.contrib.auth.urls`.

- [ ] **Step 1: Write the failing test**

```python
# usuarios/tests/test_access.py
from django.test import TestCase
from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario

def make_user(username, rol):
    u = User.objects.create_user(username, password="x")
    PerfilUsuario.objects.create(user=u, rol=rol)
    return u

class RedirectTest(TestCase):
    def test_jefe_redirected_to_dashboard(self):
        make_user("jefe", PerfilUsuario.ROL_JEFE)
        self.client.login(username="jefe", password="x")
        resp = self.client.get("/", follow=False)
        self.assertRedirects(resp, "/dashboard/", target_status_code=200)

    def test_encuestador_redirected_to_cargar(self):
        make_user("ana", PerfilUsuario.ROL_ENCUESTADOR)
        self.client.login(username="ana", password="x")
        resp = self.client.get("/", follow=False)
        self.assertRedirects(resp, "/encuestas/cargar/", target_status_code=200)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python manage.py test usuarios.tests.test_access`
Expected: FAIL (404 / no URL).

- [ ] **Step 3: Implement mixins**

```python
# usuarios/mixins.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

class _RolMixin(LoginRequiredMixin):
    rol_requerido = None
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        perfil = getattr(request.user, "perfil", None)
        if perfil is None or perfil.rol != self.rol_requerido:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class JefeRequiredMixin(_RolMixin):
    rol_requerido = "jefe"

class EncuestadorRequiredMixin(_RolMixin):
    rol_requerido = "encuestador"
```

- [ ] **Step 4: Implement redirect view and URLs**

```python
# usuarios/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View

class PostLoginRedirect(LoginRequiredMixin, View):
    def get(self, request):
        perfil = getattr(request.user, "perfil", None)
        if perfil and perfil.es_jefe:
            return redirect("dashboard")
        return redirect("cargar_familia")
```

```python
# campana/urls.py
from django.contrib import admin
from django.urls import path, include
from usuarios.views import PostLoginRedirect

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", PostLoginRedirect.as_view(), name="home"),
    path("encuestas/", include("encuestas.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("usuarios/", include("usuarios.urls")),
]
```

Create `templates/registration/login.html` extending `base.html` with a standard `{{ form }}` POST form. Create minimal `usuarios/urls.py` (empty `urlpatterns = []` for now, filled in Task 9). Create placeholder `encuestas/urls.py` and `dashboard/urls.py` with the names `cargar_familia` and `dashboard` pointing at `TemplateView`s temporarily so redirects resolve; they are replaced in later tasks.

- [ ] **Step 5: Run tests**

Run: `python manage.py test usuarios`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "feat: role mixins and post-login redirect"
```

---

### Task 7: Encuestador — cargar familia form & view

**Files:**
- Create: `encuestas/forms.py`, `templates/encuestas/cargar.html`
- Modify: `encuestas/views.py`, `encuestas/urls.py`
- Test: `encuestas/tests/test_cargar.py`

**Interfaces:**
- Consumes: `crear_relevamiento`, `EncuestadorRequiredMixin`, `PerfilUsuario.parcelas`.
- Produces: `FamiliaForm` (fields: numero_familia, nombre_familia, integrantes, contacto_1, contacto_2, parcela, intencion, consentimiento_informado) where `parcela` queryset is limited to the user's assigned parcelas and `consentimiento_informado` must be `True`. View name `cargar_familia` at `/encuestas/cargar/`.

- [ ] **Step 1: Write the failing tests**

```python
# encuestas/tests/test_cargar.py
from django.test import TestCase
from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario
from territorio.models import Parcela
from encuestas.models import Familia, Voto

class CargarTest(TestCase):
    def setUp(self):
        self.u = User.objects.create_user("ana", password="x")
        self.perfil = PerfilUsuario.objects.create(user=self.u, rol=PerfilUsuario.ROL_ENCUESTADOR)
        self.p_mia = Parcela.objects.create(numero=12, coords="1,2,3,4")
        self.p_ajena = Parcela.objects.create(numero=40, coords="1,2,3,4")
        self.perfil.parcelas.add(self.p_mia)
        self.client.login(username="ana", password="x")

    def _payload(self, **over):
        data = {"numero_familia": "5", "nombre_familia": "Pérez", "integrantes": 4,
                "contacto_1": "", "contacto_2": "", "parcela": self.p_mia.id,
                "intencion": "PJ", "consentimiento_informado": "on"}
        data.update(over); return data

    def test_saves_with_consent(self):
        resp = self.client.post("/encuestas/cargar/", self._payload())
        self.assertEqual(Familia.objects.count(), 1)
        self.assertEqual(Voto.objects.get().intencion, "PJ")

    def test_rejects_without_consent(self):
        data = self._payload(); data.pop("consentimiento_informado")
        self.client.post("/encuestas/cargar/", data)
        self.assertEqual(Familia.objects.count(), 0)

    def test_cannot_load_into_unassigned_parcela(self):
        self.client.post("/encuestas/cargar/", self._payload(parcela=self.p_ajena.id))
        self.assertEqual(Familia.objects.count(), 0)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python manage.py test encuestas.tests.test_cargar`
Expected: FAIL.

- [ ] **Step 3: Implement the form**

```python
# encuestas/forms.py
from django import forms
from encuestas.models import Familia, Voto

CONSENT_LABEL = ("Confirmo que el vecino fue informado de que estos datos "
                 "son para uso estadístico y de campaña")

class FamiliaForm(forms.Form):
    numero_familia = forms.CharField(max_length=20)
    nombre_familia = forms.CharField(max_length=120)
    integrantes = forms.IntegerField(min_value=1)
    contacto_1 = forms.CharField(max_length=60, required=False)
    contacto_2 = forms.CharField(max_length=60, required=False)
    parcela = forms.ModelChoiceField(queryset=None)
    intencion = forms.ChoiceField(choices=Voto.INTENCIONES)
    consentimiento_informado = forms.BooleanField(label=CONSENT_LABEL)  # required=True default

    def __init__(self, *args, parcelas_qs=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["parcela"].queryset = parcelas_qs
```

- [ ] **Step 4: Implement the view and URL**

```python
# encuestas/views.py
from django.shortcuts import render, redirect
from usuarios.mixins import EncuestadorRequiredMixin
from django.views import View
from encuestas.forms import FamiliaForm
from encuestas.services import crear_relevamiento

class CargarFamilia(EncuestadorRequiredMixin, View):
    def _parcelas(self, request):
        return request.user.perfil.parcelas.all()

    def get(self, request):
        form = FamiliaForm(parcelas_qs=self._parcelas(request))
        return render(request, "encuestas/cargar.html", {"form": form})

    def post(self, request):
        form = FamiliaForm(request.POST, parcelas_qs=self._parcelas(request))
        if form.is_valid():
            cd = form.cleaned_data
            crear_relevamiento(
                datos_familia={k: cd[k] for k in
                    ("numero_familia", "nombre_familia", "integrantes",
                     "contacto_1", "contacto_2", "consentimiento_informado")},
                intencion=cd["intencion"], parcela=cd["parcela"], usuario=request.user,
            )
            return redirect("mis_cargas")
        return render(request, "encuestas/cargar.html", {"form": form})
```

Replace the placeholder in `encuestas/urls.py`:

```python
from django.urls import path
from encuestas import views
urlpatterns = [
    path("cargar/", views.CargarFamilia.as_view(), name="cargar_familia"),
]
```

Create `templates/encuestas/cargar.html` extending `base.html`, rendering the form via POST with `{% csrf_token %}` and a submit button. (`mis_cargas` URL added in Task 8 — add a temporary placeholder name now if needed.)

- [ ] **Step 5: Run tests**

Run: `python manage.py test encuestas`
Expected: PASS (consent + assigned-parcela enforcement verified).

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "feat: encuestador cargar familia form with consent + parcela scoping"
```

---

### Task 8: Encuestador — Mis cargas list, edit & delete (own only)

**Files:**
- Modify: `encuestas/views.py`, `encuestas/urls.py`
- Create: `templates/encuestas/mis_cargas.html`
- Test: `encuestas/tests/test_mis_cargas.py`

**Interfaces:**
- Consumes: `Familia`, `EncuestadorRequiredMixin`, `FamiliaForm`.
- Produces: views `mis_cargas` (`/encuestas/mias/`), `editar_familia` (`/encuestas/<pk>/editar/`), `borrar_familia` (`/encuestas/<pk>/borrar/`). Edit/delete raise 404 if the `Familia` was not `cargada_por` the current user.

- [ ] **Step 1: Write the failing tests**

```python
# encuestas/tests/test_mis_cargas.py
from django.test import TestCase
from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario
from territorio.models import Parcela
from encuestas.services import crear_relevamiento
from encuestas.models import Familia

class MisCargasTest(TestCase):
    def setUp(self):
        self.p = Parcela.objects.create(numero=12, coords="1,2,3,4")
        self.ana = User.objects.create_user("ana", password="x")
        PerfilUsuario.objects.create(user=self.ana, rol="encuestador").parcelas.add(self.p)
        self.beto = User.objects.create_user("beto", password="x")
        PerfilUsuario.objects.create(user=self.beto, rol="encuestador").parcelas.add(self.p)

    def _fam(self, user):
        return crear_relevamiento(
            datos_familia={"numero_familia": "1", "nombre_familia": "X",
                           "integrantes": 2, "consentimiento_informado": True},
            intencion="PJ", parcela=self.p, usuario=user)

    def test_list_shows_only_own(self):
        self._fam(self.ana); self._fam(self.beto)
        self.client.login(username="ana", password="x")
        resp = self.client.get("/encuestas/mias/")
        self.assertEqual(len(resp.context["familias"]), 1)

    def test_cannot_delete_others(self):
        fam = self._fam(self.beto)
        self.client.login(username="ana", password="x")
        resp = self.client.post(f"/encuestas/{fam.pk}/borrar/")
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(Familia.objects.filter(pk=fam.pk).exists())
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python manage.py test encuestas.tests.test_mis_cargas`
Expected: FAIL.

- [ ] **Step 3: Implement the views**

```python
# add to encuestas/views.py
from django.shortcuts import get_object_or_404
from encuestas.models import Familia, Voto

class MisCargas(EncuestadorRequiredMixin, View):
    def get(self, request):
        familias = (Familia.objects.filter(cargada_por=request.user)
                    .select_related("parcela", "voto").order_by("-fecha"))
        return render(request, "encuestas/mis_cargas.html", {"familias": familias})

class BorrarFamilia(EncuestadorRequiredMixin, View):
    def post(self, request, pk):
        fam = get_object_or_404(Familia, pk=pk, cargada_por=request.user)
        fam.delete()
        return redirect("mis_cargas")

class EditarFamilia(EncuestadorRequiredMixin, View):
    def _get(self, request, pk):
        return get_object_or_404(Familia, pk=pk, cargada_por=request.user)

    def get(self, request, pk):
        fam = self._get(request, pk)
        form = FamiliaForm(parcelas_qs=request.user.perfil.parcelas.all(), initial={
            "numero_familia": fam.numero_familia, "nombre_familia": fam.nombre_familia,
            "integrantes": fam.integrantes, "contacto_1": fam.contacto_1,
            "contacto_2": fam.contacto_2, "parcela": fam.parcela_id,
            "intencion": fam.voto.intencion, "consentimiento_informado": True})
        return render(request, "encuestas/cargar.html", {"form": form, "editar": True})

    def post(self, request, pk):
        fam = self._get(request, pk)
        form = FamiliaForm(request.POST, parcelas_qs=request.user.perfil.parcelas.all())
        if form.is_valid():
            cd = form.cleaned_data
            for f in ("numero_familia", "nombre_familia", "integrantes",
                      "contacto_1", "contacto_2", "consentimiento_informado"):
                setattr(fam, f, cd[f])
            fam.parcela = cd["parcela"]; fam.save()
            Voto.objects.update_or_create(familia=fam, defaults={"intencion": cd["intencion"]})
            return redirect("mis_cargas")
        return render(request, "encuestas/cargar.html", {"form": form, "editar": True})
```

Add to `encuestas/urls.py`:

```python
path("mias/", views.MisCargas.as_view(), name="mis_cargas"),
path("<int:pk>/editar/", views.EditarFamilia.as_view(), name="editar_familia"),
path("<int:pk>/borrar/", views.BorrarFamilia.as_view(), name="borrar_familia"),
```

Create `templates/encuestas/mis_cargas.html` listing `familias` (nombre, parcela, voto, fecha) with edit/delete (POST) buttons.

- [ ] **Step 4: Run tests**

Run: `python manage.py test encuestas`
Expected: PASS (own-only enforced; others → 404).

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: mis cargas list with own-only edit/delete"
```

---

### Task 9: Jefe — Gestión de encuestadores

**Files:**
- Modify: `usuarios/views.py`, `usuarios/urls.py`, `usuarios/forms.py` (create)
- Create: `templates/usuarios/gestion.html`
- Test: `usuarios/tests/test_gestion.py`

**Interfaces:**
- Consumes: `JefeRequiredMixin`, `PerfilUsuario`, `Parcela`.
- Produces: view `gestion_encuestadores` (`/usuarios/encuestadores/`) listing encuestadores and a form to create one (username, password, parcelas multi-select) creating `User` + `PerfilUsuario(rol=encuestador)` with assigned parcelas. Encuestadores get 403 here.

- [ ] **Step 1: Write the failing tests**

```python
# usuarios/tests/test_gestion.py
from django.test import TestCase
from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario
from territorio.models import Parcela

class GestionTest(TestCase):
    def setUp(self):
        self.p = Parcela.objects.create(numero=12, coords="1,2,3,4")
        self.jefe = User.objects.create_user("jefe", password="x")
        PerfilUsuario.objects.create(user=self.jefe, rol="jefe")

    def test_encuestador_gets_403(self):
        u = User.objects.create_user("ana", password="x")
        PerfilUsuario.objects.create(user=u, rol="encuestador")
        self.client.login(username="ana", password="x")
        self.assertEqual(self.client.get("/usuarios/encuestadores/").status_code, 403)

    def test_jefe_creates_encuestador_with_parcela(self):
        self.client.login(username="jefe", password="x")
        resp = self.client.post("/usuarios/encuestadores/", {
            "username": "nuevo", "password": "secreta123", "parcelas": [self.p.id]})
        nuevo = User.objects.get(username="nuevo")
        self.assertTrue(nuevo.perfil.es_encuestador)
        self.assertIn(self.p, nuevo.perfil.parcelas.all())
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python manage.py test usuarios.tests.test_gestion`
Expected: FAIL.

- [ ] **Step 3: Implement form**

```python
# usuarios/forms.py
from django import forms
from territorio.models import Parcela

class EncuestadorForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    parcelas = forms.ModelMultipleChoiceField(
        queryset=Parcela.objects.all(), widget=forms.CheckboxSelectMultiple)
```

- [ ] **Step 4: Implement view & URL**

```python
# add to usuarios/views.py
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from usuarios.mixins import JefeRequiredMixin
from usuarios.models import PerfilUsuario
from usuarios.forms import EncuestadorForm

class GestionEncuestadores(JefeRequiredMixin, View):
    def get(self, request):
        return render(request, "usuarios/gestion.html", {
            "form": EncuestadorForm(),
            "encuestadores": PerfilUsuario.objects.filter(rol="encuestador").select_related("user")})

    def post(self, request):
        form = EncuestadorForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = User.objects.create_user(cd["username"], password=cd["password"])
            perfil = PerfilUsuario.objects.create(user=user, rol="encuestador")
            perfil.parcelas.set(cd["parcelas"])
            return redirect("gestion_encuestadores")
        return render(request, "usuarios/gestion.html", {
            "form": form,
            "encuestadores": PerfilUsuario.objects.filter(rol="encuestador").select_related("user")})
```

```python
# usuarios/urls.py
from django.urls import path
from usuarios.views import GestionEncuestadores
urlpatterns = [
    path("encuestadores/", GestionEncuestadores.as_view(), name="gestion_encuestadores"),
]
```

Create `templates/usuarios/gestion.html` with the create form and the list of existing encuestadores + their parcelas.

- [ ] **Step 5: Run tests**

Run: `python manage.py test usuarios`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "feat: jefe gestión de encuestadores screen"
```

---

### Task 10: Heat-map aggregation (pure logic)

**Files:**
- Create: `dashboard/aggregation.py`
- Test: `dashboard/tests/test_aggregation.py`

**Interfaces:**
- Consumes: `Voto`, `Parcela`.
- Produces: `resumen_parcela(parcela) -> dict` with keys `numero, total, mayoria (code|None), color (hex|None), opacidad (float), porcentaje (int)`. Constants `COLORES: dict[str,str]`, `ORDEN_DESEMPATE: list[str]`. Empty parcela → `mayoria=None, color=None, opacidad=0`.

- [ ] **Step 1: Write the failing tests**

```python
# dashboard/tests/test_aggregation.py
from django.test import TestCase
from django.contrib.auth.models import User
from territorio.models import Parcela
from encuestas.services import crear_relevamiento
from dashboard.aggregation import resumen_parcela, COLORES

class AggregationTest(TestCase):
    def setUp(self):
        self.u = User.objects.create_user("ana", password="x")
        self.p = Parcela.objects.create(numero=12, coords="1,2,3,4")

    def _voto(self, intencion, n=1):
        for _ in range(n):
            crear_relevamiento(
                datos_familia={"numero_familia": "1", "nombre_familia": "X",
                               "integrantes": 1, "consentimiento_informado": True},
                intencion=intencion, parcela=self.p, usuario=self.u)

    def test_empty_parcela_is_transparent(self):
        r = resumen_parcela(self.p)
        self.assertEqual(r["total"], 0)
        self.assertIsNone(r["mayoria"]); self.assertIsNone(r["color"]); self.assertEqual(r["opacidad"], 0)

    def test_majority_color_and_opacity(self):
        self._voto("PJ", 8); self._voto("UCR", 2)
        r = resumen_parcela(self.p)
        self.assertEqual(r["mayoria"], "PJ")
        self.assertEqual(r["color"], COLORES["PJ"])
        self.assertEqual(r["porcentaje"], 80)
        self.assertEqual(r["opacidad"], 0.8)

    def test_opacity_floor_is_035(self):
        self._voto("PJ", 1); self._voto("UCR", 1); self._voto("Otro", 1)
        r = resumen_parcela(self.p)  # PJ wins tie at 1/3 ≈ 0.33 -> floored
        self.assertEqual(r["opacidad"], 0.35)

    def test_tie_break_order_pj_over_ucr(self):
        self._voto("UCR", 2); self._voto("PJ", 2)
        self.assertEqual(resumen_parcela(self.p)["mayoria"], "PJ")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python manage.py test dashboard.tests.test_aggregation`
Expected: FAIL (import error).

- [ ] **Step 3: Implement aggregation**

```python
# dashboard/aggregation.py
from django.db.models import Count
from encuestas.models import Voto

COLORES = {"PJ": "#1f4e9c", "UCR": "#c62828", "Otro": "#2e7d32",
           "Indeciso": "#757575", "No contesta": "#e0e0e0"}
ORDEN_DESEMPATE = ["PJ", "UCR", "Otro", "Indeciso", "No contesta"]

def resumen_parcela(parcela):
    counts = {row["intencion"]: row["n"] for row in
              Voto.objects.filter(familia__parcela=parcela)
              .values("intencion").annotate(n=Count("id"))}
    total = sum(counts.values())
    if total == 0:
        return {"numero": parcela.numero, "total": 0, "mayoria": None,
                "color": None, "opacidad": 0, "porcentaje": 0}
    max_n = max(counts.values())
    mayoria = next(c for c in ORDEN_DESEMPATE if counts.get(c, 0) == max_n)
    frac = max_n / total
    return {"numero": parcela.numero, "total": total, "mayoria": mayoria,
            "color": COLORES[mayoria], "opacidad": round(max(0.35, frac), 2),
            "porcentaje": round(frac * 100)}
```

- [ ] **Step 4: Run tests**

Run: `python manage.py test dashboard.tests.test_aggregation`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: heat-map aggregation logic with tie-break and opacity floor"
```

---

### Task 11: Dashboard view & SVG map render

**Files:**
- Modify: `dashboard/views.py`, `dashboard/urls.py`
- Create: `templates/dashboard/dashboard.html`
- Test: `dashboard/tests/test_dashboard.py`

**Interfaces:**
- Consumes: `JefeRequiredMixin`, `resumen_parcela`, `Parcela.svg_points`.
- Produces: view `dashboard` (`/dashboard/`). Context `parcelas_resumen`: list of `{parcela, resumen}` for all 64. Template renders `<img>` of `static/img/mapa_unidas.jpeg` with an overlaid `<svg>` of `<polygon>`s using `svg_points`, `fill`, `fill-opacity`. Encuestador → 403.

- [ ] **Step 1: Write the failing tests**

```python
# dashboard/tests/test_dashboard.py
from django.test import TestCase
from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario
from territorio.models import Parcela
from encuestas.services import crear_relevamiento

class DashboardTest(TestCase):
    def setUp(self):
        Parcela.objects.create(numero=12, coords="10,20,30,40,50,60")
        self.jefe = User.objects.create_user("jefe", password="x")
        PerfilUsuario.objects.create(user=self.jefe, rol="jefe")

    def test_encuestador_gets_403(self):
        u = User.objects.create_user("ana", password="x")
        PerfilUsuario.objects.create(user=u, rol="encuestador")
        self.client.login(username="ana", password="x")
        self.assertEqual(self.client.get("/dashboard/").status_code, 403)

    def test_jefe_sees_polygon_points(self):
        self.client.login(username="jefe", password="x")
        resp = self.client.get("/dashboard/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "10,20 30,40 50,60")
        self.assertContains(resp, "<polygon")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python manage.py test dashboard.tests.test_dashboard`
Expected: FAIL.

- [ ] **Step 3: Implement the view & URL**

```python
# dashboard/views.py
from django.shortcuts import render
from django.views import View
from usuarios.mixins import JefeRequiredMixin
from territorio.models import Parcela
from dashboard.aggregation import resumen_parcela, COLORES

class Dashboard(JefeRequiredMixin, View):
    def get(self, request):
        datos = [{"parcela": p, "resumen": resumen_parcela(p)}
                 for p in Parcela.objects.all()]
        return render(request, "dashboard/dashboard.html",
                      {"parcelas_resumen": datos, "colores": COLORES})
```

Replace the placeholder `dashboard/urls.py`:

```python
from django.urls import path
from dashboard import views
urlpatterns = [
    path("", views.Dashboard.as_view(), name="dashboard"),
]
```

`templates/dashboard/dashboard.html` (extends base) renders inside a positioned container:

```html
{% load static %}
<div style="position:relative;display:inline-block">
  <img src="{% static 'img/mapa_unidas.jpeg' %}" alt="Mapa">
  <svg viewBox="0 0 1024 700" style="position:absolute;top:0;left:0;width:100%;height:100%">
    {% for item in parcelas_resumen %}
    <polygon points="{{ item.parcela.svg_points }}"
      data-numero="{{ item.parcela.numero }}"
      fill="{% if item.resumen.color %}{{ item.resumen.color }}{% else %}none{% endif %}"
      fill-opacity="{{ item.resumen.opacidad }}"
      stroke="#333" stroke-width="1" style="cursor:pointer"/>
    {% endfor %}
  </svg>
</div>
<div id="detalle"></div>
```

(Confirm the `viewBox` matches the JPEG's pixel dimensions; adjust width/height to the real image size.)

- [ ] **Step 4: Run tests**

Run: `python manage.py test dashboard`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: dashboard SVG heat-map render"
```

---

### Task 12: Detalle nominal endpoint (the JOIN)

**Files:**
- Modify: `dashboard/views.py`, `dashboard/urls.py`
- Create: `templates/dashboard/_detalle.html`
- Modify: `templates/dashboard/dashboard.html` (add click JS)
- Test: `dashboard/tests/test_detalle.py`

**Interfaces:**
- Consumes: `JefeRequiredMixin`, `Familia`.
- Produces: view `detalle_parcela` (`/dashboard/parcela/<numero>/detalle/`) returning an HTML fragment listing each `Familia` of that parcela with nombre, contactos, voto, cargada_por. Encuestador → 403. This is the only place `Familia`+`Voto` are joined for display.

- [ ] **Step 1: Write the failing tests**

```python
# dashboard/tests/test_detalle.py
from django.test import TestCase
from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario
from territorio.models import Parcela
from encuestas.services import crear_relevamiento

class DetalleTest(TestCase):
    def setUp(self):
        self.p = Parcela.objects.create(numero=12, coords="1,2,3,4")
        self.jefe = User.objects.create_user("jefe", password="x")
        PerfilUsuario.objects.create(user=self.jefe, rol="jefe")
        crear_relevamiento(
            datos_familia={"numero_familia": "1", "nombre_familia": "Pérez",
                           "integrantes": 3, "contacto_1": "3624-111",
                           "consentimiento_informado": True},
            intencion="PJ", parcela=self.p, usuario=self.jefe)

    def test_detalle_shows_nominal_join(self):
        self.client.login(username="jefe", password="x")
        resp = self.client.get("/dashboard/parcela/12/detalle/")
        self.assertContains(resp, "Pérez")
        self.assertContains(resp, "3624-111")
        self.assertContains(resp, "PJ")

    def test_encuestador_gets_403(self):
        u = User.objects.create_user("ana", password="x")
        PerfilUsuario.objects.create(user=u, rol="encuestador")
        self.client.login(username="ana", password="x")
        self.assertEqual(self.client.get("/dashboard/parcela/12/detalle/").status_code, 403)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python manage.py test dashboard.tests.test_detalle`
Expected: FAIL.

- [ ] **Step 3: Implement view, URL, template, JS**

```python
# add to dashboard/views.py
from django.shortcuts import get_object_or_404
from encuestas.models import Familia

class DetalleParcela(JefeRequiredMixin, View):
    def get(self, request, numero):
        parcela = get_object_or_404(Parcela, numero=numero)
        familias = (Familia.objects.filter(parcela=parcela)
                    .select_related("voto", "cargada_por").order_by("nombre_familia"))
        return render(request, "dashboard/_detalle.html",
                      {"parcela": parcela, "familias": familias})
```

Add to `dashboard/urls.py`:

```python
path("parcela/<int:numero>/detalle/", views.DetalleParcela.as_view(), name="detalle_parcela"),
```

`templates/dashboard/_detalle.html`: a table over `familias` showing `nombre_familia`, `numero_familia`, `integrantes`, `contacto_1`, `contacto_2`, `voto.get_intencion_display`, `cargada_por.username`.

Append to `dashboard.html` `{% block head %}`/script: click handler that `fetch`es the detalle URL and injects into `#detalle`:

```html
<script>
document.querySelectorAll('polygon[data-numero]').forEach(el =>
  el.addEventListener('click', async () => {
    const r = await fetch(`/dashboard/parcela/${el.dataset.numero}/detalle/`);
    document.getElementById('detalle').innerHTML = await r.text();
  }));
</script>
```

- [ ] **Step 4: Run tests**

Run: `python manage.py test dashboard`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: detalle nominal endpoint (Familia+Voto join) for jefe"
```

---

### Task 13: KPI panel

**Files:**
- Create: `dashboard/kpis.py`
- Modify: `dashboard/views.py` (add KPIs to Dashboard context), `templates/dashboard/dashboard.html` (Chart.js panel)
- Test: `dashboard/tests/test_kpis.py`

**Interfaces:**
- Consumes: `Familia`, `Voto`, `Parcela`, `resumen_parcela`.
- Produces: `calcular_kpis() -> dict` with keys `total_familias, total_personas, parcelas_relevadas, total_parcelas, distribucion (dict code->count), cuadras_indecisas (int)`. Rendered with Chart.js (CDN) for the distribution chart.

- [ ] **Step 1: Write the failing tests**

```python
# dashboard/tests/test_kpis.py
from django.test import TestCase
from django.contrib.auth.models import User
from territorio.models import Parcela
from encuestas.services import crear_relevamiento
from dashboard.kpis import calcular_kpis

class KpisTest(TestCase):
    def setUp(self):
        self.u = User.objects.create_user("ana", password="x")
        self.p1 = Parcela.objects.create(numero=1, coords="1,2,3,4")
        self.p2 = Parcela.objects.create(numero=2, coords="1,2,3,4")

    def _voto(self, parcela, intencion, integrantes=2):
        crear_relevamiento(
            datos_familia={"numero_familia": "1", "nombre_familia": "X",
                           "integrantes": integrantes, "consentimiento_informado": True},
            intencion=intencion, parcela=parcela, usuario=self.u)

    def test_kpis_totals_and_coverage(self):
        self._voto(self.p1, "PJ", 3); self._voto(self.p1, "UCR", 2)
        k = calcular_kpis()
        self.assertEqual(k["total_familias"], 2)
        self.assertEqual(k["total_personas"], 5)
        self.assertEqual(k["parcelas_relevadas"], 1)
        self.assertEqual(k["total_parcelas"], 2)
        self.assertEqual(k["distribucion"]["PJ"], 1)

    def test_cuadras_indecisas_counts_majority_indeciso(self):
        self._voto(self.p2, "Indeciso")
        self.assertEqual(calcular_kpis()["cuadras_indecisas"], 1)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python manage.py test dashboard.tests.test_kpis`
Expected: FAIL.

- [ ] **Step 3: Implement KPIs**

```python
# dashboard/kpis.py
from django.db.models import Count, Sum
from territorio.models import Parcela
from encuestas.models import Familia, Voto
from dashboard.aggregation import resumen_parcela, ORDEN_DESEMPATE

def calcular_kpis():
    distribucion = {c: 0 for c in ORDEN_DESEMPATE}
    for row in Voto.objects.values("intencion").annotate(n=Count("id")):
        distribucion[row["intencion"]] = row["n"]
    parcelas = list(Parcela.objects.all())
    relevadas = sum(1 for p in parcelas if resumen_parcela(p)["total"] > 0)
    indecisas = sum(1 for p in parcelas if resumen_parcela(p)["mayoria"] == "Indeciso")
    return {
        "total_familias": Familia.objects.count(),
        "total_personas": Familia.objects.aggregate(s=Sum("integrantes"))["s"] or 0,
        "parcelas_relevadas": relevadas,
        "total_parcelas": len(parcelas),
        "distribucion": distribucion,
        "cuadras_indecisas": indecisas,
    }
```

- [ ] **Step 4: Wire into Dashboard view & template**

In `dashboard/views.py` `Dashboard.get`, add `"kpis": calcular_kpis()` to context (import `from dashboard.kpis import calcular_kpis`). In `dashboard.html`, add a KPI panel below the map showing the totals and a Chart.js `<canvas>` fed by `{{ kpis.distribucion|json_script:"dist-data" }}`, loading Chart.js from CDN in `{% block head %}`.

- [ ] **Step 5: Run tests**

Run: `python manage.py test`
Expected: PASS (full suite green).

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "feat: KPI panel with Chart.js distribution"
```

---

## Self-Review

**Spec coverage:**
- Two-table dissociation → Task 5; analytics touch only Voto/Parcela → Tasks 10–11; JOIN only in detalle → Task 12. ✓
- RBAC mixins + 403 → Task 6; enforced in Tasks 9, 11, 12; encuestador scoping → Tasks 7, 8. ✓
- Consent checkbox exact text + backend validation → Task 7 (`CONSENT_LABEL`, `BooleanField` required). ✓
- Closed choices (intención, parcela) → Tasks 5, 7. ✓
- Atomic save → Task 5. ✓
- Map color/opacity/tie-break/empty → Task 10; SVG render → Task 11; interaction → Task 12. ✓
- KPI set (totals, personas, cobertura, distribución, indecisas) → Task 13. (Ranking de cuadras del partido propio is deferred — see gap below.) 
- seed_parcelas from coordenadas.md → Task 3. ✓
- SQLite, PythonAnywhere, Spanish locale → Task 1. ✓

**Gap found & resolved:** the spec's KPI "ranking de cuadras más fuertes para el partido propio" requires a configurable "partido propio", which was never specified. Deferred from Task 13 (kept out of scope to avoid an unspecified config); flag to the user during execution if they want it — it's an additive query over `resumen_parcela`, no schema change.

**Placeholder scan:** no TBD/TODO; all code steps contain runnable code. The only deliberately-deferred template details (full HTML/CSS styling) are described with exact context variables and the required output (tested via `assertContains`).

**Type consistency:** `crear_relevamiento(*, datos_familia, intencion, parcela, usuario)` used identically in Tasks 7, 8, 10, 12, 13. `resumen_parcela` dict keys (`total/mayoria/color/opacidad/porcentaje/numero`) consistent across Tasks 10, 11, 13. `COLORES`/`ORDEN_DESEMPATE` defined once (Task 10), imported elsewhere. Mixin names `JefeRequiredMixin`/`EncuestadorRequiredMixin` consistent.

## Notes for the implementer

- The JPEG real pixel size must set the SVG `viewBox` (Task 11). Inspect `static/img/mapa_unidas.jpeg` dimensions before finalizing the template; the `<area>` coords in `coordenadas.md` are in that image's pixel space.
- After Task 1, create a superuser and a Jefe `PerfilUsuario` manually (`python manage.py createsuperuser`, then set perfil via shell) to exercise the dashboard during development.
- Run `python manage.py seed_parcelas` once locally and on the server after deploy.
