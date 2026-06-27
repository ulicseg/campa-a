Actúa como un Arquitecto de Software y Desarrollador Full-Stack Experto en Django.

Te voy a proporcionar una imagen de un mapa de una localidad (Colonias Unidas, Chaco, Argentina) con sus respectivas coordenadas en HTML (<area>), y una estructura de datos basada en relevamientos territoriales (planillas con datos de familias, contactos y observaciones políticas).

Necesito que me asistas en el desarrollo de una aplicación web, pero antes de generar cualquier código o estructura técnica, debes entender y memorizar el siguiente contexto general, las reglas de negocio y las restricciones legales del proyecto. El despliegue se realizará en PythonAnywhere utilizando Django.

1. Objetivo Principal del Proyecto:
Crear una plataforma de gestión territorial y encuestas políticas. El núcleo analítico será un mapa interactivo (Mapa de Calor) que permita visualizar los resultados de las encuestas cuadra por cuadra (parcelas), complementado con indicadores clave de rendimiento (KPIs).

2. Arquitectura de Roles y Permisos (RBAC - CRÍTICO):
El sistema debe estar fuertemente blindado mediante un sistema de usuarios con dos roles exclusivos y con interfaces completamente distintas:

Rol "Encuestador" (Operativo):

NO TIENE ACCESO AL MAPA. * Su interfaz se limita exclusivamente a la carga de datos y revisión básica.

Puede ver el formulario para cargar nuevas encuestas.

Puede ver una vista en formato de lista de los datos cargados, pero sin exponer cruces de datos sensibles masivos.

Rol "Jefe de Campaña" (Administrador y Analista):

Tiene acceso total.

Vista Principal (Dashboard): Visualiza el Mapa de Calor interactivo. Debajo del mapa, se debe incluir un panel de KPIs (Key Performance Indicators) con métricas globales (Ej: Total de encuestas realizadas, Porcentaje de intención de voto general, Zonas con mayor índice de reclamos, etc.).

Al hacer clic en una parcela del mapa, tiene la opción de "Ver detalle nominal", lo que despliega la lista exacta de qué familia vota a quién, sus datos de contacto y reclamos en esa cuadra específica.

3. Lógica Visual del Mapa (Solo para Jefe de Campaña):

El mapa base es una imagen estática sobre la cual se dibujarán polígonos interactivos (SVG o similar) usando las coordenadas HTML que te pasaré.

Mapa de Calor: Cada parcela se pintará de un color dependiendo del partido político o tendencia que tenga mayoría en esa cuadra. La opacidad (intensidad del color) dependerá del porcentaje de dominancia o cantidad de encuestas realizadas.

4. Restricciones Legales y Éticas (Ley 25.326 de Argentina):
La aplicación manejará "Datos Sensibles" (ideología política). Para proteger al equipo de desarrollo y cumplir con la ley, el diseño del sistema debe forzar las siguientes reglas:

Disociación de Datos: A nivel de base de datos, los datos identificatorios de las personas (nombre, teléfono) deben estar separados de la intención de voto. Solo se unen mediante consultas (JOINs) cuando el Jefe de Campaña lo solicita explícitamente en su vista detallada.

El Checkbox Obligatorio: En la interfaz del formulario de carga (vista del Encuestador), el campo de texto libre "Observaciones" se reemplazará por menús desplegables cerrados (Intención de voto, Preocupación principal). Es obligatorio incluir una casilla de verificación (Checkbox) que el Encuestador deba marcar sí o sí para poder guardar el registro. El texto será: "Confirmo que el vecino fue informado de que estos datos son para uso estadístico y de campaña". Esto sirve como blindaje legal para el sistema.

Instrucción Final para la IA:
Confirma que has entendido este contexto, las diferencias estrictas de interfaces entre roles, el panel de KPIs y las restricciones legales. Una vez que confirmes, te pasaré las coordenadas del mapa y la estructura de las columnas para que empecemos a diseñar los modelos, la lógica y las vistas en Django.