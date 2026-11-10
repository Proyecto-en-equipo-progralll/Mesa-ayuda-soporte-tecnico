# UML y diagrama entidad–relación — Proyecto individual 15

**Asignación del documento:** Mesa de ayuda de soporte técnico. Estudiante: Yordi Yoel Gutiérrez Suazo. Asignatura: Programación III (IS-151), UPH.

## Lo que solicita la ficha del docente

Tablas mínimas: departamentos, equipos, tecnicos, tickets, seguimientos. Los campos obligatorios son los señalados en la ficha de la página 7. El sistema debe aceptar prioridad **baja, media o alta**, prohibir el cierre de un ticket sin al menos un seguimiento y registrar automáticamente la fecha de cierre. El reto propio es asignar tickets al técnico con menos tickets abiertos y generar el tiempo promedio de solución por técnico.

Además, el requisito técnico común solicita autenticación, por lo que la implementación añade **usuarios**.

## Cómo explicar el UML

- **Departamento → Equipo (1 a muchos):** un departamento contiene varios equipos; un equipo pertenece a un departamento.
- **Equipo → Ticket (1 a muchos):** un equipo puede presentar varias fallas; cada ticket se origina por un equipo.
- **Técnico → Ticket (1 a muchos):** un técnico puede recibir múltiples tickets, pero un ticket tiene como máximo un técnico asignado.
- **Ticket → Seguimiento (1 a muchos):** un ticket puede tener varios registros de atención; cada seguimiento pertenece a un solo ticket.
- **Técnico ↔ Usuario (opcional):** una cuenta de acceso puede asociarse a un técnico; no todos los técnicos necesitan una cuenta.

**Diferencia:** UML muestra las clases de Python, sus atributos y el método real `puede_cerrarse`. El diagrama ER muestra los campos que se guardan en las tablas SQLite, incluidas fechas y restricciones. Por ello no tienen que contener exactamente los mismos atributos.

## Reglas y lógica implementadas (fuera de las entidades)

La asignación de técnico al menos ocupado, el cierre con fecha automática y el reporte están implementados mediante lógica de servicios/API y restricciones SQL; no se presentan falsamente como métodos de `Ticket`.

## Nota importante

El UML usa los nombres de clases en español tal como aparecen en Python (`Tecnico`, `Ticket`, etc.) y títulos completamente en español. El código Python no se renombra, para evitar romper importaciones.
