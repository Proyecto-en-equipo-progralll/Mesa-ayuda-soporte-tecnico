PRAGMA foreign_keys = ON;

DROP VIEW IF EXISTS reporte_tiempo_tecnicos;
DROP TRIGGER IF EXISTS ticket_cierre_requiere_seguimiento;
DROP TRIGGER IF EXISTS ticket_fecha_cierre;
DROP TRIGGER IF EXISTS ticket_no_insertar_cerrado;
DROP TABLE IF EXISTS mantenimientos;
DROP TABLE IF EXISTS seguimientos;
DROP TABLE IF EXISTS eventos_ticket;
DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS usuarios;
DROP TABLE IF EXISTS equipos;
DROP TABLE IF EXISTS tecnicos;
DROP TABLE IF EXISTS departamentos;

CREATE TABLE departamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    ubicacion TEXT NOT NULL
);
CREATE TABLE tecnicos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    especialidad TEXT NOT NULL,
    correo TEXT NOT NULL UNIQUE,
    activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0, 1))
);
CREATE TABLE equipos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_inventario TEXT NOT NULL UNIQUE,
    tipo TEXT NOT NULL,
    marca TEXT NOT NULL,
    modelo TEXT,
    departamento_id INTEGER NOT NULL REFERENCES departamentos(id) ON DELETE RESTRICT
);
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_usuario TEXT NOT NULL UNIQUE,
    contrasena_hash TEXT NOT NULL,
    rol TEXT NOT NULL CHECK (rol IN ('administrador', 'tecnico')),
    tecnico_id INTEGER UNIQUE REFERENCES tecnicos(id) ON DELETE RESTRICT
);
CREATE TABLE tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipo_id INTEGER NOT NULL REFERENCES equipos(id) ON DELETE RESTRICT,
    descripcion TEXT NOT NULL CHECK (length(trim(descripcion)) > 0),
    prioridad TEXT NOT NULL CHECK (prioridad IN ('baja', 'media', 'alta')),
    estado TEXT NOT NULL DEFAULT 'abierto' CHECK (estado IN ('abierto', 'en_proceso', 'cerrado')),
    tecnico_id INTEGER REFERENCES tecnicos(id) ON DELETE RESTRICT,
    fecha_creacion TEXT NOT NULL DEFAULT (datetime('now')),
    fecha_cierre TEXT,
    fecha_limite TEXT,
    sla_horas INTEGER,
    CHECK (fecha_cierre IS NULL OR estado = 'cerrado')
);
CREATE TABLE eventos_ticket (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id INTEGER NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    usuario TEXT NOT NULL DEFAULT 'sistema',
    accion TEXT NOT NULL,
    detalle TEXT NOT NULL DEFAULT '',
    fecha TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE mantenimientos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipo_id INTEGER NOT NULL REFERENCES equipos(id) ON DELETE RESTRICT,
    tecnico_id INTEGER REFERENCES tecnicos(id) ON DELETE RESTRICT,
    tipo TEXT NOT NULL CHECK (tipo IN ('preventivo','correctivo')),
    descripcion TEXT NOT NULL CHECK (length(trim(descripcion)) > 0),
    fecha_programada TEXT NOT NULL,
    fecha_realizacion TEXT,
    estado TEXT NOT NULL DEFAULT 'programado' CHECK (estado IN ('programado','completado','cancelado'))
);

CREATE TABLE seguimientos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id INTEGER NOT NULL REFERENCES tickets(id) ON DELETE RESTRICT,
    comentario TEXT NOT NULL CHECK (length(trim(comentario)) > 0),
    fecha TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Reglas de negocio a nivel de base de datos.
CREATE TRIGGER ticket_no_insertar_cerrado
BEFORE INSERT ON tickets
WHEN NEW.estado = 'cerrado'
BEGIN
    SELECT RAISE(ABORT, 'Cree el ticket abierto y registre su seguimiento antes de cerrarlo');
END;

CREATE TRIGGER ticket_cierre_requiere_seguimiento
BEFORE UPDATE OF estado ON tickets
WHEN NEW.estado = 'cerrado' AND OLD.estado <> 'cerrado'
BEGIN
    SELECT CASE WHEN NOT EXISTS (
        SELECT 1 FROM seguimientos WHERE ticket_id = OLD.id
    ) THEN RAISE(ABORT, 'No se puede cerrar un ticket sin seguimiento') END;
END;

CREATE TRIGGER ticket_fecha_cierre
AFTER UPDATE OF estado ON tickets
WHEN NEW.estado = 'cerrado' AND OLD.estado <> 'cerrado'
BEGIN
    UPDATE tickets SET fecha_cierre = datetime('now') WHERE id = NEW.id;
END;

