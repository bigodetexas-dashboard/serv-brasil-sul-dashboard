# -*- coding: utf-8 -*-
"""
Parser de logs do servidor DayZ
Extrai informacoes de conexao dos jogadores
"""

import re
from datetime import datetime
from ftplib import FTP  # nosec B402 - Legacy log parser, consider migrating to FTP_TLS
import os
from dotenv import load_dotenv

load_dotenv()


class DayZLogParser:
    """Extrai informacoes de conexao dos logs do servidor"""

    def __init__(self):
        self.ftp_host = os.getenv("FTP_HOST")
        self.ftp_user = os.getenv("FTP_USER")
        self.ftp_pass = os.getenv("FTP_PASS")
        self.ftp_port = int(os.getenv("FTP_PORT", 21))
        self.log_path = "/dayzxb_missions/dayzOffline.chernarusplus/ADM.log"

    def fetch_logs(self, local_file="server_logs.txt"):
        """Baixa logs do servidor via FTP"""
        try:
            print(f"[LOG PARSER] Conectando ao FTP: {self.ftp_host}")
            ftp = FTP()  # nosec B321 - Legacy compatibility, consider upgrading to FTP_TLS
            ftp.connect(self.ftp_host, self.ftp_port, timeout=30)
            ftp.login(self.ftp_user, self.ftp_pass)

            print(f"[LOG PARSER] Baixando: {self.log_path}")
            with open(local_file, "wb") as f:
                ftp.retrbinary(f"RETR {self.log_path}", f.write)

            ftp.quit()
            print(f"[LOG PARSER] Log salvo em: {local_file}")
            return True

        except Exception as e:
            print(f"[LOG PARSER] Erro ao baixar logs: {e}")
            return False

    def parse_connections(self, log_file="server_logs.txt"):
        """Extrai conexoes do arquivo de log"""
        connections = []

        # Padroes possiveis de log DayZ (com player ID)
        patterns = [
            # Padrao 1: Player "Name" (id=76561198123456789 ip=192.168.1.100:12345)
            r'Player "([^"]+)".*id=([0-9]+).*ip=([0-9.]+):(\d+)',
            # Padrao 2: Player "Name" (ip=192.168.1.100:12345) - sem ID
            r'Player "([^"]+)".*ip=([0-9.]+):(\d+)',
            # Padrao 3: Connected: Name | IP: 192.168.1.100
            r"Connected:\s*([^\|]+)\s*\|\s*IP:\s*([0-9.]+)",
            # Padrao 4: [timestamp] Name connected from 192.168.1.100
            r"\]\s*([^\s]+)\s+connected from\s+([0-9.]+)",
            # Padrao 5: Name (192.168.1.100) connected
            r"([^\s]+)\s+\(([0-9.]+)\)\s+connected",
            # Padrao 6: Player "Name" (id=...) placed Base_Fence at [x, y, z]
            r'Player "([^"]+)".*placed\s+([A-Za-z0-9_]+)\s+at\s+\[([0-9.-]+),\s*([0-9.-]+),\s*([0-9.-]+)\]',
            # Padrao 7: Player "Name" (id=...) killed Zombie
            r'Player "([^"]+)".*killed\s+(Zombie|Infected)',
            # Padrao 8: Player "Name" (id=...) caught Fish
            r'Player "([^"]+)".*caught\s+([A-Za-z0-9_]+)',
        ]

        try:
            with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    for i, pattern in enumerate(patterns):
                        match = re.search(pattern, line)
                        if match:
                            # Padrao 1 tem player_id
                            if i == 0 and len(match.groups()) >= 4:
                                gamertag = match.group(1).strip()
                                player_id = match.group(2).strip()
                                ip = match.group(3).strip()
                                port = match.group(4).strip()
                            else:
                                gamertag = match.group(1).strip()
                                ip = match.group(2).strip()
                                player_id = None
                                port = None

                            # Extrair timestamp se possivel
                            timestamp = self._extract_timestamp(line)

                            # Definir tipo de evento baseado no padrao
                            event_type = "connection"
                            extra_data = {}

                            if i == 5:  # Placed
                                event_type = "place"
                                extra_data = {"item": match.group(2)}
                            elif i == 6:  # Killed Zombie
                                event_type = "zombie_kill"
                            elif i == 7:  # Caught Fish
                                event_type = "fish_caught"

                            connections.append(
                                {
                                    "gamertag": gamertag,
                                    "ip": ip if i < 5 else None,
                                    "event_type": event_type,
                                    "extra": extra_data,
                                    "player_id": player_id,
                                    "timestamp": timestamp,
                                }
                            )
                            break

        except FileNotFoundError:
            print(f"[LOG PARSER] Arquivo {log_file} nao encontrado")
        except Exception as e:
            print(f"[LOG PARSER] Erro ao parsear logs: {e}")

        return connections

    def _extract_timestamp(self, line):
        """Extrai timestamp da linha de log"""
        # Padrao: [2026-01-21 20:30:15]
        match = re.search(r"\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\]", line)
        if match:
            return match.group(1)
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
