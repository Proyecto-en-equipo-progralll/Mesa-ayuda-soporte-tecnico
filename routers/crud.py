import sqlite3
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from repositorios.entidades import DepartamentosRepo,EquiposRepo,TecnicosRepo,TicketsRepo,SeguimientosRepo,MantenimientosRepo
from esquemas import DepartamentoIn,EquipoIn,TecnicoIn,TicketIn,TicketUpdate,SeguimientoIn,MantenimientoIn
from seguridad import actual,admin
from servicios import asignar_ticket,cambiar_ticket
from migraciones import registrar_evento
from database import conectar
router=APIRouter(tags=['Gestion'])
CONFIG={'departamentos':(DepartamentosRepo(),DepartamentoIn),'equipos':(EquiposRepo(),EquipoIn),'tecnicos':(TecnicosRepo(),TecnicoIn),'seguimientos':(SeguimientosRepo(),SeguimientoIn),'mantenimientos':(MantenimientosRepo(),MantenimientoIn)}
def problema(error):
    txt=str(error)
    if 'FOREIGN KEY' in txt: return HTTPException(400,'Registro relacionado inexistente o tiene referencias que impiden eliminarlo')
    if 'UNIQUE' in txt: return HTTPException(400,'Ya existe un registro con ese dato unico')
    return HTTPException(400,txt)

def validar_propiedad(ticket_id:int, usuario):
    ticket=TicketsRepo().obtener(ticket_id)
    if ticket is None: raise HTTPException(404,'Ticket no encontrado')
    if usuario['rol']=='tecnico' and ticket['tecnico_id']!=usuario.get('tecnico_id'):
        raise HTTPException(403,'Solo puedes consultar o modificar tus propios tickets')
    return ticket

def validar_seguimiento(ticket_id:int, usuario=None):
    ticket=TicketsRepo().obtener(ticket_id)
    if ticket is None: raise HTTPException(404,'Ticket no encontrado')
    if usuario is not None: validar_propiedad(ticket_id,usuario)
    if ticket['estado']=='cerrado': raise HTTPException(400,'No se pueden cambiar seguimientos de un ticket cerrado')

