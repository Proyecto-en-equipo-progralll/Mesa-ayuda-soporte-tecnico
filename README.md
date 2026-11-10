# Mesa de ayuda de soporte técnico · Programación III

Proyecto individual N.º 15, UPH. Estudiante: Yordi Yoel Gutiérrez Suazo.

## Alcance

Sistema diseñado desde cero para departamentos, equipos, técnicos, tickets, seguimientos y usuarios. SQLite, FastAPI, Pydantic, repositorios, clases de dominio, autenticación mediante token HMAC con caducidad de una hora y contraseñas PBKDF2-SHA256. Dashboard HTML/JS, reportes de totales y tiempos promedio, CSV y respaldo SQLite en hilo. pruebas automatizadas ampliadas.

## Requisitos

Python 3.10 o superior y Windows, Linux o macOS.

## Instalar y ejecutar (Windows PowerShell)

```powershell
cd ruta\Mesa_Ayuda_Yordi_Completo
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python inicializar_bd.py
python -m uvicorn main:app --reload
```

La inicialización solicita el nombre y contraseña del administrador (mínimo 10 caracteres). No se distribuyen contraseñas fijas. **No vuelvas a inicializar con datos reales: recrea la base.**

Abre `http://127.0.0.1:8000` para la interfaz o `http://127.0.0.1:8000/docs` para Swagger. Inicia sesión con el usuario y contraseña creados.

## Ejecución de pruebas

```powershell
python -m pytest -q
```

## Organización

- `crear_bd.sql`: tablas, restricciones, vistas, disparadores y 10 filas por tabla principal.
- `database.py`: conexión SQLite y claves foráneas.
- `modelos/entidades.py`: clases de dominio y método `puede_cerrarse`.
- `repositorios/`: herencia `RepositorioBase`, CRUD de entidades.
- `esquemas.py`: validaciones Pydantic.
- `routers/`: autenticación, CRUD, reportes y backups.
- `servicios.py`: transacción de asignación automática y regla de cierre.
- `seguridad.py`: contraseñas y tokens firmados.
- `static/index.html`: interfaz para operaciones generales.
- `tests/`: validaciones de la API.
- `diagrama_ER.md`, `diagrama_UML.md`: diagramas Mermaid; ver en GitHub.

## Endpoints destacados

- `POST /auth/login`, `GET /auth/yo`, `POST /auth/usuarios` (administrador).
- GET/POST/PUT/DELETE `/departamentos`, `/equipos`, `/tecnicos`, `/tickets`, `/seguimientos` (con `/{id}` para detalle, modificación y eliminación).
- `GET /reportes/resumen`, `GET /reportes/tiempos-tecnicos`, `GET /reportes/sla`, `GET /reportes/tickets.csv`.
- `GET /tickets/{id}/historial` y `GET /mis-tickets`.
- CRUD `/mantenimientos` para planificación de mantenimiento de equipos.
- `POST /reportes/respaldo` (administrador): crea un archivo en `respaldos/` mediante un hilo.

## Reglas

- Prioridades: baja, media, alta.
- Crear ticket asigna técnico activo con menos tickets abiertos o en proceso, desempate por id; transacción IMMEDIATE.
- No se cierra sin seguimiento; trigger SQLite registra automáticamente `fecha_cierre`.
- Los tickets cerrados no se modifican por la API y sus seguimientos quedan bloqueados.
- Eliminaciones vinculadas a otras tablas se rechazan por integridad referencial.
- Solo administradores eliminan registros, crean usuarios y generan respaldos.

## GitHub y defensa

Crear repositorio público `gutierrez-yordi-mesa-ayuda`. Realizar commits propios en distintas fechas y documentar cada cambio; **no inventar commits anteriores**. Para la defensa comprende las relaciones, la herencia Repository, la transacción de asignación, los triggers y las validaciones. Añade capturas reales después de ejecutar el sistema.

## Seguridad y limitaciones

Diseñado para demostración académica local, no despliegue público sin endurecimiento de seguridad. Configura `MESA_SECRET` con una clave aleatoria persistente, usa HTTPS y controla acceso al servidor si lo publicas. El token se guarda solamente en memoria del navegador. Los cambios de contraseña no invalidan inmediatamente tokens existentes. No se incluye una UI para creación de usuarios (se realiza desde `/docs` por administrador). La exportación CSV protege campos de texto frente a fórmulas de hoja de cálculo y se limita a tickets y el respaldo se guarda en el equipo servidor.

## Mejoras del dashboard (revisión del 26/10/2026)

La interfaz ahora muestra códigos/nombres de equipos, técnicos y departamentos en lugar de números sin contexto. Los formularios de `equipo_id`, `departamento_id` y `ticket_id` utilizan listas desplegables alimentadas por la API; los tickets cerrados ya no aparecen para nuevos seguimientos. Se añadieron estados y prioridades legibles, tarjetas de estadísticas, búsqueda, confirmación antes de eliminar, permisos visibles según el rol y un diseño adaptable a móviles.

**En Windows, opción sencilla:** desde la carpeta que contiene `main.py`, ejecuta primero `INSTALAR_WINDOWS.bat` y luego `INICIAR_WINDOWS.bat`. Alternativamente, usa `python -m pip install -r requirements.txt` y `python -m uvicorn main:app --reload`. Si no existe una base de datos, `INICIAR_WINDOWS.bat` abrirá la inicialización y solicitará las credenciales del administrador.

