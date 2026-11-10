from database import conectar
from sqlite3 import IntegrityError
class RepositorioBase:
    def __init__(self, tabla: str, columnas: tuple[str, ...]):
        self.tabla, self.columnas = tabla, columnas
    def listar(self, buscar: str = ''):
        with conectar() as c:
            if buscar:
                filtro = ' OR '.join(f'CAST({x} AS TEXT) LIKE ?' for x in self.columnas)
                return [dict(r) for r in c.execute(f'SELECT * FROM {self.tabla} WHERE {filtro} ORDER BY id DESC',tuple('%'+buscar+'%' for _ in self.columnas))]
            return [dict(r) for r in c.execute(f'SELECT * FROM {self.tabla} ORDER BY id DESC')]
    def obtener(self, id: int):
        with conectar() as c:
            r=c.execute(f'SELECT * FROM {self.tabla} WHERE id=?',(id,)).fetchone()
            return dict(r) if r else None
    def crear(self, datos: dict):
        keys=tuple(k for k in datos if k in self.columnas)
        if not keys: raise ValueError('No hay campos validos')
        marks=','.join('?' for _ in keys)
        with conectar() as c:
            cur=c.execute(f'INSERT INTO {self.tabla} ({",".join(keys)}) VALUES ({marks})',tuple(datos[k] for k in keys))
            id=cur.lastrowid
        return self.obtener(id)
    def actualizar(self,id:int,datos:dict):
        keys=tuple(k for k in datos if k in self.columnas)
        if not keys: raise ValueError('No hay campos para actualizar')
        with conectar() as c:
            cur=c.execute(f'UPDATE {self.tabla} SET '+','.join(f'{k}=?' for k in keys)+' WHERE id=?',tuple(datos[k] for k in keys)+(id,))
            return cur.rowcount>0
    def eliminar(self,id:int):
        with conectar() as c:
            cur=c.execute(f'DELETE FROM {self.tabla} WHERE id=?',(id,))
            return cur.rowcount>0
