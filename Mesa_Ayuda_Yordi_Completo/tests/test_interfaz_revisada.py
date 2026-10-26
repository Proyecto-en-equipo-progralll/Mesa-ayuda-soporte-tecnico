def test_uml_incluido():
    from pathlib import Path
    carpeta=Path(__file__).resolve().parents[1]/'DOCUMENTACION'/'UML_APROBADO'
    assert (carpeta/'UML_Clases_En_Espanol.png').stat().st_size > 10000

def test_interfaz_sin_edicion_ticket_cerrado(client):
    html=client.get('/').text
    assert 'columnasVista' in html
    assert "r.estado==='cerrado'" in html
    assert 'Los tickets cerrados no pueden editarse' in html

def test_boton_recarga(client):
    assert 'id="refrescar"' in client.get('/').text
