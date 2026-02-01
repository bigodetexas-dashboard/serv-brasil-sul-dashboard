@echo off
REM ============================================
REM Script para Aplicar Schema no Banco de Dados
REM ============================================

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                              ║
echo ║                    🗄️  APLICANDO SCHEMA NO BANCO DE DADOS                    ║
echo ║                                                                              ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

REM Verificar se o arquivo de schema existe
if not exist "schema_achievements_history.sql" (
    echo ❌ ERRO: Arquivo schema_achievements_history.sql não encontrado!
    echo.
    echo Por favor, certifique-se de estar no diretório correto.
    pause
    exit /b 1
)

echo ✅ Arquivo de schema encontrado!
echo.

REM Verificar se DATABASE_URL está definido
if "%DATABASE_URL%"=="" (
    echo ⚠️  AVISO: DATABASE_URL não está definido!
    echo.
    echo Por favor, defina a variável de ambiente DATABASE_URL ou edite este script.
    echo.
    echo Exemplo:
    echo set DATABASE_URL=postgresql://user:password@host:port/database
    echo.
    pause
    exit /b 1
)

echo ✅ DATABASE_URL encontrado!
echo.
echo 📋 Aplicando schema...
echo.

REM Aplicar o schema
psql "%DATABASE_URL%" -f schema_achievements_history.sql

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ╔══════════════════════════════════════════════════════════════════════════════╗
    echo ║                                                                              ║
    echo ║                    ✅ SCHEMA APLICADO COM SUCESSO!                           ║
    echo ║                                                                              ║
    echo ╚══════════════════════════════════════════════════════════════════════════════╝
    echo.
    echo 📊 O que foi criado:
    echo    - Tabela: achievements (18 conquistas pré-cadastradas)
    echo    - Tabela: user_achievements
    echo    - Tabela: activity_history
    echo    - Tabela: user_settings
    echo    - Funções: update_achievement_progress(), add_activity_event()
    echo    - Views: v_user_achievements_full, v_user_achievement_stats
    echo.
    echo 🎉 Sistema pronto para uso!
    echo.
) else (
    echo.
    echo ╔══════════════════════════════════════════════════════════════════════════════╗
    echo ║                                                                              ║
    echo ║                    ❌ ERRO AO APLICAR SCHEMA!                                ║
    echo ║                                                                              ║
    echo ╚══════════════════════════════════════════════════════════════════════════════╝
    echo.
    echo Possíveis causas:
    echo    1. DATABASE_URL incorreto
    echo    2. Banco de dados não acessível
    echo    3. Permissões insuficientes
    echo    4. PostgreSQL não instalado
    echo.
)

pause
