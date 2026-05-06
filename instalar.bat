@echo off
echo ===============================
echo Instalando Validador Nubceo...
echo ===============================

python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo ❌ Python no esta instalado
    echo 👉 Descargar de https://www.python.org/downloads/
    pause
    exit
)

python -m venv venv

call venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ✅ Instalacion completa
echo 👉 Ahora ejecuta iniciar.bat
pause