import sqlite3
from fastapi import HTTPException
from database import conectar

def asignar_ticket(datos, usuario='sistema'):
    # Transaccion IMMEDIATE: evita asignaciones concurrentes con conteos obsoletos.
    with conectar() as c:
        c.execute('BEGIN IMMEDIATE')
        if not c.execute('SELECT 1 FROM equipos WHERE id=?',(datos['equipo_id'],)).fetchone():
            raise HTTPException(404,'El equipo no existe')
        tec=c.execute("""SELECT t.id,COUNT(k.id) carga FROM tecnicos t
          LEFT JOIN tickets k ON t.id=k.tecnico_id AND k.estado IN ('abierto','en_proceso')
          WHERE t.activo=1 GROUP BY t.id ORDER BY carga,t.id LIMIT 1""").fetchone()
        if not tec: raise HTTPException(400,'No hay tecnicos activos disponibles')
        horas={'alta':4,'media':8,'baja':24}[datos['prioridad']]
        cur=c.execute("INSERT INTO tickets(equipo_id,descripcion,prioridad,tecnico_id,sla_horas,fecha_limite) VALUES(?,?,?,?,?,datetime('now', ?))",
                      (datos['equipo_id'],datos['descripcion'],datos['prioridad'],tec['id'],horas,f'+{horas} hours'))
        ticket=dict(c.execute('SELECT * FROM tickets WHERE id=?',(cur.lastrowid,)).fetchone())
        c.execute('INSERT INTO eventos_ticket(ticket_id,usuario,accion,detalle) VALUES(?,?,?,?)',
                  (cur.lastrowid,usuario,'Ticket creado',f"Asignado a técnico #{tec['id']} · SLA {horas} horas"))
        return ticket

def cambiar_ticket(id, datos, usuario='sistema'):
    with conectar() as c:
        c.execute('BEGIN IMMEDIATE')
        actual=c.execute('SELECT * FROM tickets WHERE id=?',(id,)).fetchone()
        if not actual: raise HTTPException(404,'Ticket no encontrado')
        if actual['estado']=='cerrado': raise HTTPException(400,'No se puede modificar un ticket cerrado')
        if datos.get('estado')=='cerrado':
            if not c.execute('SELECT 1 FROM seguimientos WHERE ticket_id=? LIMIT 1',(id,)).fetchone():
                raise HTTPException(400,'Debe registrar al menos un seguimiento antes de cerrar')
        permitidos={k:v for k,v in datos.items() if v is not None and k in ('equipo_id','descripcion','prioridad','estado')}
        if not permitidos: raise HTTPException(400,'Debe proporcionar algun campo')
        cambios=[]
        for campo, valor in permitidos.items():
            anterior=actual[campo]
            if anterior != valor: cambios.append(f'{campo}: {anterior} → {valor}')
        c.execute('UPDATE tickets SET '+','.join(f'{k}=?' for k in permitidos)+' WHERE id=?',tuple(permitidos.values())+(id,))
        if cambios:
            c.execute('INSERT INTO eventos_ticket(ticket_id,usuario,accion,detalle) VALUES(?,?,?,?)',
                      (id,usuario,'Ticket actualizado','; '.join(cambios)))
        if permitidos.get('estado')=='cerrado':
            c.execute('INSERT INTO eventos_ticket(ticket_id,usuario,accion,detalle) VALUES(?,?,?,?)',
                      (id,usuario,'Ticket cerrado','Resolución registrada'))
        return dict(c.execute('SELECT * FROM tickets WHERE id=?',(id,)).fetchone())
