@echo off
setlocal
cd /d "%~dp0"
echo ===============================================
echo MESA DE AYUDA - INICIAR SERVIDOR
 echo ===============================================
if not exist "mesa_ayuda.db" (
  echo No hay base de datos. Se ejecutara la inicializacion inicial.
  python inicializar_bd.py
  if errorlevel 1 (echo ERROR inicializando la base de datos.& pause & exit /b 1)
)
python -m uvicorn main:app --reload
if errorlevel 1 (echo No se pudo iniciar. Revisa dependencias con INSTALAR_WINDOWS.bat.& pause)