INSERT INTO departamentos (nombre, ubicacion) VALUES
('Direccion', 'Edificio A'),('Recursos Humanos','Edificio A'),('Contabilidad','Edificio B'),
('Compras','Edificio B'),('Registro','Edificio C'),('Biblioteca','Edificio C'),
('Informatica','Edificio A'),('Secretaria','Edificio A'),('Archivo','Edificio B'),
('Atencion al Publico','Edificio C');

INSERT INTO tecnicos (nombre, especialidad, correo) VALUES
('Ana Lopez','Redes','ana@institucion.local'),('Carlos Mejia','Hardware','carlos@institucion.local'),
('Brenda Flores','Software','brenda@institucion.local'),('Jose Rivera','Impresoras','jose@institucion.local'),
('Maria Torres','Hardware','maria@institucion.local'),('Pedro Cruz','Redes','pedro@institucion.local'),
('Elena Diaz','Software','elena@institucion.local'),('Luis Paz','Servidores','luis@institucion.local'),
('Sofia Molina','Seguridad','sofia@institucion.local'),('Daniel Ruiz','Soporte general','daniel@institucion.local');

INSERT INTO equipos (codigo_inventario, tipo, marca, modelo, departamento_id) VALUES
('EQ-001','Computadora','Dell','OptiPlex',1),('EQ-002','Impresora','HP','LaserJet',2),
('EQ-003','Computadora','Lenovo','ThinkCentre',3),('EQ-004','Router','TP-Link','Archer',4),
('EQ-005','Computadora','HP','ProDesk',5),('EQ-006','Impresora','Epson','EcoTank',6),
('EQ-007','Servidor','Dell','PowerEdge',7),('EQ-008','Computadora','Acer','Veriton',8),
('EQ-009','Escaner','Canon','DR-C240',9),('EQ-010','Computadora','ASUS','ExpertCenter',10);

INSERT INTO tickets (equipo_id, descripcion, prioridad, estado, tecnico_id, fecha_creacion) VALUES
(1,'La computadora no enciende','alta','abierto',2,'2026-10-20 08:00:00'),
(2,'Impresora muestra atasco de papel','media','abierto',4,'2026-10-20 08:30:00'),
(3,'No abre el programa contable','alta','abierto',3,'2026-10-20 09:00:00'),
(4,'Conexion a red intermitente','media','abierto',1,'2026-10-20 10:00:00'),
(5,'Equipo tarda en iniciar','baja','abierto',5,'2026-10-20 11:00:00'),
(6,'No imprime a color','baja','abierto',4,'2026-10-21 08:00:00'),
(7,'Servicio de archivos no responde','alta','abierto',8,'2026-10-21 09:00:00'),
(8,'Navegador se bloquea','media','abierto',7,'2026-10-21 10:00:00'),
(9,'Escaner no detecta documentos','media','abierto',10,'2026-10-21 11:00:00'),
(10,'No se puede iniciar sesion','alta','abierto',9,'2026-10-21 12:00:00');

INSERT INTO seguimientos (ticket_id, comentario, fecha) VALUES
(1,'Se reviso cableado electrico','2026-10-20 08:20:00'),
(2,'Se limpio rodillo de papel','2026-10-20 09:00:00'),
(3,'Se verifico instalacion del programa','2026-10-20 09:30:00'),
(4,'Se revisaron los puertos del router','2026-10-20 10:30:00'),
(5,'Se revisaron aplicaciones de inicio','2026-10-20 11:30:00'),
(6,'Se comprobaron cartuchos','2026-10-21 08:30:00'),
(7,'Se reinicio el servicio de archivos','2026-10-21 09:30:00'),
(8,'Se limpiaron datos temporales','2026-10-21 10:30:00'),
(9,'Se actualizaron controladores','2026-10-21 11:30:00'),
(10,'Se restablecio la configuracion de acceso','2026-10-21 12:30:00');

UPDATE tickets SET estado='cerrado' WHERE id IN (1, 2, 3);
UPDATE tickets SET estado='en_proceso' WHERE id IN (4, 7);

-- La vista calcula el promedio de horas para los tickets cerrados.
CREATE VIEW reporte_tiempo_tecnicos AS
SELECT t.id AS tecnico_id, t.nombre AS tecnico,
       COUNT(k.id) AS tickets_cerrados,
       ROUND(AVG((julianday(k.fecha_cierre) - julianday(k.fecha_creacion)) * 24), 2)
       AS horas_promedio_solucion
FROM tecnicos t LEFT JOIN tickets k
ON k.tecnico_id = t.id AND k.estado = 'cerrado'
GROUP BY t.id, t.nombre;

CREATE INDEX IF NOT EXISTS idx_eventos_ticket_fecha ON eventos_ticket(ticket_id, fecha DESC);
CREATE INDEX IF NOT EXISTS idx_tickets_estado_limite ON tickets(estado, fecha_limite);
