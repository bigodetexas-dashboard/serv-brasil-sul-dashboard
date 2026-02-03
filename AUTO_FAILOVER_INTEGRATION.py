# -*- coding: utf-8 -*-
"""
Task de Auto-Failover para Discord Bot
Adicione este código ao bot_main.py para ativar failover automático.
"""

# ==================== ADICIONAR NO INÍCIO DO ARQUIVO (após imports) ====================

from utils.auto_failover import auto_failover

# ==================== ADICIONAR APÓS @bot.event async def on_ready() ====================


@tasks.loop(seconds=30)
async def auto_failover_check():
    """
    Task que roda a cada 30 segundos verificando se monitor_logs.py está ativo.
    Se não estiver, ativa modo backup automaticamente.
    """
    try:
        # Verifica se deve ativar backup
        should_backup = auto_failover.should_activate_backup()

        # Envia heartbeat se estiver em modo backup
        if should_backup:
            auto_failover.send_backup_heartbeat()

    except Exception as e:
        print(f"[AUTO-FAILOVER] Erro na verificação: {e}")


@auto_failover_check.before_loop
async def before_auto_failover():
    """Aguarda o bot estar pronto antes de iniciar o failover"""
    await bot.wait_until_ready()
    print("🔄 [AUTO-FAILOVER] Sistema de failover autônomo iniciado!")
    print("👁️ [AUTO-FAILOVER] Monitorando monitor_logs.py a cada 30 segundos...")


# ==================== MODIFICAR A FUNÇÃO parse_log_line ====================

# No início da função parse_log_line, adicionar:


def parse_log_line(line):
    """Parse de uma linha de log do DayZ."""

    # 🔄 AUTO-FAILOVER: Se não estiver em modo backup, não processar
    if not auto_failover.should_activate_backup():
        return  # Sistema principal está ativo, não fazer nada

    # Resto do código normal...
    # (continua com o código existente)


# ==================== NO FINAL DO ARQUIVO (antes de bot.run) ====================

# Iniciar task de auto-failover
auto_failover_check.start()

# Resto do código...
bot.run(TOKEN)
