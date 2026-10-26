from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from routers.auth import router as auth
from routers.crud import router as crud
from routers.reportes import router as reportes
app=FastAPI(title='Mesa de Ayuda - Soporte Tecnico',version='1.0.0')
app.include_router(auth);app.include_router(crud);app.include_router(reportes)
@app.get('/',include_in_schema=False)
def inicio():return FileResponse(Path(__file__).parent/'static'/'index.html')
