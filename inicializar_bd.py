import sqlite3
from pathlib import Path
from database import DB_PATH
from seguridad import hash_clave
ruta=Path(DB_PATH)
if ruta.exists():
    respuesta=input('ATENCION: se perderan datos existentes. Escribe RECREAR para continuar: ')
    if respuesta!='RECREAR': raise SystemExit('Cancelado, no se modifico la base')
import getpass
usuario=input('Nombre del administrador inicial [admin]: ').strip() or 'admin'
clave=getpass.getpass('Contrasena inicial del administrador (min. 10 caracteres): ')
if len(clave)<10: raise SystemExit('Contrasena demasiado corta: minimo 10 caracteres')
with sqlite3.connect(ruta) as c:
    c.executescript((Path(__file__).parent/'crear_bd.sql').read_text(encoding='utf-8'))
    c.execute('INSERT INTO usuarios (nombre_usuario,contrasena_hash,rol) VALUES(?,?,?)',(usuario,hash_clave(clave),'administrador'))
print('Base creada y administrador registrado en',ruta)
