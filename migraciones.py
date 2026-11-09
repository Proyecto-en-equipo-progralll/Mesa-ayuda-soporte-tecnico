"""Migraciones incrementales y seguras para instalaciones existentes."""
from database import conectar


def actualizar_esquema():
    with conectar() as c:
        columnas = {r['name'] for r in c.execute('PRAGMA table_info(tickets)')}
        if 'fecha_limite' not in columnas:
            c.execute('ALTER TABLE tickets ADD COLUMN fecha_limite TEXT')
        if 'sla_horas' not in columnas:
            c.execute('ALTER TABLE tickets ADD COLUMN sla_horas INTEGER')
        c.execute('''CREATE TABLE IF NOT EXISTS eventos_ticket (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
            usuario TEXT NOT NULL DEFAULT 'sistema',
            accion TEXT NOT NULL,
            detalle TEXT NOT NULL DEFAULT '',
            fecha TEXT NOT NULL DEFAULT (datetime('now'))
        )''')
        c.execute("""CREATE TABLE IF NOT EXISTS mantenimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipo_id INTEGER NOT NULL REFERENCES equipos(id) ON DELETE RESTRICT,
            tecnico_id INTEGER REFERENCES tecnicos(id) ON DELETE RESTRICT,
            tipo TEXT NOT NULL CHECK (tipo IN ('preventivo','correctivo')),
            descripcion TEXT NOT NULL CHECK (length(trim(descripcion)) > 0),
            fecha_programada TEXT NOT NULL, fecha_realizacion TEXT,
            estado TEXT NOT NULL DEFAULT 'programado' CHECK (estado IN ('programado','completado','cancelado'))
        )""")
        c.execute('CREATE INDEX IF NOT EXISTS idx_mantenimientos_fecha ON mantenimientos(estado, fecha_programada)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_eventos_ticket_fecha ON eventos_ticket(ticket_id, fecha DESC)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_tickets_estado_limite ON tickets(estado, fecha_limite)')
        # Completa SLA en registros de versiones anteriores sin alterar fechas originales.
        c.execute("""UPDATE tickets SET sla_horas=CASE prioridad WHEN 'alta' THEN 4 WHEN 'media' THEN 8 ELSE 24 END
                    WHERE sla_horas IS NULL""")
        c.execute("""UPDATE tickets SET fecha_limite=datetime(fecha_creacion, '+' || sla_horas || ' hours')
                    WHERE fecha_limite IS NULL""")
        c.execute("""INSERT INTO eventos_ticket(ticket_id, usuario, accion, detalle)
                    SELECT t.id, 'sistema', 'Migración inicial', 'Historial habilitado para este ticket'
                    FROM tickets t WHERE NOT EXISTS
                    (SELECT 1 FROM eventos_ticket e WHERE e.ticket_id=t.id)""")


def registrar_evento(ticket_id: int, accion: str, detalle: str = '', usuario: str = 'sistema'):
    with conectar() as c:
        c.execute('INSERT INTO eventos_ticket(ticket_id,usuario,accion,detalle) VALUES(?,?,?,?)',
                  (ticket_id, usuario or 'sistema', accion, detalle or ''))
