@echo off
setlocal
cd /d "%~dp0"
echo Instalando dependencias de Mesa de Ayuda...
python -m pip install -r requirements.txt
if errorlevel 1 (echo ERROR instalando dependencias.& pause & exit /b 1)
echo Instalacion terminada.
pause
