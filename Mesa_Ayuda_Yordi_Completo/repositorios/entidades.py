from repositorios.base import RepositorioBase
class DepartamentosRepo(RepositorioBase):
    def __init__(self): super().__init__('departamentos',('nombre','ubicacion'))
class EquiposRepo(RepositorioBase):
    def __init__(self): super().__init__('equipos',('codigo_inventario','tipo','marca','modelo','departamento_id'))
class TecnicosRepo(RepositorioBase):
    def __init__(self): super().__init__('tecnicos',('nombre','especialidad','correo','activo'))
class TicketsRepo(RepositorioBase):
    def __init__(self): super().__init__('tickets',('equipo_id','descripcion','prioridad','estado','tecnico_id'))
class SeguimientosRepo(RepositorioBase):
    def __init__(self): super().__init__('seguimientos',('ticket_id','comentario'))
