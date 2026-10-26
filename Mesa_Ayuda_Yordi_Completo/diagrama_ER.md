# Diagrama entidad-relación — Mesa de ayuda

Pega este bloque en GitHub o en un editor compatible con Mermaid para visualizarlo.

```mermaid
erDiagram
    DEPARTAMENTOS ||--o{ EQUIPOS : tiene
    EQUIPOS ||--o{ TICKETS : presenta
    TECNICOS |o--o{ TICKETS : atiende
    TICKETS ||--o{ SEGUIMIENTOS : registra
    TECNICOS |o--o| USUARIOS : accede
    DEPARTAMENTOS {
      int id PK
      string nombre UK
      string ubicacion
    }
    EQUIPOS {
      int id PK
      string codigo_inventario UK
      string tipo
      string marca
      string modelo
      int departamento_id FK
    }
    TECNICOS {
      int id PK
      string nombre
      string especialidad
      string correo UK
      bool activo
    }
    TICKETS {
      int id PK
      int equipo_id FK
      string descripcion
      string prioridad
      string estado
      int tecnico_id FK
      datetime fecha_creacion
      datetime fecha_cierre
    }
    SEGUIMIENTOS {
      int id PK
      int ticket_id FK
      string comentario
      datetime fecha
    }
    USUARIOS {
      int id PK
      string nombre_usuario UK
      string contrasena_hash
      string rol
      int tecnico_id FK
    }
```

## Relaciones

- Un departamento puede tener muchos equipos; cada equipo pertenece a un departamento.
- Un equipo puede tener muchos tickets; cada ticket se refiere a un equipo.
- Un técnico puede atender muchos tickets; un ticket puede permanecer sin técnico antes de asignarse.
- Un ticket puede tener muchos seguimientos; para cerrarlo se exige al menos uno.
- Un usuario puede estar asociado a un técnico (opcional para administrador).
