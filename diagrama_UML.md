# Diagrama UML de clases — Mesa de ayuda de soporte técnico

## 1. Estructura de la institución

- **Departamento:** área donde se encuentra un equipo (Contabilidad, Dirección, etc.).
- **Equipo:** dispositivo inventariado (computadora, impresora, servidor). Pertenece a un departamento.

## 2. Atención de fallas

- **Ticket / solicitud de soporte:** problema reportado en un equipo. Incluye descripción, prioridad, estado y técnico responsable.
- **Seguimiento:** acción o comentario registrado durante el trabajo. Un ticket puede tener varios seguimientos.

## 3. Personal y acceso al sistema

- **Técnico:** empleado de soporte que atiende tickets.
- **Usuario del sistema:** cuenta para ingresar con contraseña protegida y rol; puede vincularse con un técnico.

## 4. Relaciones que debes explicar

1. Un departamento tiene muchos equipos; cada equipo pertenece a un departamento.
2. Un equipo puede generar varios tickets; cada ticket corresponde a un equipo.
3. Un técnico puede atender varios tickets; un ticket puede tener un técnico asignado.
4. Cada ticket puede registrar muchos seguimientos, pero cada seguimiento pertenece a un solo ticket.
5. Un técnico puede estar vinculado con una cuenta de usuario; los administradores no necesitan técnico asignado.

## 5. Cómo funciona el proceso

**Equipo falla → Se crea un ticket → Se asigna al técnico con menos tickets abiertos → El técnico registra seguimientos → Se cierra el ticket cuando tiene un seguimiento → Se registra la fecha de cierre automáticamente.**

## 6. Cómo leer el diagrama

- Cada recuadro representa una **clase** del sistema.
- Arriba está el **nombre de la clase**.
- Debajo se muestran los **atributos** y sus tipos.
- Las flechas unen clases relacionadas. El texto indica cuántos registros pueden relacionarse.
- El método `puede_cerrarse()` comprueba que exista al menos un seguimiento.

## 7. Nota sobre el código

Este diagrama muestra el **modelo funcional del sistema**, además de los campos de la base de datos. La clase Python `Ticket` implementa el método `puede_cerrarse()`; el cierre real y la fecha automática están controlados en el servicio y en la base SQLite. La asignación del técnico con menos tickets abiertos se implementa en `servicios.py`, no dentro de la clase Técnico.

Consulta la imagen `diagrama_UML.png` o el PDF `diagrama_UML.pdf` para una vista clara lista para imprimir.
