@echo off
echo ========================================
echo   BACKUP DE SEGURANCA - BigodeBot
echo ========================================
echo.

set timestamp=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set timestamp=%timestamp: =0%
set backupDir=backups\backup_pre_finalizacao_%timestamp%

echo Criando backup em: %backupDir%
echo.

mkdir "%backupDir%" 2>nul

echo Copiando arquivos do dashboard...
xcopy /E /I /Y "new_dashboard" "%backupDir%\new_dashboard" >nul

echo Copiando arquivos SQL...
copy /Y "*.sql" "%backupDir%\" >nul 2>nul

echo Copiando scripts Python importantes...
copy /Y "apply_*.py" "%backupDir%\" >nul 2>nul
copy /Y "check_*.py" "%backupDir%\" >nul 2>nul
copy /Y "database.py" "%backupDir%\" >nul 2>nul

echo.
echo ========================================
echo BACKUP CONCLUIDO COM SUCESSO!
echo Local: %backupDir%
echo ========================================
echo.

pause