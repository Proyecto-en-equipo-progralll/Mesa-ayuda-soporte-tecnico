from pathlib import Path

def test_portada_html(client):
    r=client.get('/')
    assert r.status_code==200
    assert 'text/html' in r.headers['content-type']
    assert 'Gestión de registros' in r.text
    assert 'id="modulo"' in r.text

def test_catalogos_para_selectores(client):
    for modulo in ('departamentos','equipos','tecnicos','tickets'):
        r=client.get('/'+modulo)
        assert r.status_code==200
        assert isinstance(r.json(),list)

def test_resumen_reporte(client):
    assert client.get('/reportes/resumen').status_code==200
    assert isinstance(client.get('/reportes/tiempos-tecnicos').json(),list)


def test_reporte_no_duplica_tecnico_en_interfaz(client):
    html = client.get('/').text
    assert "tabla(t.map(({tecnico_id,...columnas})=>columnas))" in html
    respuesta = client.get('/reportes/tiempos-tecnicos')
    assert respuesta.status_code == 200
    # El backend conserva el ID para integraciones, la vista no lo repite.
    datos = respuesta.json()
    if datos:
        assert 'tecnico_id' in datos[0] and 'tecnico' in datos[0]


def test_mensaje_asignacion_tecnico_en_dashboard(client):
    html = client.get('/').text
    assert 'Técnico responsable:' in html
    assert 'tituloTecnico(respuesta.tecnico_id)' in html
    assert 'En proceso indica que se está atendiendo' in html

def test_dashboard_muestra_sla_historial_y_version(client):
    html=client.get('/').text
    assert 'Control de SLA' in html
    assert 'Historial del ticket' in html
    assert client.get('/openapi.json').json()['info']['version']=='2.0.0'
