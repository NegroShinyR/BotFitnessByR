@echo off
title Chatbot Fitness

echo ==========================
echo INICIANDO CHATBOT FITNESS
echo ==========================

cd /d "%~dp0"

if not exist venv (
    echo Creando entorno virtual...
    python -m venv venv
)

call venv\Scripts\activate

pip install -r requirements.txt

python -m app.bot

pause