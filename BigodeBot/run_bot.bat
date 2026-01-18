@echo off
cd /d %~dp0
if exist venv\Scripts\activate (
    call venv\Scripts\activate
)
echo Iniciando BigodeTexas Discord Bot...
python bot_main.py
pause
