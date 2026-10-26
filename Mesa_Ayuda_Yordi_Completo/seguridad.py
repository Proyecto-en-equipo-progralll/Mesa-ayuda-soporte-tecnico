import base64, hashlib, hmac, json, os, secrets, time
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from database import conectar
# Cambiar MESA_SECRET en producción; si no se indica, tokens caducan al reiniciar.
SECRET=os.environ.get('MESA_SECRET') or secrets.token_urlsafe(48)
bearer=HTTPBearer(auto_error=False)
def hash_clave(clave):
    salt=os.urandom(16)
    dk=hashlib.pbkdf2_hmac('sha256',clave.encode(),salt,310000)
    return 'pbkdf2_sha256$310000$'+salt.hex()+'$'+dk.hex()
def verificar(clave,almacenada):
    try:
        tipo,iteraciones,salt,digest=almacenada.split('$')
        if tipo!='pbkdf2_sha256': return False
        return hmac.compare_digest(hashlib.pbkdf2_hmac('sha256',clave.encode(),bytes.fromhex(salt),int(iteraciones)),bytes.fromhex(digest))
    except (ValueError,TypeError): return False
def token(usuario):
    data=base64.urlsafe_b64encode(json.dumps({'id':usuario['id'],'exp':int(time.time())+3600},separators=(',',':')).encode()).rstrip(b'=')
    firma=hmac.new(SECRET.encode(),data,hashlib.sha256).hexdigest()
    return data.decode()+'.'+firma
def actual(cred:HTTPAuthorizationCredentials|None=Depends(bearer)):
    err=HTTPException(401,'Debe iniciar sesion con un token valido',headers={'WWW-Authenticate':'Bearer'})
    if not cred: raise err
    try:
        data,firma=cred.credentials.split('.')
        if not hmac.compare_digest(hmac.new(SECRET.encode(),data.encode(),hashlib.sha256).hexdigest(),firma): raise err
        payload=json.loads(base64.urlsafe_b64decode(data+'='*(-len(data)%4)))
        if payload['exp']<time.time(): raise err
        with conectar() as c:
            user=c.execute('SELECT id,nombre_usuario,rol,tecnico_id FROM usuarios WHERE id=?',(payload['id'],)).fetchone()
        if not user: raise err
        return dict(user)
    except (ValueError,KeyError,UnicodeError,TypeError): raise err
def admin(user=Depends(actual)):
    if user['rol']!='administrador': raise HTTPException(403,'Solo administradores')
    return user
