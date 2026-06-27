# Diseño — Plataforma de Gestión Territorial y Encuestas Políticas

- **Fecha:** 2026-06-27
- **Localidad:** Colonias Unidas, Chaco, Argentina
- **Estado:** Diseño aprobado, listo para plan de implementación
- **Marco legal:** Ley 25.326 (Protección de Datos Personales, Argentina) — la intención de voto es **dato sensible**

## 1. Objetivo

Plataforma web para gestionar relevamientos territoriales y encuestas políticas casa por casa. El núcleo analítico es un **mapa de calor interactivo** que muestra la intención de voto parcela por parcela (las 64 cuadras del mapa de la localidad), acompañado de un panel de KPIs. El acceso está separado en dos roles con interfaces totalmente distintas.

## 2. Decisiones tomadas (resumen del brainstorming)

| Tema | Decisión |
|---|---|
| Unidad de datos | La **familia/hogar**. Una intención de voto por familia. |
| `integrantes` | Un número (cantidad de personas en la familia). |
| Intención de voto | Desplegable cerrado: **PJ / UCR / Otro / Indeciso / No contesta**. |
| Preocupación principal / reclamos | **Descartado** (no existe en las planillas reales). |
| Vínculo encuesta↔parcela | El encuestador **elige** la parcela de un desplegable con **solo sus parcelas asignadas**. |
| Edición por encuestador | Puede agregar y **editar/borrar solo lo que él cargó** (no toca lo ajeno). |
| Gestión de usuarios | **Pantalla propia** dentro del dashboard del Jefe (no Django Admin). |
| Mapa: color | Partido mayoritario en la cuadra. PJ→azul, UCR→rojo, Otro→verde, Indeciso→gris. |
| Mapa: opacidad | **Dominancia** (% del partido ganador en la cuadra). |
| Mapa: parcela sin encuestas | **Transparente** (se ve solo la imagen de fondo). |
| Render del mapa | **SVG inline generado por Django** (Enfoque A). Leaflet es el plan B si hace falta. |
| Base de datos | **SQLite**. |
| Despliegue | **PythonAnywhere, free tier**. |
| Escala | Pocos encuestadores, volumen bajo. |

## 3. Roles

### Encuestador (operativo)
- **NO tiene acceso al mapa ni a KPIs.**
- `Cargar familia`: formulario con nombre y n° de familia, integrantes, contactos (opcionales), desplegable de parcela (solo asignadas), desplegable de intención de voto, y checkbox de consentimiento obligatorio.
- `Mis cargas`: lista de las familias que **él** cargó, con editar/borrar **solo sobre las propias**. Sin cruces masivos, sin KPIs, sin mapa.
- Intentar acceder a vistas del Jefe o a parcelas no asignadas → **403**.

### Jefe de Campaña (administrador y analista)
- Acceso total.
- `Dashboard`: mapa de calor + panel de KPIs.
- `Detalle nominal de parcela`: al clickear una cuadra, la lista de familias de esa parcela con voto, contacto y quién la cargó. **Único punto donde ocurre el JOIN `Familia`+`Voto`.**
- `Gestión de encuestadores`: pantalla propia para crear/editar encuestadores y asignarles parcelas.
- Puede cargar familias en **cualquier** parcela (sin restricción de asignación) y editar/borrar cualquier familia.

## 4. Arquitectura

### Apps de Django
- `usuarios` — perfil de rol y asignación de parcelas.
- `territorio` — las 64 parcelas (datos fijos del mapa).
- `encuestas` — carga de relevamientos; aquí vive la disociación.
- `dashboard` — mapa de calor + KPIs (solo Jefe).

### Modelo de datos

La separación **identidad ↔ voto** en dos tablas es el mecanismo estructural de disociación que exige la Ley 25.326.

```
Parcela                  (territorio)
  numero        entero 1–64 (único)
  coords        texto de coordenadas.md (pares x,y del polígono)

PerfilUsuario            (usuarios)  — extiende User de Django (OneToOne)
  user          OneToOne -> User
  rol           "encuestador" | "jefe"
  parcelas      ManyToMany -> Parcela   (aplica solo a encuestadores)

Familia                  (encuestas)  ← DATOS IDENTIFICATORIOS
  numero_familia
  nombre_familia
  integrantes               entero (cantidad)
  contacto_1                opcional
  contacto_2                opcional
  parcela                   FK -> Parcela
  cargada_por               FK -> User
  fecha                     auto al crear
  consentimiento_informado  Booleano (checkbox legal, debe ser True)

Voto                     (encuestas)  ← DATO SENSIBLE, tabla separada
  familia       OneToOne -> Familia
  intencion     "PJ" | "UCR" | "Otro" | "Indeciso" | "No contesta"
```

