# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Estado del proyecto

Este repositorio está en **fase de diseño** — todavía no hay código. Contiene los documentos de especificación a partir de los cuales se construirá una aplicación web Django. Antes de generar modelos, vistas o lógica, leé `contexto.md` (reglas de negocio, roles y restricciones legales) y `coordenadas.md` (geometría del mapa).

Archivos fuente:
- `contexto.md` — briefing del proyecto: objetivo, roles/permisos, lógica del mapa de calor y restricciones legales.
- `coordenadas.md` — image map HTML con 69 parcelas (`<area shape="poly">`), cada una con `alt`/`title` = número de parcela y `coords` de polígono.
- `mapa unidas.jpeg` — imagen base estática (Colonias Unidas, Chaco, Argentina) sobre la que se dibujan las parcelas.

## Stack y despliegue

- **Backend:** Django.
- **Despliegue:** PythonAnywhere. Tené en cuenta sus limitaciones (sin procesos en background arbitrarios, base de datos típicamente MySQL/SQLite, archivos estáticos servidos por la plataforma) al elegir dependencias y arquitectura.

## Modelo de dominio (objetivo)

Plataforma de gestión territorial y encuestas políticas. El núcleo es un **mapa de calor interactivo** que visualiza resultados de encuestas parcela por parcela (cuadra), más un panel de KPIs.

- Las 69 parcelas del image map son las unidades geográficas. Las `coords` de `coordenadas.md` se renderizan como polígonos interactivos (SVG o equivalente) sobre `mapa unidas.jpeg`.
- Color de cada parcela = partido/tendencia con mayoría en esa cuadra. Opacidad = porcentaje de dominancia o cantidad de encuestas.

## Reglas críticas (no negociables)

Estas reglas vienen de `contexto.md` y son requisitos legales/de negocio, no preferencias. Cualquier diseño de modelos o vistas debe respetarlas:

1. **RBAC con dos roles de interfaces totalmente separadas:**
   - **Encuestador (operativo):** NO accede al mapa. Solo formulario de carga de encuestas y una vista en lista básica de lo que cargó, sin cruces masivos de datos sensibles.
   - **Jefe de Campaña (admin/analista):** acceso total. Dashboard con mapa de calor + panel de KPIs (total de encuestas, % de intención de voto, zonas con más reclamos, etc.). Al clickear una parcela puede "Ver detalle nominal" (qué familia vota a quién, contacto y reclamos de esa cuadra).

2. **Disociación de datos (Ley 25.326, datos sensibles = ideología política):** a nivel de base de datos los datos identificatorios (nombre, teléfono) deben estar **separados** de la intención de voto. Solo se unen mediante JOINs cuando el Jefe de Campaña lo pide explícitamente en la vista de detalle. Diseñá los modelos para que esta separación sea estructural, no solo a nivel de vista.

3. **Formulario del Encuestador:** "Observaciones" de texto libre se reemplaza por menús desplegables cerrados (Intención de voto, Preocupación principal). Es **obligatorio** un checkbox que el encuestador debe marcar para poder guardar: *"Confirmo que el vecino fue informado de que estos datos son para uso estadístico y de campaña"* — sirve de blindaje legal y la validación no se puede saltear.
