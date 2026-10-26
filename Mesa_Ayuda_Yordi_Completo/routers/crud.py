import sqlite3
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from repositorios.entidades import DepartamentosRepo,EquiposRepo,TecnicosRepo,TicketsRepo,SeguimientosRepo
from esquemas import DepartamentoIn,EquipoIn,TecnicoIn,TicketIn,TicketUpdate,SeguimientoIn
from seguridad import actual,admin
from servicios import asignar_ticket,cambiar_ticket
router=APIRouter(tags=['Gestion'])
CONFIG={'departamentos':(DepartamentosRepo(),DepartamentoIn),'equipos':(EquiposRepo(),EquipoIn),'tecnicos':(TecnicosRepo(),TecnicoIn),'seguimientos':(SeguimientosRepo(),SeguimientoIn)}
def problema(error):
    txt=str(error)
    if 'FOREIGN KEY' in txt: return HTTPException(400,'Registro relacionado inexistente o tiene referencias que impiden eliminarlo')
    if 'UNIQUE' in txt: return HTTPException(400,'Ya existe un registro con ese dato unico')
    return HTTPException(400,txt)

def validar_seguimiento(ticket_id:int):
    ticket=TicketsRepo().obtener(ticket_id)
    if ticket is None: raise HTTPException(404,'Ticket no encontrado')
    if ticket['estado']=='cerrado': raise HTTPException(400,'No se pueden cambiar seguimientos de un ticket cerrado')

def registrar_crud(nombre,repo,esquema):
    def lista(buscar:str='', usuario=Depends(actual)): return repo.listar(buscar)
    def detalle(id:int,usuario=Depends(actual)):
        x=repo.obtener(id)
        if x is None: raise HTTPException(404,'Registro no encontrado')
        return x
    def crear(datos:esquema,usuario=Depends(actual)):
        if nombre=='seguimientos': validar_seguimiento(datos.ticket_id)
        try: return repo.crear(datos.model_dump())
        except sqlite3.IntegrityError as ex: raise problema(ex)
    def editar(id:int,datos:esquema,usuario=Depends(actual)):
        if nombre=='seguimientos':
            anterior=repo.obtener(id)
            if anterior is None: raise HTTPException(404,'Registro no encontrado')
            validar_seguimiento(anterior['ticket_id'])
            validar_seguimiento(datos.ticket_id)
        try:
            if not repo.actualizar(id,datos.model_dump()): raise HTTPException(404,'Registro no encontrado')
            return repo.obtener(id)
        except sqlite3.IntegrityError as ex: raise problema(ex)
    def borrar(id:int,usuario=Depends(admin)):
        if nombre=='seguimientos':
            anterior=repo.obtener(id)
            if anterior is None: raise HTTPException(404,'Registro no encontrado')
            validar_seguimiento(anterior['ticket_id'])
        try:
            if not repo.eliminar(id): raise HTTPException(404,'Registro no encontrado')
            return {'mensaje':'Eliminado'}
        except sqlite3.IntegrityError as ex: raise problema(ex)
    router.add_api_route('/'+nombre,lista,methods=['GET'],name='Listar '+nombre)
    router.add_api_route('/'+nombre+'/{id}',detalle,methods=['GET'],name='Consultar '+nombre)
    router.add_api_route('/'+nombre,crear,methods=['POST'],status_code=201,name='Crear '+nombre)
    router.add_api_route('/'+nombre+'/{id}',editar,methods=['PUT'],name='Editar '+nombre)
    router.add_api_route('/'+nombre+'/{id}',borrar,methods=['DELETE'],name='Eliminar '+nombre)
for nom,(repo,esquema) in CONFIG.items(): registrar_crud(nom,repo,esquema)
repo_t=TicketsRepo()
@router.get('/tickets')
def tickets(buscar:str='',usuario=Depends(actual)): return repo_t.listar(buscar)
@router.get('/tickets/{id}')
def ticket(id:int,usuario=Depends(actual)):
    x=repo_t.obtener(id)
    if not x: raise HTTPException(404,'Ticket no encontrado')
    return x
@router.post('/tickets',status_code=201)
def nuevo_ticket(datos:TicketIn,usuario=Depends(actual)): return asignar_ticket(datos.model_dump())
@router.put('/tickets/{id}')
def editar_ticket(id:int,datos:TicketUpdate,usuario=Depends(actual)):
    try: return cambiar_ticket(id,datos.model_dump(exclude_unset=True))
    except sqlite3.IntegrityError as ex: raise problema(ex)
@router.delete('/tickets/{id}')
def borrar_ticket(id:int,usuario=Depends(admin)):
    try:
        if not repo_t.eliminar(id): raise HTTPException(404,'Ticket no encontrado')
        return {'mensaje':'Ticket eliminado'}
    except sqlite3.IntegrityError as ex: raise problema(ex)
