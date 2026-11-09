@echo off
setlocal
cd /d "%~dp0"
echo ===============================================
echo MESA DE AYUDA - INICIAR SERVIDOR
 echo ===============================================
set "INICIALIZAR=0"
if not exist "mesa_ayuda.db" set "INICIALIZAR=1"
if exist "mesa_ayuda.db" for %%A in ("mesa_ayuda.db") do if %%~zA EQU 0 set "INICIALIZAR=1"
if "%INICIALIZAR%"=="1" (
  echo No hay una base de datos valida (archivo inexistente o vacio).
  echo Se ejecutara la inicializacion para crear las tablas y el administrador.
  python inicializar_bd.py
  if errorlevel 1 (echo ERROR inicializando la base de datos.& pause & exit /b 1)
)
python -m uvicorn main:app --reload
if errorlevel 1 (echo No se pudo iniciar. Revisa dependencias con INSTALAR_WINDOWS.bat.& pause)
