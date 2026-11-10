# Mesa de ayuda de soporte técnico · Programación III

Proyecto individual N.º 15, UPH. Estudiante: Yordi Yoel Gutiérrez Suazo.

## Alcance

Sistema diseñado desde cero para departamentos, equipos, técnicos, tickets, seguimientos y usuarios. SQLite, FastAPI, Pydantic, repositorios, clases de dominio, autenticación mediante token HMAC con caducidad de una hora y contraseñas PBKDF2-SHA256. Dashboard HTML/JS, reportes de totales y tiempos promedio, CSV y respaldo SQLite en hilo. pruebas automatizadas ampliadas.

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
- `GET /reportes/resumen`, `GET /reportes/tiempos-tecnicos`, `GET /reportes/tickets.csv`.
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


## Base de datos de demostración incluida
Esta entrega incluye `mesa_ayuda.db`, con 10 registros de prueba para cada tabla principal y un usuario administrador inicial con clave aleatoria indicada en `ACCESO_INICIAL.txt`. Cambie la clave usando `python cambiar_clave.py`. No ejecute `inicializar_bd.py` sobre esa base salvo que quiera reemplazarla. Archivos UML y ER disponibles en Markdown, DOT y PNG. No suba las credenciales de demostración a un repositorio público.


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
