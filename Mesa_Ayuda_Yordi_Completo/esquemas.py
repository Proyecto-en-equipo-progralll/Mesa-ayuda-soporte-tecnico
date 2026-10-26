from pydantic import BaseModel, Field, ConfigDict
from typing import Literal
class Entrada(BaseModel):
    model_config=ConfigDict(extra='forbid',str_strip_whitespace=True)
class DepartamentoIn(Entrada):
    nombre:str=Field(min_length=2)
    ubicacion:str=Field(min_length=2)
class EquipoIn(Entrada):
    codigo_inventario:str=Field(min_length=2)
    tipo:str=Field(min_length=2)
    marca:str=Field(min_length=2)
    modelo:str|None=None
    departamento_id:int=Field(gt=0)
class TecnicoIn(Entrada):
    nombre:str=Field(min_length=2)
    especialidad:str=Field(min_length=2)
    correo:str=Field(min_length=3)
    activo:Literal[0,1]=1
class TicketIn(Entrada):
    equipo_id:int=Field(gt=0)
    descripcion:str=Field(min_length=3)
    prioridad:Literal['baja','media','alta']
class TicketUpdate(Entrada):
    equipo_id:int|None=Field(default=None,gt=0)
    descripcion:str|None=Field(default=None,min_length=3)
    prioridad:Literal['baja','media','alta']|None=None
    estado:Literal['abierto','en_proceso','cerrado']|None=None
class SeguimientoIn(Entrada):
    ticket_id:int=Field(gt=0)
    comentario:str=Field(min_length=2)
class Credenciales(Entrada):
    usuario:str
    contrasena:str
class UsuarioNuevo(Entrada):
    usuario:str=Field(min_length=3)
    contrasena:str=Field(min_length=10)
    rol:Literal['administrador','tecnico']='tecnico'
    tecnico_id:int|None=None
