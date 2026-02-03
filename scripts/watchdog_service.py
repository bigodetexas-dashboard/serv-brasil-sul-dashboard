# -*- coding: utf-8 -*-
"""
Watchdog Service - Sistema de Failover Inteligente
Monitora saúde dos sistemas e gerencia transições automáticas.
"""

import time
import subprocess
import sys
import os
from datetime import datetime

# Adiciona raiz do projeto ao path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from utils.heartbeat import check_primary_alive, get_system_status, mark_system_failed
from utils.sync_manager import SyncManager


class WatchdogService:
    """Serviço de monitoramento e failover automático"""

    def __init__(self):
        self.primary_process = None
        self.backup_process = None
        self.check_interval = 30  # Verifica a cada 30 segundos
        self.primary_timeout = 120  # 2 minutos sem heartbeat = falha
        self.sync_manager = SyncManager()

    def log(self, message, level="INFO"):
        """Log com timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prefix = {
            "INFO": "ℹ️",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "SUCCESS": "✅",
            "CRITICAL": "🚨",
        }.get(level, "📝")

        print(f"[{timestamp}] {prefix} [WATCHDOG] {message}")

    def check_primary_health(self):
        """Verifica se sistema principal está saudável"""
        return check_primary_alive(timeout_seconds=self.primary_timeout)

    def start_primary(self):
        """Inicia sistema principal"""
        if self.primary_process is None or self.primary_process.poll() is not None:
            self.log("Iniciando sistema principal (monitor_logs.py)...", "INFO")

            try:
                self.primary_process = subprocess.Popen(
                    [
                        sys.executable,
                        os.path.join(PROJECT_ROOT, "scripts", "monitor_logs.py"),
                    ],
                    cwd=PROJECT_ROOT,
                )
                self.log("Sistema principal iniciado!", "SUCCESS")
                return True
            except Exception as e:
                self.log(f"Erro ao iniciar sistema principal: {e}", "ERROR")
                return False
        else:
            self.log("Sistema principal já está rodando", "INFO")
            return True

    def start_backup(self):
        """Inicia sistema backup"""
        if self.backup_process is None or self.backup_process.poll() is not None:
            self.log("Iniciando sistema backup (bot_main.py)...", "WARNING")

            try:
                self.backup_process = subprocess.Popen(
                    [sys.executable, os.path.join(PROJECT_ROOT, "bot_main.py")],
                    cwd=PROJECT_ROOT,
                    env={**os.environ, "BACKUP_MODE": "1"},  # Sinaliza modo backup
                )
                self.log("Sistema backup ativado! Assumindo controle...", "CRITICAL")
                return True
            except Exception as e:
                self.log(f"Erro ao iniciar sistema backup: {e}", "ERROR")
                return False
        else:
            self.log("Sistema backup já está rodando", "INFO")
            return True

    def stop_backup(self):
        """Para sistema backup"""
        if self.backup_process and self.backup_process.poll() is None:
            self.log("Parando sistema backup...", "INFO")

            try:
                self.backup_process.terminate()
                self.backup_process.wait(timeout=10)
                self.backup_process = None
                self.log("Sistema backup parado", "SUCCESS")
                return True
            except Exception as e:
                self.log(f"Erro ao parar sistema backup: {e}", "ERROR")
                try:
                    self.backup_process.kill()
                    self.backup_process = None
                except:
                    pass
                return False
        return True

    def sync_backup_events(self):
        """Sincroniza eventos processados pelo backup"""
        self.log("Verificando eventos para sincronização...", "INFO")

        if self.sync_manager.has_pending_sync():
            self.log(
                "Eventos pendentes detectados! Iniciando sincronização...", "WARNING"
            )
            count = self.sync_manager.process_backup_events()
            self.log(f"Sincronização concluída: {count} eventos processados", "SUCCESS")
        else:
            self.log("Nenhum evento pendente de sincronização", "INFO")

    def run(self):
        """Loop principal do watchdog"""
        self.log("=== WATCHDOG SERVICE INICIADO ===", "SUCCESS")
        self.log(f"Intervalo de verificação: {self.check_interval}s", "INFO")
        self.log(f"Timeout do sistema principal: {self.primary_timeout}s", "INFO")

        # Inicia sistema principal
        self.start_primary()

        primary_was_down = False

        while True:
            try:
                time.sleep(self.check_interval)

                # Verifica saúde do sistema principal
                primary_alive = self.check_primary_health()

                if not primary_alive:
                    if not primary_was_down:
                        # Primeira detecção de falha
                        self.log("SISTEMA PRINCIPAL NÃO RESPONDE!", "CRITICAL")
                        mark_system_failed("primary")
                        primary_was_down = True

                    # Ativa backup
                    self.start_backup()

                else:
                    # Sistema principal está saudável
                    if primary_was_down:
                        # Sistema principal recuperou!
                        self.log("SISTEMA PRINCIPAL RECUPERADO!", "SUCCESS")

                        # Sincroniza eventos do backup
                        self.sync_backup_events()

                        # Para backup
                        self.stop_backup()

                        primary_was_down = False

                    # Verifica se backup está rodando indevidamente
                    if self.backup_process and self.backup_process.poll() is None:
                        self.log(
                            "Backup rodando com principal ativo. Parando backup...",
                            "WARNING",
                        )
                        self.stop_backup()

                # Limpa eventos antigos (uma vez por dia)
                current_hour = datetime.now().hour
                if current_hour == 3:  # 3 AM
                    self.sync_manager.clear_old_events(days=7)

            except KeyboardInterrupt:
                self.log("Interrupção detectada. Encerrando...", "WARNING")
                break
            except Exception as e:
                self.log(f"Erro no loop principal: {e}", "ERROR")
                import traceback

                traceback.print_exc()

        # Cleanup
        self.log("Encerrando sistemas...", "INFO")
        if self.primary_process:
            self.primary_process.terminate()
        if self.backup_process:
            self.backup_process.terminate()

        self.log("=== WATCHDOG SERVICE ENCERRADO ===", "INFO")


if __name__ == "__main__":
    watchdog = WatchdogService()
    watchdog.run()
