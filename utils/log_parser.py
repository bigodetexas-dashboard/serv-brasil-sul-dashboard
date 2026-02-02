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
        # Initial config from .env (fallback)
        self.ftp_host = os.getenv("FTP_HOST")
        self.ftp_user = os.getenv("FTP_USER")
        self.ftp_pass = os.getenv("FTP_PASS")
        self.ftp_port = int(os.getenv("FTP_PORT", 21))
        self.log_path = "/dayzxb_missions/dayzOffline.chernarusplus/ADM.log"

    def fetch_logs(self, local_file="server_logs.txt"):
        """Baixa logs do servidor via FTP (usando credenciais dinâmicas se disponíveis)"""
        import asyncio
        from utils.nitrado import get_ftp_credentials

        # 1. Tentar obter credenciais dinâmicas do Nitrado API
        try:
            creds = asyncio.run(get_ftp_credentials())
            if creds:
                print(
                    f"[LOG PARSER] Usando credenciais dinâmicas da Nitrado para {creds['host']}"
                )
                self.ftp_host = creds["host"]
                self.ftp_user = creds["user"]
                self.ftp_port = int(creds["port"])
                if not self.ftp_pass and os.getenv("FTP_PASS"):
                    self.ftp_pass = os.getenv("FTP_PASS")
        except Exception as e:
            print(f"[LOG PARSER] Falha ao obter credenciais dinâmicas: {e}")

        if not self.ftp_host or not self.ftp_user or not self.ftp_pass:
            print("[LOG PARSER] ERRO: Credenciais FTP incompletas no .env")
            return False

        try:
            print(f"[LOG PARSER] Conectando ao FTP: {self.ftp_host}:{self.ftp_port}")
            ftp = FTP()
            ftp.connect(self.ftp_host, self.ftp_port, timeout=30)
            ftp.login(self.ftp_user, self.ftp_pass)

            # Os logs do Xbox costumam estar na pasta 'profile'
            target_dirs = [
                "dayzxb/profile",
                "dayzxb_missions/dayzOffline.chernarusplus",
                "",
            ]

            found_file = None
            for d in target_dirs:
                try:
                    ftp.cwd("/" + d if d else "/")
                    files = ftp.nlst()

                    # Prioridade 1: Arquivos .ADM (Mais completos para DayZ)
                    adm_files = sorted(
                        [f for f in files if f.upper().endswith(".ADM")], reverse=True
                    )
                    if adm_files:
                        found_file = (d + "/" if d else "") + adm_files[0]
                        break

                    # Prioridade 2: Arquivos .RPT
                    rpt_files = sorted(
                        [f for f in files if f.upper().endswith(".RPT")], reverse=True
                    )
                    if rpt_files:
                        found_file = (d + "/" if d else "") + rpt_files[0]
                        break
                except:
                    continue

            if not found_file:
                print(
                    "[LOG PARSER] ERRO: Nenhum arquivo .ADM ou .RPT encontrado no FTP."
                )
                ftp.quit()
                return False

            print(f"[LOG PARSER] Baixando: {found_file}")
            with open(local_file, "wb") as f:
                ftp.retrbinary(f"RETR {found_file}", f.write)

            ftp.quit()
            return True

        except Exception as e:
            print(f"[LOG PARSER] Erro crítico no FTP: {e}")
            return False

    def parse_log_events(self, log_file="server_logs.txt"):
        """Extrai conexoes, PvP Kills e eventos importantes do log."""
        events = []

        # Regex Patterns
        p_conn = r'Player "([^"]+)".*id=([0-9]+).*ip=([0-9.]+):(\d+)'
        p_kill_adm = r"PlayerKill: Killer=\"(?P<killer>[^\"]+)\".*Victim=\"(?P<victim>[^\"]+)\".*Pos=<(?P<x>[-0-9.]+),.*,\s*(?P<z>[-0-9.]+)>, Weapon=(?P<weapon>[^,]+), Distance=(?P<dist>\d+)"
        p_kill_rpt = r"Kill: (?P<killer>[^\"]+) killed (?P<victim>[^\"]+) at \[(?P<x>[-0-9.]+),.*,\s*(?P<z>[-0-9.]+)\] with (?P<weapon>[^\(]+) \(?(?P<dist>\d+)?m?"
        p_zombie = r'Player "([^"]+)".*killed\s+(Zombie|Infected)'
        p_placement = r'Player "(?P<player>[^"]+)" .* pos=<(?P<x>[-0-9.]+),.*,\s*(?P<z>[-0-9.]+)>.*placed (?P<item>.+)'
        p_build = r'Player "(?P<player>[^"]+)" .* pos=<(?P<x>[-0-9.]+),.*,\s*(?P<z>[-0-9.]+)>.*(?P<action>built|dismantled) (?P<item>.+) with (?P<tool>.+)'

        try:
            with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    ts = self._extract_timestamp(line)

                    # 1. PvP Kill (Prioridade Máxima)
                    m = re.search(p_kill_adm, line) or re.search(p_kill_rpt, line)
                    if m:
                        events.append(
                            {
                                "type": "pvp_kill",
                                "killer": m.group("killer").strip(),
                                "victim": m.group("victim").strip(),
                                "weapon": m.group("weapon").strip(),
                                "distance": float(m.group("dist") or 0),
                                "pos": (float(m.group("x")), float(m.group("z"))),
                                "timestamp": ts,
                            }
                        )
                        continue

                    # 2. Conexão
                    m = re.search(p_conn, line)
                    if m:
                        events.append(
                            {
                                "type": "connection",
                                "gamertag": m.group(1).strip(),
                                "player_id": m.group(2).strip(),
                                "ip": m.group(3).strip(),
                                "timestamp": ts,
                            }
                        )
                        continue

                    # 3. Zombie Kill
                    m = re.search(p_zombie, line)
                    if m:
                        events.append(
                            {
                                "type": "zombie_kill",
                                "gamertag": m.group(1).strip(),
                                "timestamp": ts,
                            }
                        )
                        continue

                    # 4. Build Ações (Construção/Desmonte)
                    m = re.search(p_build, line)
                    if m:
                        events.append(
                            {
                                "type": "build_action",
                                "player": m.group("player").strip(),
                                "action": m.group("action").strip(),
                                "item": m.group("item").strip(),
                                "tool": m.group("tool").strip(),
                                "pos": (float(m.group("x")), float(m.group("z"))),
                                "timestamp": ts,
                            }
                        )
                        continue

                    # 5. Placement
                    m = re.search(p_placement, line)
                    if m:
                        events.append(
                            {
                                "type": "placement",
                                "player": m.group("player").strip(),
                                "item": m.group("item").strip(),
                                "pos": (float(m.group("x")), float(m.group("z"))),
                                "timestamp": ts,
                            }
                        )

        except Exception as e:
            print(f"[LOG PARSER] Erro ao parsear logs: {e}")

        return events

    def _extract_timestamp(self, line):
        """Extrai timestamp da linha de log"""
        # Padrao: [2026-01-21 20:30:15]
        match = re.search(r"\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\]", line)
        if match:
            return match.group(1)
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
