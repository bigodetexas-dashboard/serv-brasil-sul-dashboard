# -*- coding: utf-8 -*-
"""
Módulo de Auto-Failover Autônomo
Detecta automaticamente quando monitor_logs.py para e assume controle.
Roda dentro do bot_main.py - 100% autônomo, sem intervenção humana.
"""

import os
import sys
import time
from datetime import datetime

# Adiciona raiz do projeto ao path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from utils.heartbeat import check_primary_alive, send_heartbeat
from utils.sync_manager import SyncManager


class AutoFailover:
    """Sistema autônomo de failover - detecta e age automaticamente"""

    def __init__(self):
        self.is_backup_mode = False
        self.check_interval = 30  # Verifica a cada 30 segundos
        self.primary_timeout = 120  # 2 minutos sem heartbeat = assumir controle
        self.sync_manager = SyncManager()
        self.last_check = None

    def should_activate_backup(self):
        """
        Verifica se deve ativar modo backup.
        Retorna True se monitor_logs.py está offline.
        """
        # Só verifica a cada 30 segundos para não sobrecarregar
        now = time.time()
        if self.last_check and (now - self.last_check) < self.check_interval:
            return self.is_backup_mode

        self.last_check = now

        # Verifica se sistema principal está vivo
        primary_alive = check_primary_alive(timeout_seconds=self.primary_timeout)

        if not primary_alive and not self.is_backup_mode:
            # Sistema principal morreu! Assumir controle!
            print("=" * 60)
            print("🚨 [AUTO-FAILOVER] SISTEMA PRINCIPAL OFFLINE DETECTADO!")
            print("🔄 [AUTO-FAILOVER] ATIVANDO MODO BACKUP AUTOMATICAMENTE...")
            print("=" * 60)
            self.is_backup_mode = True
            return True

        elif primary_alive and self.is_backup_mode:
            # Sistema principal voltou! Transferir controle!
            print("=" * 60)
            print("✅ [AUTO-FAILOVER] SISTEMA PRINCIPAL RECUPERADO!")
            print("🔄 [AUTO-FAILOVER] SINCRONIZANDO EVENTOS...")
            print("=" * 60)

            # Sincroniza eventos processados pelo backup
            if self.sync_manager.has_pending_sync():
                count = self.sync_manager.process_backup_events()
                print(f"✅ [AUTO-FAILOVER] {count} eventos sincronizados!")

            print("🔄 [AUTO-FAILOVER] TRANSFERINDO CONTROLE PARA SISTEMA PRINCIPAL...")
            print("=" * 60)
            self.is_backup_mode = False
            return False

        return self.is_backup_mode

    def send_backup_heartbeat(self):
        """Envia heartbeat indicando que backup está ativo"""
        if self.is_backup_mode:
            send_heartbeat("backup")

    def queue_event_if_backup(self, event_type, event_data):
        """
        Se estiver em modo backup, adiciona evento à fila de sincronização.

        Args:
            event_type (str): Tipo do evento
            event_data (dict): Dados do evento
        """
        if self.is_backup_mode:
            self.sync_manager.queue_event(event_type, event_data, "backup")


# Instância global para uso no bot_main.py
auto_failover = AutoFailover()