**Al actualizar una instalación existente:** detén Uvicorn (Ctrl+C), realiza copia de seguridad de tu `mesa_ayuda.db`, reemplaza los archivos de código sin eliminar esa base, y arranca de nuevo. **No ejecutes `inicializar_bd.py` sobre datos existentes**. La versión revisada no incluye una base `mesa_ayuda.db`, por lo que al extraerla no sustituye automáticamente tus registros; consérvalos en la misma carpeta de ejecución.

**Alcance de validación:** pruebas API con pytest y validación de sintaxis JavaScript; el funcionamiento visual en el navegador y Windows debe comprobarse en el equipo de destino. Uso académico local; no exponer el servidor públicamente sin endurecer seguridad.


## UML explicado en español
Abre `diagrama_UML.pdf` para el diagrama con secciones en español o `diagrama_UML.md` para leer la explicación de cada clase y relación.


## Versión visual revisada (26 de octubre de 2026)

- UML aprobado en español: `DOCUMENTACION/UML_APROBADO/` (PNG, PDF, SVG y guía).
- Listados simplificados (sin columnas técnicas redundantes) y nombres comprensibles.
- Tickets cerrados se presentan como historial y no ofrecen edición desde el dashboard.
- Botón **Actualizar datos**, mejora de contraste y distribución en pantallas pequeñas.
- Se mantienen las rutas de la API, las tablas y los datos de ejemplo.

### Conservación de datos personales
Si ya utilizas una instalación anterior, respalda su `mesa_ayuda.db` y sustituye únicamente ese archivo en este proyecto **con Uvicorn detenido**. No ejecutes `inicializar_bd.py` sobre una base con datos reales. La base suministrada es de demostración.

---

# Versión 2.0 · mejoras funcionales

Esta versión mantiene la API y los módulos originales, e incorpora:

- **SLA automático por prioridad:** alta 4 horas, media 8 horas y baja 24 horas. El vencimiento se calcula al crear el ticket.
- **Panel de cumplimiento:** muestra tickets vencidos, activos dentro del plazo y tickets cerrados a tiempo o tarde.
- **Historial de auditoría:** registra creación, cambios, cierre y seguimientos de cada ticket; se consulta desde el botón Historial.
- **Vista de trabajo del técnico:** `GET /mis-tickets`; además, las cuentas de técnico solo pueden consultar y modificar tickets asignados a su propio `tecnico_id`.
- **Mantenimiento de equipos:** programación de mantenimientos preventivos/correctivos, asignación opcional de técnico y fechas programadas/realizadas. Solo administradores crean o modifican mantenimientos; técnicos consultan los que tienen asignados.
- **Exportación CSV ampliada:** incluye SLA y fecha límite.
- **Migración automática:** al iniciar el servidor, `migraciones.py` agrega las columnas y la tabla de eventos si faltan, y completa los SLA de tickets existentes. No elimina tablas ni reinicializa la base.
- **Secreto persistente local:** si no configuras `MESA_SECRET`, se crea `.mesa_secret` una sola vez y se reutiliza en reinicios. El archivo está excluido de Git. En producción configura `MESA_SECRET` con un valor aleatorio seguro.

## Actualizar desde una versión anterior

1. Detén el servidor con `Ctrl+C`.
2. Haz una copia de `mesa_ayuda.db` y de `.mesa_secret` si existe.
3. Extrae esta versión en una carpeta nueva o reemplaza los archivos de aplicación conservando tu base de datos.
4. Instala dependencias con `INSTALAR_WINDOWS.bat` o `python -m pip install -r requirements.txt`.
5. Inicia con `INICIAR_WINDOWS.bat` o `python -m uvicorn main:app --reload`.
6. La migración se ejecuta automáticamente al arrancar. No ejecutes `inicializar_bd.py` para actualizar.

## Credenciales y usuarios técnicos

En una instalación nueva, `INICIAR_WINDOWS.bat` ejecuta la inicialización y solicita crear el usuario administrador y su contraseña. En una actualización, el usuario administrador existente conserva sus credenciales. Para vincular una cuenta técnica, crea el usuario desde `/docs` como administrador mediante `POST /auth/usuarios`, asignando el `tecnico_id` correcto. Cada técnico solo verá tickets asignados a su registro de técnico.

## Verificación de la versión 2.0

Ejecuta `python -m pytest -q`. Las pruebas cubren autenticación, CRUD, asignación automática, cierre con seguimiento, SLA, historial, restricciones por técnico y la interfaz. La versión se identifica como `2.0.0` en OpenAPI.

**Nota de despliegue:** el proyecto sigue orientado a uso local/académico. Para acceso por red o Internet se requiere HTTPS, configuración de `MESA_SECRET`, política de respaldos, control de acceso al servidor y revisión de archivos adjuntos (no se habilita carga arbitraria de archivos en esta entrega).


## Interfaz visual 3.0 · noviembre de 2026

- Rediseño de estructura con barra lateral de navegación y área de trabajo.
- Accesos directos a Resumen, Tickets, Departamentos, Equipos, Técnicos, Seguimientos y Mantenimientos.
- Inicio de sesión renovado, cabecera clara, jerarquía tipográfica y tarjetas de métricas simplificadas.
- Tablas, formularios, controles, estados y navegación adaptados a pantallas pequeñas.
- Se conservan las rutas API, nombres de campos, reglas de negocio y operaciones existentes.
- `INICIAR_WINDOWS.bat` también detecta una base de datos de cero bytes y ejecuta el asistente de inicialización; el asistente solicita confirmación antes de recrear el archivo.

Esta actualización modifica la presentación web y el lanzador de Windows. No reemplaza ni borra una base de datos con contenido.
