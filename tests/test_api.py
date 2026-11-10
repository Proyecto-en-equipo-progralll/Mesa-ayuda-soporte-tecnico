def test_login_incorrecto(client):
    assert client.post('/auth/login',json={'usuario':'admin','contrasena':'incorrecta'}).status_code==401

def test_sin_token(client):
    assert client.get('/tickets',headers={'Authorization':''}).status_code==401

def test_listar_equipos(client):
    assert len(client.get('/equipos').json())==10

def test_crear_departamento(client):
    r=client.post('/departamentos',json={'nombre':'Laboratorio','ubicacion':'B2'})
    assert r.status_code==201
    assert r.json()['nombre']=='Laboratorio'

def test_unico_departamento(client):
    r=client.post('/departamentos',json={'nombre':'Direccion','ubicacion':'Edificio X'})
    assert r.status_code==400

def test_equipo_departamento_inexistente(client):
    r=client.post('/equipos',json={'codigo_inventario':'EQ-100','tipo':'PC','marca':'HP','departamento_id':999})
    assert r.status_code==400

def test_prioridad_invalida(client):
    assert client.post('/tickets',json={'equipo_id':1,'descripcion':'No inicia','prioridad':'urgente'}).status_code==422

def test_asignacion_automatica(client):
    r=client.post('/tickets',json={'equipo_id':1,'descripcion':'No inicia','prioridad':'alta'})
    assert r.status_code==201
    assert r.json()['tecnico_id']==2 # técnico 2 tiene 0 tickets abiertos y es el primer id libre

def test_cierre_requiere_seguimiento(client):
    id=client.post('/tickets',json={'equipo_id':1,'descripcion':'Falla','prioridad':'media'}).json()['id']
    assert client.put(f'/tickets/{id}',json={'estado':'cerrado'}).status_code==400
    assert client.post('/seguimientos',json={'ticket_id':id,'comentario':'Se verifico la falla'}).status_code==201
    r=client.put(f'/tickets/{id}',json={'estado':'cerrado'})
    assert r.status_code==200 and r.json()['fecha_cierre'] is not None

def test_no_eliminar_equipo_con_tickets(client):
    assert client.delete('/equipos/1').status_code==400

def test_reporte(client):
    assert len(client.get('/reportes/tiempos-tecnicos').json())==10

def test_csv(client):
    r=client.get('/reportes/tickets.csv')
    assert r.status_code==200 and 'fecha_cierre' in r.text

def test_no_reabrir_cerrado(client):
    assert client.put('/tickets/1',json={'estado':'abierto'}).status_code==400

def test_ticket_incluye_sla_y_historial(client):
    creado=client.post('/tickets',json={'equipo_id':1,'descripcion':'Prueba de SLA','prioridad':'alta'})
    assert creado.status_code==201
    ticket=creado.json()
    assert ticket['sla_horas']==4 and ticket['fecha_limite']
    historial=client.get(f"/tickets/{ticket['id']}/historial")
    assert historial.status_code==200
    assert historial.json()[0]['accion']=='Ticket creado'

def test_seguimiento_se_agrega_al_historial(client):
    ticket=client.post('/tickets',json={'equipo_id':1,'descripcion':'Prueba historial','prioridad':'media'}).json()
    r=client.post('/seguimientos',json={'ticket_id':ticket['id'],'comentario':'Se revisó el equipo'})
    assert r.status_code==201
    eventos=client.get(f"/tickets/{ticket['id']}/historial").json()
    assert any(e['accion']=='Seguimiento agregado' for e in eventos)

def test_reporte_sla(client):
    r=client.get('/reportes/sla')
    assert r.status_code==200
    assert {'vencidos','dentro_plazo','cerrados_a_tiempo','cerrados_tarde'} <= set(r.json()['resumen'])

def test_tecnico_solo_ve_sus_tickets(client):
    from seguridad import hash_clave
    with __import__('database').conectar() as c:
        c.execute("INSERT INTO usuarios(nombre_usuario,contrasena_hash,rol,tecnico_id) VALUES(?,?,?,?)",
                  ('tecnico_prueba',hash_clave('clave-segura-123'),'tecnico',2))
    login=client.post('/auth/login',json={'usuario':'tecnico_prueba','contrasena':'clave-segura-123'}).json()
    headers={'Authorization':'Bearer '+login['access_token']}
    tickets=client.get('/tickets',headers=headers).json()
    assert all(t['tecnico_id']==2 for t in tickets)
    ajeno=client.get('/tickets/2',headers=headers)
    if ajeno.status_code==200:
        assert ajeno.json()['tecnico_id']==2


def test_crear_mantenimiento_preventivo(client):
    r=client.post('/mantenimientos',json={'equipo_id':1,'tecnico_id':2,'tipo':'preventivo','descripcion':'Limpieza interna del equipo','fecha_programada':'2026-12-01','estado':'programado'})
    assert r.status_code==201
    assert r.json()['tipo']=='preventivo'

def test_fecha_mantenimiento_invalida(client):
    r=client.post('/mantenimientos',json={'equipo_id':1,'tipo':'preventivo','descripcion':'Revision programada','fecha_programada':'01-12-2026'})
    assert r.status_code==422

def test_tecnico_no_puede_ver_ticket_ajeno(client):
    from seguridad import hash_clave
    from database import conectar
    with conectar() as c:
        c.execute("INSERT INTO usuarios(nombre_usuario,contrasena_hash,rol,tecnico_id) VALUES(?,?,?,?)",
                  ('tecnico_dos',hash_clave('clave-segura-123'),'tecnico',2))
        c.execute("UPDATE tickets SET tecnico_id=1 WHERE id=10")
    login=client.post('/auth/login',json={'usuario':'tecnico_dos','contrasena':'clave-segura-123'}).json()
    headers={'Authorization':'Bearer '+login['access_token']}
    assert client.get('/tickets/10',headers=headers).status_code==403
    assert client.put('/tickets/10',headers=headers,json={'estado':'en_proceso'}).status_code==403

def test_tecnico_no_ve_mantenimiento_de_otro(client):
    from seguridad import hash_clave
    from database import conectar
    with conectar() as c:
        c.execute("INSERT INTO usuarios(nombre_usuario,contrasena_hash,rol,tecnico_id) VALUES(?,?,?,?)",
                  ('tecnico_tres',hash_clave('clave-segura-123'),'tecnico',3))
        c.execute("INSERT INTO mantenimientos(equipo_id,tecnico_id,tipo,descripcion,fecha_programada) VALUES(1,2,'preventivo','Limpieza','2026-12-10')")
    login=client.post('/auth/login',json={'usuario':'tecnico_tres','contrasena':'clave-segura-123'}).json()
    headers={'Authorization':'Bearer '+login['access_token']}
    assert client.get('/mantenimientos',headers=headers).json()==[]
    assert client.get('/reportes/sla',headers=headers).status_code==200


def test_mantenimiento_completado_exige_fecha_realizacion(client):
    r=client.post('/mantenimientos',json={'equipo_id':1,'tipo':'preventivo','descripcion':'Revision terminada','fecha_programada':'2026-12-01','estado':'completado'})
    assert r.status_code==422
