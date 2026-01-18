@echo off
cd /d %~dp0
if exist venv\Scripts\activate (
    call venv\Scripts\activate
)
start /b pythonw launcher.py
exit
