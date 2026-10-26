import sqlite3
from fastapi import APIRouter,Depends,HTTPException
from esquemas import Credenciales,UsuarioNuevo
from seguridad import actual,admin,hash_clave,verificar,token
from database import conectar
router=APIRouter(prefix='/auth',tags=['Autenticacion'])
@router.post('/login')
def login(datos:Credenciales):
    with conectar() as c: u=c.execute('SELECT * FROM usuarios WHERE nombre_usuario=?',(datos.usuario,)).fetchone()
    if not u or not verificar(datos.contrasena,u['contrasena_hash']): raise HTTPException(401,'Usuario o contrasena incorrectos')
    return {'access_token':token(dict(u)),'token_type':'bearer','expires_in':3600}
@router.get('/yo')
def yo(u=Depends(actual)): return u
@router.post('/usuarios',status_code=201)
def nuevo_usuario(datos:UsuarioNuevo,u=Depends(admin)):
    try:
        with conectar() as c:
            cur=c.execute('INSERT INTO usuarios(nombre_usuario,contrasena_hash,rol,tecnico_id) VALUES(?,?,?,?)',
                (datos.usuario,hash_clave(datos.contrasena),datos.rol,datos.tecnico_id))
            return {'id':cur.lastrowid,'usuario':datos.usuario,'rol':datos.rol}
    except sqlite3.IntegrityError: raise HTTPException(400,'Usuario duplicado o tecnico inexistente/ocupado')
