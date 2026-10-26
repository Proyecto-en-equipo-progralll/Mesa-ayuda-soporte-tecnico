import os,tempfile,sqlite3,sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import database
from seguridad import hash_clave
from main import app
@pytest.fixture
def client(tmp_path,monkeypatch):
    db=str(tmp_path/'test.db');monkeypatch.setattr(database,'DB_PATH',db)
    # Los módulos importan una ruta dinámicamente en reportes; el resto usa conectar().
    with sqlite3.connect(db) as c:
        c.executescript((Path(__file__).resolve().parents[1]/'crear_bd.sql').read_text())
        c.execute('INSERT INTO usuarios(nombre_usuario,contrasena_hash,rol) VALUES(?,?,?)',('admin',hash_clave('test-password-123'),'administrador'))
    with TestClient(app) as cliente:
        r=cliente.post('/auth/login',json={'usuario':'admin','contrasena':'test-password-123'})
        cliente.headers['Authorization']='Bearer '+r.json()['access_token']
        yield cliente