def registrar_crud(nombre,repo,esquema):
    def lista(buscar:str='', usuario=Depends(actual)):
        if nombre=='seguimientos' and usuario['rol']=='tecnico':
            with conectar() as c:
                x=c.execute('SELECT s.* FROM seguimientos s JOIN tickets t ON t.id=s.ticket_id WHERE s.id=? AND t.tecnico_id=?',(id,usuario.get('tecnico_id'))).fetchone()
                if x is None: raise HTTPException(404,'Registro no encontrado')
                return dict(x)
        if nombre=='mantenimientos' and usuario['rol']=='tecnico':
            if not usuario.get('tecnico_id'): raise HTTPException(403,'Cuenta técnica sin técnico vinculado')
            with conectar() as c: return [dict(r) for r in c.execute('SELECT * FROM mantenimientos WHERE tecnico_id=? ORDER BY id DESC',(usuario['tecnico_id'],))]
        if nombre=='seguimientos' and usuario['rol']=='tecnico':
            with conectar() as c: return [dict(r) for r in c.execute('SELECT s.* FROM seguimientos s JOIN tickets t ON t.id=s.ticket_id WHERE t.tecnico_id=? ORDER BY s.id DESC',(usuario.get('tecnico_id'),))]
        return repo.listar(buscar)
    def detalle(id:int,usuario=Depends(actual)):
        if nombre=='mantenimientos' and usuario['rol']!='administrador':
            with conectar() as c:
                x=c.execute('SELECT * FROM mantenimientos WHERE id=? AND tecnico_id=?',(id,usuario.get('tecnico_id'))).fetchone()
                if x is None: raise HTTPException(404,'Registro no encontrado')
                return dict(x)
        x=repo.obtener(id)
        if x is None: raise HTTPException(404,'Registro no encontrado')
        return x
    def crear(datos:esquema,usuario=Depends(actual)):
        if nombre=='mantenimientos' and usuario['rol']!='administrador': raise HTTPException(403,'Solo administradores pueden programar mantenimientos')
        if nombre=='seguimientos': validar_seguimiento(datos.ticket_id,usuario)
        try:
            creado=repo.crear(datos.model_dump())
            if nombre=='seguimientos': registrar_evento(datos.ticket_id,'Seguimiento agregado',datos.comentario,usuario['nombre_usuario'])
            return creado
        except sqlite3.IntegrityError as ex: raise problema(ex)
    def editar(id:int,datos:esquema,usuario=Depends(actual)):
        if nombre=='mantenimientos' and usuario['rol']!='administrador': raise HTTPException(403,'Solo administradores pueden modificar mantenimientos')
        if nombre=='seguimientos':
            anterior=repo.obtener(id)
            if anterior is None: raise HTTPException(404,'Registro no encontrado')
            validar_seguimiento(anterior['ticket_id'],usuario)
            validar_seguimiento(datos.ticket_id,usuario)
        try:
            if not repo.actualizar(id,datos.model_dump()): raise HTTPException(404,'Registro no encontrado')
            return repo.obtener(id)
        except sqlite3.IntegrityError as ex: raise problema(ex)
    def borrar(id:int,usuario=Depends(admin)):
        if nombre=='seguimientos':
            anterior=repo.obtener(id)
            if anterior is None: raise HTTPException(404,'Registro no encontrado')
            validar_seguimiento(anterior['ticket_id'],usuario)
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
def tickets(buscar:str='',usuario=Depends(actual)):
    if usuario['rol']=='administrador': return repo_t.listar(buscar)
    if not usuario.get('tecnico_id'): raise HTTPException(403,'La cuenta no está vinculada a un técnico')
    with conectar() as c:
        q="SELECT * FROM tickets WHERE tecnico_id=? AND (descripcion LIKE ? OR prioridad LIKE ? OR estado LIKE ?) ORDER BY id DESC"
        return [dict(r) for r in c.execute(q,(usuario['tecnico_id'],f'%{buscar}%',f'%{buscar}%',f'%{buscar}%'))]
@router.get('/tickets/{id}')
def ticket(id:int,usuario=Depends(actual)):
    x=repo_t.obtener(id)
    if not x: raise HTTPException(404,'Ticket no encontrado')
    validar_propiedad(id,usuario)
    return x
@router.post('/tickets',status_code=201)
def nuevo_ticket(datos:TicketIn,usuario=Depends(actual)): return asignar_ticket(datos.model_dump(),usuario['nombre_usuario'])
@router.put('/tickets/{id}')
def editar_ticket(id:int,datos:TicketUpdate,usuario=Depends(actual)):
    validar_propiedad(id,usuario)
    try: return cambiar_ticket(id,datos.model_dump(exclude_unset=True),usuario['nombre_usuario'])
    except sqlite3.IntegrityError as ex: raise problema(ex)
@router.delete('/tickets/{id}')
def borrar_ticket(id:int,usuario=Depends(admin)):
    try:
        if not repo_t.eliminar(id): raise HTTPException(404,'Ticket no encontrado')
        return {'mensaje':'Ticket eliminado'}
    except sqlite3.IntegrityError as ex: raise problema(ex)


@router.get('/tickets/{id}/historial')
def historial_ticket(id:int, usuario=Depends(actual)):
    if not repo_t.obtener(id): raise HTTPException(404,'Ticket no encontrado')
    validar_propiedad(id,usuario)
    with conectar() as c:
        return [dict(r) for r in c.execute('SELECT id,ticket_id,usuario,accion,detalle,fecha FROM eventos_ticket WHERE ticket_id=? ORDER BY fecha DESC,id DESC',(id,))]

@router.get('/mis-tickets')
def mis_tickets(usuario=Depends(actual)):
    if usuario['rol']=='administrador':
        return repo_t.listar()
    if not usuario.get('tecnico_id'):
        raise HTTPException(403,'La cuenta no está vinculada a un técnico')
    with conectar() as c:
        return [dict(r) for r in c.execute('SELECT * FROM tickets WHERE tecnico_id=? ORDER BY id DESC',(usuario['tecnico_id'],))]
