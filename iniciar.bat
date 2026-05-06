@echo off
cd /d %~dp0

echo ===============================
echo Iniciando Validador Nubceo...
echo ===============================

call venv\Scripts\activate

streamlit run app.py

pause