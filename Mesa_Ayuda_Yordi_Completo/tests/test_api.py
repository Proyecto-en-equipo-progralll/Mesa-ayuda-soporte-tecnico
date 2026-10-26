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
