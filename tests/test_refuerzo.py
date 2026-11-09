import sqlite3
from pathlib import Path

def test_no_editar_seguimiento_cerrado(client):
    r=client.put('/seguimientos/1',json={'ticket_id':1,'comentario':'Editado'})
    assert r.status_code==400

def test_no_eliminar_seguimiento_cerrado(client):
    assert client.delete('/seguimientos/1').status_code==400

def test_no_agregar_seguimiento_cerrado(client):
    assert client.post('/seguimientos',json={'ticket_id':1,'comentario':'Otro'}).status_code==400

def test_seguimiento_no_existente(client):
    assert client.post('/seguimientos',json={'ticket_id':999,'comentario':'Prueba'}).status_code==404

def test_editar_ticket_cerrado(client):
    assert client.put('/tickets/1',json={'prioridad':'baja'}).status_code==400

def test_crear_tecnico_y_actualizar(client):
    r=client.post('/tecnicos',json={'nombre':'Nueva Tecnica','especialidad':'Redes','correo':'nueva@example.org','activo':1})
    assert r.status_code==201
    i=r.json()['id']
    r=client.put(f'/tecnicos/{i}',json={'nombre':'Nueva Tecnica','especialidad':'Hardware','correo':'nueva@example.org','activo':1})
    assert r.status_code==200 and r.json()['especialidad']=='Hardware'

def test_csv_no_ejecuta_formula(client):
    r=client.post('/tickets',json={'equipo_id':1,'descripcion':'=2+2 prueba','prioridad':'baja'})
    assert r.status_code==201
    salida=client.get('/reportes/tickets.csv').text
    assert "'=2+2 prueba" in salida

def test_permisos_tecnico(client):
    user=client.post('/auth/usuarios',json={'usuario':'tecnico_prueba','contrasena':'clave-de-prueba-123','rol':'tecnico'})
    assert user.status_code==201
    login=client.post('/auth/login',json={'usuario':'tecnico_prueba','contrasena':'clave-de-prueba-123'})
    cab={'Authorization':'Bearer '+login.json()['access_token']}
    assert client.delete('/departamentos/10',headers=cab).status_code==403
    assert client.post('/reportes/respaldo',headers=cab).status_code==403

def test_respaldo_crea_archivo(client,monkeypatch,tmp_path):
    import database, routers.reportes as modulo
    # Se prueba la funcion de respaldo directamente para esperar su terminacion.
    modulo.respaldo()
    carpeta=Path(database.DB_PATH).parent/'respaldos'
    ficheros=list(carpeta.glob('mesa_ayuda_*.db'))
    assert ficheros
    with sqlite3.connect(ficheros[-1]) as c:
        assert c.execute('SELECT COUNT(*) FROM equipos').fetchone()[0]==10

def test_reporte_tiempo_tiene_campos(client):
    r=client.get('/reportes/tiempos-tecnicos')
    assert r.status_code==200
    assert {'tecnico_id','tecnico','tickets_cerrados','horas_promedio_solucion'}<=set(r.json()[0])
