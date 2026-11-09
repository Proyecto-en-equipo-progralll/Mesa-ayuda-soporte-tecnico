from database import conectar
from seguridad import hash_clave
import getpass
nombre=input("Nombre de usuario [admin]: ").strip() or "admin"
clave=getpass.getpass("Nueva contrasena (min. 10 caracteres): ")
if len(clave)<10: raise SystemExit("La contrasena debe tener al menos 10 caracteres")
with conectar() as con:
    resultado=con.execute("UPDATE usuarios SET contrasena_hash=? WHERE nombre_usuario=?", (hash_clave(clave),nombre))
    if not resultado.rowcount: raise SystemExit("Usuario no encontrado")
print("Contrasena cambiada. Elimina ACCESO_INICIAL.txt si estaba guardado.")
