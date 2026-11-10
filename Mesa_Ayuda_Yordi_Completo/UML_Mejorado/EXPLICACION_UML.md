# UML del Sistema de Mesa de Ayuda — guía de defensa

## Lámina 1: Clases y relaciones
- **Departamento**: el área donde se encuentran los equipos. Un departamento tiene muchos equipos.
- **Equipo**: equipo inventariado que puede reportar varios tickets.
- **Ticket**: incidente reportado, con prioridad, estado y técnico asignado. El método `puede_cerrarse(seguimientos)` impide cerrar sin seguimiento.
- **Técnico**: persona que atiende varios tickets.
- **Seguimiento**: registro de cada avance del ticket. Un ticket puede tener varios.
- **Usuario**: credenciales y rol para acceder al sistema. Se representa independiente porque no hay relación obligatoria con técnicos.

**Las cardinalidades** `1` y `0..*` significan 'uno' y 'cero o muchos'.

## Lámina 2: Arquitectura
El dashboard se comunica con las rutas FastAPI. Las rutas llaman a la lógica de negocio y los repositorios, y éstos acceden a SQLite. El sistema usa `RepositorioBase` como clase reutilizable y repositorios por tabla.

## Tres reglas que debes saber explicar
1. El ticket solo acepta prioridades baja, media y alta.
2. El técnico se asigna según la cantidad menor de tickets abiertos o en proceso.
3. El ticket no se cierra sin seguimiento; la base registra la fecha del cierre.

**Nota:** el dibujo es simplificado para exposición. Campos de base de datos adicionales se consultan en `crear_bd.sql`. Los nombres de clases siguen el código Python real.