**Por qué dos tablas:** los datos personales (nombre, contactos) viven en `Familia`; la ideología política vive en `Voto`. El mapa y los KPIs consultan **solo `Voto` + `Parcela`**, nunca datos personales. El JOIN ocurre exclusivamente en "Detalle nominal" del Jefe.

### Stack
- Django (último estable) + SQLite.
- `mapa unidas.jpeg` como archivo estático.
- KPIs con **Chart.js** vía CDN (sin build de frontend).
- Mapa con templates de Django (SVG inline). JavaScript propio mínimo: `fetch` del detalle y hover.
- **Sin Django REST Framework**: los endpoints de detalle devuelven HTML parcial o JSON simple desde vistas normales.

## 5. Lógica del mapa de calor (Enfoque A — SVG)

**Servidor:** una función de agregación recorre las 64 parcelas y, por cada una, consulta solo `Voto`:
- Cuenta votos por opción → determina el **partido mayoritario** (color) y su **% de dominancia** (opacidad, ej. rango 0.35–1.0).
- Colores: PJ→azul, UCR→rojo, Otro→verde, Indeciso→gris.
- **Parcela sin votos → transparente** (sin `fill`).
- **Desempate determinista:** ante empate de mayoría, gana por orden fijo PJ > UCR > Otro > Indeciso (regla estable para que el color no cambie entre renders).

**Plantilla:** `<svg>` superpuesto a `mapa unidas.jpeg`. Cada `<polygon>` usa los `points` parseados de `coords` y el `fill`/`fill-opacity` calculados. El SVG dibuja sin problema los polígonos con muchos puntos y cóncavos (parcelas 11, 55, 57…).

**Interacción:** click en polígono → `fetch` a `/parcela/<numero>/detalle/` → panel lateral/modal con el detalle nominal. Hover → resalta la cuadra y muestra tooltip "Cuadra N — mayoría X (NN%) — M familias".

## 6. Panel de KPIs (Jefe)

- **Total de familias relevadas** y total de personas (suma de `integrantes`).
- **Cobertura**: cuántas de las 64 parcelas tienen al menos una encuesta (ej. "47/64").
- **Distribución general de intención de voto**: % de cada opción sobre el total (barra o torta con Chart.js).
- **Ranking de cuadras** más fuertes para el partido propio.
- **Indecisos**: % y/o cantidad de cuadras donde "Indeciso" es mayoría (zonas a trabajar).

## 7. Blindaje legal (Ley 25.326)

1. **Checkbox de consentimiento obligatorio**, texto exacto:
   > "Confirmo que el vecino fue informado de que estos datos son para uso estadístico y de campaña"

   Validado **en el backend** (no solo `required` HTML): si `consentimiento_informado` no es `True`, el formulario no valida ni guarda. El valor queda persistido en `Familia` como prueba.
2. **Campos cerrados:** intención de voto y parcela son `choices`, nunca texto libre. No hay campo "observaciones" abierto.
3. **Disociación efectiva:** las consultas analíticas tocan solo `Voto`/`Parcela`; el JOIN con datos personales solo en "Detalle nominal", detrás del mixin de rol.
4. **Guardado transaccional:** `Familia` + `Voto` se escriben en `transaction.atomic()` — o ambas o ninguna.

## 8. Reglas de seguridad (backend, siempre)

1. Un encuestador nunca accede a vistas del Jefe (mixin de rol → 403).
2. Un encuestador solo opera sobre familias de **sus parcelas asignadas**, y edita/borra solo las **cargadas por él**.
3. Redirección post-login según rol: encuestador → "Cargar familia"; jefe → "Dashboard".

## 9. Testing (núcleo a cubrir)

- **RBAC:** encuestador recibe 403 en dashboard, parcelas ajenas y al editar familias de otros; jefe accede a todo.
- **Disociación:** las consultas de mapa/KPIs no tocan datos personales; el detalle nominal sí hace el JOIN.
- **Validación legal:** guardar sin `consentimiento_informado=True` falla; con el checkbox marcado, guarda.
- **Agregación del mapa:** color/opacidad correctos según votos; parcela vacía = transparente; desempate determinista.
- **Atomicidad:** si falla el guardado del `Voto`, no queda la `Familia` suelta.

## 10. Despliegue (PythonAnywhere free tier)

- Subir la imagen y correr `collectstatic`.
- **Datos semilla:** comando de management `python manage.py seed_parcelas` que parsea `coordenadas.md` y crea las 64 `Parcela` una sola vez.
- El free tier "duerme" y reinicia la app; con SQLite y pocos usuarios no hay problema de concurrencia.

## 11. Fuera de alcance (YAGNI)

- Preocupación principal / reclamos.
- Voto por persona individual (la unidad es la familia).
- Geocodificación por dirección.
- Zoom/pan avanzado del mapa (Leaflet) — solo si el Enfoque A se queda corto.
- Django REST Framework / API pública.
