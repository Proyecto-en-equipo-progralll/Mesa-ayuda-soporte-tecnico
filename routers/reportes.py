import csv,io,threading,shutil,datetime,sqlite3
from pathlib import Path
from fastapi import APIRouter,Depends,Response,BackgroundTasks
from database import conectar
import database
from seguridad import actual,admin
router=APIRouter(prefix='/reportes',tags=['Reportes'])
@router.get('/resumen')
def resumen(u=Depends(actual)):
    with conectar() as c:
        return {'tickets_por_estado':[dict(r) for r in c.execute('SELECT estado, COUNT(*) cantidad FROM tickets GROUP BY estado')],
                'tickets_por_prioridad':[dict(r) for r in c.execute('SELECT prioridad, COUNT(*) cantidad FROM tickets GROUP BY prioridad')],
                'total_equipos':c.execute('SELECT count(*) FROM equipos').fetchone()[0]}

@router.get('/sla')
def reporte_sla(u=Depends(actual)):
    filtro=' WHERE tecnico_id=?' if u['rol']=='tecnico' else ''
    parametros=(u.get('tecnico_id'),) if u['rol']=='tecnico' else ()
    with conectar() as c:
        resumen=c.execute("""SELECT
            SUM(CASE WHEN estado!='cerrado' AND datetime(fecha_limite)<datetime('now') THEN 1 ELSE 0 END) vencidos,
            SUM(CASE WHEN estado!='cerrado' AND datetime(fecha_limite)>=datetime('now') THEN 1 ELSE 0 END) dentro_plazo,
            SUM(CASE WHEN estado='cerrado' AND datetime(fecha_cierre)<=datetime(fecha_limite) THEN 1 ELSE 0 END) cerrados_a_tiempo,
            SUM(CASE WHEN estado='cerrado' AND datetime(fecha_cierre)>datetime(fecha_limite) THEN 1 ELSE 0 END) cerrados_tarde
            FROM tickets"""+filtro,parametros).fetchone()
        filtro_detalle=' WHERE k.tecnico_id=?' if u['rol']=='tecnico' else ''
        detalle=[dict(r) for r in c.execute("""SELECT k.id,k.descripcion,k.prioridad,k.estado,k.fecha_limite,
            CASE WHEN k.estado='cerrado' THEN 'cerrado' WHEN datetime(k.fecha_limite)<datetime('now') THEN 'vencido' ELSE 'en_plazo' END cumplimiento,
            te.nombre tecnico, e.codigo_inventario equipo
            FROM tickets k LEFT JOIN tecnicos te ON te.id=k.tecnico_id
            LEFT JOIN equipos e ON e.id=k.equipo_id"""+filtro_detalle+" ORDER BY CASE WHEN k.estado!='cerrado' AND datetime(k.fecha_limite)<datetime('now') THEN 0 ELSE 1 END, k.fecha_limite ASC LIMIT 100""",parametros)]
    return {'resumen':{k:int(v or 0) for k,v in dict(resumen).items()},'tickets':detalle}

@router.get('/tiempos-tecnicos')
def tiempos(u=Depends(actual)):
    with conectar() as c: return [dict(r) for r in c.execute('SELECT * FROM reporte_tiempo_tecnicos ORDER BY tecnico')]
@router.get('/tickets.csv')
def csv_tickets(u=Depends(actual)):
    with conectar() as c:
        if u['rol']=='tecnico': rows=[dict(x) for x in c.execute('SELECT * FROM tickets WHERE tecnico_id=? ORDER BY id',(u.get('tecnico_id'),))]
        else: rows=[dict(x) for x in c.execute('SELECT * FROM tickets ORDER BY id')]
    out=io.StringIO(); campos=['id','equipo_id','descripcion','prioridad','estado','tecnico_id','fecha_creacion','fecha_cierre','sla_horas','fecha_limite']
    # Excel y otras hojas pueden interpretar celdas que comienzan por =,+,-,@ como formulas.
    # Proteger todas las columnas de texto provenientes de usuarios.
    for fila in rows:
        for campo in ('descripcion', 'prioridad', 'estado'):
            valor=fila.get(campo)
            if isinstance(valor,str) and valor.lstrip().startswith(('=','+','-','@')):
                fila[campo]="'"+valor
    wr=csv.DictWriter(out,fieldnames=campos);wr.writeheader();wr.writerows(rows)
    return Response('﻿'+out.getvalue(),media_type='text/csv; charset=utf-8',headers={'Content-Disposition':'attachment; filename="tickets.csv"'})

def respaldo():
    destino=Path(database.DB_PATH).resolve().parent/'respaldos'; destino.mkdir(exist_ok=True)
    archivo=destino/('mesa_ayuda_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'.db')
    with conectar() as origen, sqlite3.connect(archivo) as copia: origen.backup(copia)
@router.post('/respaldo',status_code=202)
def generar_respaldo(u=Depends(admin)):
    hilo=threading.Thread(target=respaldo,daemon=False)
    hilo.start()
    return {'mensaje':'Respaldo iniciado en un hilo','carpeta':'respaldos/'}
