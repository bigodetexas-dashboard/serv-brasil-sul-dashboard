@echo off
echo ========================================
echo   BigodeTexas Dashboard - Novo
echo ========================================
echo.
echo Iniciando servidor...
echo.

cd new_dashboard
start "BigodeTexas Server" python app.py

echo Aguardando servidor iniciar...
timeout /t 5 /nobreak > nul

echo Abrindo navegador...
start http://localhost:5001

echo.
echo ========================================
echo Dashboard aberto em: http://localhost:5001
echo Para parar o servidor, feche a janela "BigodeTexas Server"
echo ========================================
echo.
pause