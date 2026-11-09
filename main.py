from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import FileResponse
from routers.auth import router as auth
from routers.crud import router as crud
from routers.reportes import router as reportes
from migraciones import actualizar_esquema
@asynccontextmanager
async def ciclo_vida(app):
    actualizar_esquema()
    yield

app=FastAPI(title='Mesa de Ayuda - Soporte Tecnico',version='2.0.0',lifespan=ciclo_vida)
app.include_router(auth);app.include_router(crud);app.include_router(reportes)
@app.get('/',include_in_schema=False)
def inicio():return FileResponse(Path(__file__).parent/'static'/'index.html')
