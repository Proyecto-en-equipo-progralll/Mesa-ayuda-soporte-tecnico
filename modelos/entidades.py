from dataclasses import dataclass
from datetime import datetime
@dataclass
class Entidad:
    id: int
@dataclass
class Departamento(Entidad):
    nombre: str
    ubicacion: str
@dataclass
class Equipo(Entidad):
    codigo_inventario: str
    tipo: str
    marca: str
    departamento_id: int
@dataclass
class Tecnico(Entidad):
    nombre: str
    especialidad: str
    correo: str
@dataclass
class Ticket(Entidad):
    equipo_id: int
    descripcion: str
    prioridad: str
    estado: str
    tecnico_id: int | None
    def puede_cerrarse(self, seguimientos: int) -> bool:
        return self.estado != 'cerrado' and seguimientos > 0
@dataclass
class Seguimiento(Entidad):
    ticket_id: int
    comentario: str
    fecha: datetime | None = None
@dataclass
class Usuario(Entidad):
    nombre_usuario: str
    rol: str
