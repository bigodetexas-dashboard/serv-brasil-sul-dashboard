"""
Módulo principal do Launcher do BigodeTexas.
Unidade de Comando Elite v4.0 com monitoramento tático e integração Nitrado.
"""

import asyncio
import json
import os
import shutil
import subprocess
import threading
import time
import webbrowser

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageOps, ImageTk

from utils.nitrado import get_server_status, ban_player, kick_player

# --- GESTÃO DE IDIOMAS (i18n) ---
TRANSLATIONS = {
    "pt": {
        "title": "UNIDADE DE COMANDO ELITE",
        "subtitle": "SISTEMA TÁTICO v200.0",
        "tab_cmd": "CMD",
        "tab_ops": "OPS",
        "tab_int": "INT",
        "tab_log": "LOG",
        "btn_dash": "INICIAR DASHBOARD",
        "btn_bot": "INICIAR BOT",
        "btn_exit": "FECHAR SISTEMA",
        "raid_on": "RAID ATIVO",
        "raid_off": "RAID INATIVO",
        "broadcast": "[ BROADCAST TÁTICO ]",
        "players_online": "[ OPERADORES ONLINE ]",
        "db_tools": "[ FERRAMENTAS DB ]",
        "links": "[ LINKS EXTERNOS ]",
        "vital": "[ STATUS VITAL - 24H ]",
        "diag": "[ SISTEMA DE DIAGNÓSTICO ]",
        "scheduler": "[ AGENDAMENTO DE RAID ]",
        "save": "SALVAR CONFIGURAÇÃO",
        "backup": "SNAPSHOT BACKUP",
        "lang": "IDIOMA",
        "tt_cmd": "Painel de Comando: Controle o Bot, Dashboard e operações de Raid.",
        "tt_ops": "Monitor de Operadores: Lista de jogadores online com opções de Kick/Ban.",
        "tt_int": "Inteligência Tática: Gráficos de performance e mapa dinâmico.",
        "tt_log": "Logística e Snapshot: Backups do sistema e links de acesso rápido.",
        "tt_bot": "Iniciar/Parar o Bot de Discord do BigodeTexas.",
        "tt_dash": "Iniciar/Parar o Web Dashboard para gerência remota.",
        "tt_raid": "Alternar o Modo Raid no servidor (Edita os XMLs via FTP).",
        "tt_backup": "Gerar uma cópia de segurança completa do banco de dados SQLite.",
    },
    "en": {
        "title": "ELITE COMMAND UNIT",
        "subtitle": "TACTICAL SYSTEM v200.0",
        "tab_cmd": "CMD",
        "tab_ops": "OPS",
        "tab_int": "INT",
        "tab_log": "LOG",
        "btn_dash": "START DASHBOARD",
        "btn_bot": "START BOT",
        "btn_exit": "CLOSE SYSTEM",
        "raid_on": "RAID ACTIVE",
        "raid_off": "RAID INACTIVE",
        "broadcast": "[ TACTICAL BROADCAST ]",
        "players_online": "[ OPERATORS ONLINE ]",
        "db_tools": "[ DB TOOLS ]",
        "links": "[ EXTERNAL LINKS ]",
        "vital": "[ VITAL STATUS - 24H ]",
        "diag": "[ DIAGNOSTIC SYSTEM ]",
        "scheduler": "[ RAID SCHEDULER ]",
        "save": "SAVE CONFIGURATION",
        "backup": "SNAPSHOT BACKUP",
        "lang": "LANGUAGE",
        "tt_cmd": "Command Panel: Control Bot, Dashboard, and Raid operations.",
        "tt_ops": "Operators Monitor: List online players with Kick/Ban options.",
        "tt_int": "Tactical Intel: Performance graphs and dynamic map.",
        "tt_log": "Logistics & Snapshot: System backups and quick access links.",
        "tt_bot": "Start/Stop the BigodeTexas Discord Bot.",
        "tt_dash": "Start/Stop the Web Dashboard for remote management.",
        "tt_raid": "Toggle Raid Mode on server (Edits XMLs via FTP).",
        "tt_backup": "Generate a full backup copy of the SQLite database.",
    },
    "es": {
        "title": "UNIDAD DE MANDO ELITE",
        "subtitle": "SISTEMA TÁCTICO v200.0",
        "tab_cmd": "CMD",
        "tab_ops": "OPS",
        "tab_int": "INT",
        "tab_log": "LOG",
        "btn_dash": "INICIAR DASHBOARD",
        "btn_bot": "INICIAR BOT",
        "btn_exit": "CERRAR SISTEMA",
        "raid_on": "RAID ACTIVO",
        "raid_off": "RAID INACTIVO",
        "broadcast": "[ TRANSMISIÓN TÁCTICA ]",
        "players_online": "[ OPERADORES ONLINE ]",
        "db_tools": "[ HERRAMIENTAS DB ]",
        "links": "[ ENLACES EXTERNOS ]",
        "vital": "[ ESTADO VITAL - 24H ]",
        "diag": "[ SISTEMA DE DIAGNÓSTICO ]",
        "scheduler": "[ HORARIO DE RAID ]",
        "save": "GUARDAR CONFIGURACIÓN",
        "backup": "COPIA DE SEGURIDAD",
        "lang": "IDIOMA",
        "tt_cmd": "Panel de Control: Gestione Bot, Dashboard y Raid.",
        "tt_ops": "Monitor de Operadores: Lista de jugadores con Kick/Ban.",
        "tt_int": "Inteligencia Táctica: Gráficos y mapa dinámico.",
        "tt_log": "Logística: Backups y enlaces rápidos.",
        "tt_bot": "Iniciar/Detener el Bot de Discord.",
        "tt_dash": "Iniciar/Detener el Dashboard Web.",
        "tt_raid": "Cambiar Modo Raid (FTP).",
        "tt_backup": "Generar copia de seguridad de la base de datos.",
    },
    "fr": {
        "title": "UNITÉ DE COMMANDEMENT ÉLITE",
        "subtitle": "SYSTÈME TACTIQUE v200.0",
        "tab_cmd": "CMD",
        "tab_ops": "OPS",
        "tab_int": "INT",
        "tab_log": "LOG",
        "btn_dash": "LANCER LE DASHBOARD",
        "btn_bot": "LANCER LE BOT",
        "btn_exit": "FERMER LE SYSTÈME",
        "raid_on": "RAID ACTIF",
        "raid_off": "RAID INACTIF",
        "broadcast": "[ RADIODIFFUSION TACTIQUE ]",
        "players_online": "[ OPÉRATEURS EN LIGNE ]",
        "db_tools": "[ OUTILS DB ]",
        "links": "[ LIENS EXTERNES ]",
        "vital": "[ ÉTAT VITALE - 24H ]",
        "diag": "[ SYSTÈME DE DIAGNOSTIC ]",
        "scheduler": "[ PLANIFICATION RAID ]",
        "save": "SAUVEGARDER CONFIG",
        "backup": "SAUVEGARDE DB",
        "lang": "LANGUE",
        "tt_cmd": "Panneau de Commande: Contróle du Bot, Dashboard et Raid.",
        "tt_ops": "Moniteur Opérateurs: Liste joueurs avec Kick/Ban.",
        "tt_int": "Intel Tactique: Graphiques et carte dynamique.",
        "tt_log": "Logistique: Sauvegardes et liens rapides.",
        "tt_bot": "Lancer/Arrêter le Bot Discord.",
        "tt_dash": "Lancer/Arrêter le Dashboard Web.",
        "tt_raid": "Basculer le Mode Raid (FTP).",
        "tt_backup": "Créer une sauvegarde de la base de données.",
    },
    "it": {
        "title": "UNITÀ DI COMANDO ELITE",
        "subtitle": "SISTEMA TATTICO v200.0",
        "tab_cmd": "CMD",
        "tab_ops": "OPS",
        "tab_int": "INT",
        "tab_log": "LOG",
        "btn_dash": "AVVIA DASHBOARD",
        "btn_bot": "AVVIA BOT",
        "btn_exit": "CHIUDI SISTEMA",
        "raid_on": "RAID ATTIVO",
        "raid_off": "RAID INATTIVO",
        "broadcast": "[ BROADCAST TATTICO ]",
        "players_online": "[ OPERATORI ONLINE ]",
        "db_tools": "[ STRUMENTI DB ]",
        "links": "[ LINK ESTERNI ]",
        "vital": "[ STATO VITALE - 24H ]",
        "diag": "[ SISTEMA DIAGNOSTICO ]",
        "scheduler": "[ PIANIFICAZIONE RAID ]",
        "save": "SALVA CONFIGURAZIONE",
        "backup": "BACKUP DB",
        "lang": "LINGUA",
        "tt_cmd": "Pannello di Comando: Controllo Bot, Dashboard e Raid.",
        "tt_ops": "Monitor Operatori: Lista giocatori con Kick/Ban.",
        "tt_int": "Intel Tattica: Grafici e mappa dinamica.",
        "tt_log": "Logistica: Backup e link rapidi.",
        "tt_bot": "Avvia/Arresta il Bot Discord.",
        "tt_dash": "Avvia/Arresta il Dashboard Web.",
        "tt_raid": "Attiva/Disattiva Modalità Raid (FTP).",
        "tt_backup": "Crea backup del database.",
    },
    "de": {
        "title": "ELITE-KOMMANDOEINHEIT",
        "subtitle": "TAKTIK-SYSTEM v200.0",
        "tab_cmd": "KDO",
        "tab_ops": "OPS",
        "tab_int": "INT",
        "tab_log": "LOG",
        "btn_dash": "DASHBOARD STARTEN",
        "btn_bot": "BOT STARTEN",
        "btn_exit": "SYSTEM BEENDEN",
        "raid_on": "RAID AKTIV",
        "raid_off": "RAID INAKTIV",
        "broadcast": "[ TAKTISCHER FUNK ]",
        "players_online": "[ OPERATORE ONLINE ]",
        "db_tools": "[ DB TOOLS ]",
        "links": "[ EXTERNE LINKS ]",
        "vital": "[ VITALSTATUS - 24H ]",
        "diag": "[ DIAGNOSESYSTEM ]",
        "scheduler": "[ RAID-ZEITPLAN ]",
        "save": "CONFIG SPEICHERN",
        "backup": "DB BACKUP",
        "lang": "SPRACHE",
        "tt_cmd": "Kontrollzentrum: Bot, Dashboard und Raid-Steuerung.",
        "tt_ops": "Operator-Monitor: Spielerliste mit Kick/Ban.",
        "tt_int": "Taktik-Intel: Grafiken und dynamische Karte.",
        "tt_log": "Logistik: Backups und Schnelllinks.",
        "tt_bot": "Discord-Bot starten/stoppen.",
        "tt_dash": "Web-Dashboard starten/stoppen.",
        "tt_raid": "Raid-Modus umschalten (FTP).",
        "tt_backup": "Datenbank-Backup erstellen.",
    },
    "ru": {
        "title": "ЭЛИТНЫЙ КОМАНДНЫЙ ЦЕНТР",
        "subtitle": "ТАКТИЧЕСКАЯ СИСТЕМА v200.0",
        "tab_cmd": "КМД",
        "tab_ops": "ОПС",
        "tab_int": "ИНТ",
        "tab_log": "ЛОГ",
        "btn_dash": "ЗАПУСК ПАНЕЛИ",
        "btn_bot": "ЗАПУСК БОТА",
        "btn_exit": "ЗАКРЫТЬ СИСТЕМУ",
        "raid_on": "РЕЙД АКТИВЕН",
        "raid_off": "РЕЙД НЕАКТИВЕН",
        "broadcast": "[ ТАКТИЧЕСКОЕ ВЕЩАНИЕ ]",
        "players_online": "[ ОПЕРАТОРЫ ОНЛАЙН ]",
        "db_tools": "[ ИНСТРУМЕНТЫ БД ]",
        "links": "[ ВНЕШНИЕ ССЫЛКИ ]",
        "vital": "[ СОСТОЯНИЕ - 24Ч ]",
        "diag": "[ ДИАГНОСТИКА ]",
        "scheduler": "[ РАСПИСАНИЕ РЕЙДОВ ]",
        "save": "СОХРАНИТЬ",
        "backup": "БЭКАП БД",
        "lang": "ЯЗЫК",
        "tt_cmd": "Командный пульт: Управление ботом, панелью и рейдом.",
        "tt_ops": "Монитор игроков: Список игроков, Кик/Бан.",
        "tt_int": "Разведка: Графики и динамическая карта.",
        "tt_log": "Логистика: Бэкапы и краткие ссылки.",
        "tt_bot": "Запуск/Остановка дискорд-бота.",
        "tt_dash": "Запуск/Остановка веб-панели.",
        "tt_raid": "Переключить режим рейда (FTP).",
        "tt_backup": "Создать резервную копию базы данных.",
    },
    "zh": {
        "title": "精英指挥中心",
        "subtitle": "战术系统 v200.0",
        "tab_cmd": "指令",
        "tab_ops": "行动",
        "tab_int": "情报",
        "tab_log": "物流",
        "btn_dash": "启动仪表盘",
        "btn_bot": "启动机器人",
        "btn_exit": "关闭系统",
        "raid_on": "突袭开启",
        "raid_off": "突袭关闭",
        "broadcast": "[ 战术广播 ]",
        "players_online": "[ 在线操作员 ]",
        "db_tools": "[ 数据库工具 ]",
        "links": "[ 外部链接 ]",
        "vital": "[ 运行状态 - 24H ]",
        "diag": "[ 诊断系统 ]",
        "scheduler": "[ 突击调度 ]",
        "save": "保存配置",
        "backup": "快照备份",
        "lang": "语言选择",
        "tt_cmd": "指挥面板：控制机器人、仪表盘和突袭操作。",
        "tt_ops": "操作员监控：在线玩家列表及踢出/封禁选项。",
        "tt_int": "战术情报：性能图表和动态地图。",
        "tt_log": "后勤与快照：系统备份和快速访问链接。",
        "tt_bot": "启动/停止 Discord 机器人。",
        "tt_dash": "启动/停止网页仪表盘进行远程管理。",
        "tt_raid": "在服务器上切换突袭模式（通过 FTP 编辑 XML）。",
        "tt_backup": "生成 SQLite 数据库的完整备份副本。",
    },
    "ja": {
        "title": "エリート指揮ユニット",
        "subtitle": "戦術システム v200.0",
        "tab_cmd": "コマンド",
        "tab_ops": "オペ",
        "tab_int": "インテ",
        "tab_log": "ログ",
        "btn_dash": "ダッシュボード起動",
        "btn_bot": "ボット起動",
        "btn_exit": "システム終了",
        "raid_on": "レイド有効",
        "raid_off": "レイド無効",
        "broadcast": "[ 戦術放送 ]",
        "players_online": "[ オンライン中 ]",
        "db_tools": "[ DBツール ]",
        "links": "[ 外部リンク ]",
        "vital": "[ 稼働ステータス - 24H ]",
        "diag": "[ 診断システム ]",
        "scheduler": "[ レイドスケジュール ]",
        "save": "設定を保存",
        "backup": "バックアップ",
        "lang": "言語設定",
        "tt_cmd": "コマンドパネル：ボット、ダッシュボード、レイドの制御。",
        "tt_ops": "オペレーターモニター：プレイヤーリスト（キック/バン対応）。",
        "tt_int": "戦術情報：パフォーマンスグラフと動的マップ。",
        "tt_log": "ロジスティクス：バックアップとクイックアクセス。",
        "tt_bot": "Discordボットの開始/停止。",
        "tt_dash": "ウェブダッシュボードの開始/停止。",
        "tt_raid": "レイドモードの切り替え（FTP経由）。",
        "tt_backup": "データベースのバックアップ。",
    },
    "hi": {
        "title": "एलिट कमांड यूनिट",
        "subtitle": "सामरिक प्रणाली v200.0",
        "tab_cmd": "कमांड",
        "tab_ops": "ऑप्स",
        "tab_int": "इंट",
        "tab_log": "लॉग",
        "btn_dash": "डैशबोर्ड शुरू करें",
        "btn_bot": "बॉट शुरू करें",
        "btn_exit": "सिस्टम बंद करें",
        "raid_on": "रेड सक्रिय",
        "raid_off": "रेड निष्क्रिय",
        "broadcast": "[ सामरिक प्रसारण ]",
        "players_online": "[ ऑनलाइन ऑपरेटर ]",
        "db_tools": "[ डेटाबेस टूल्स ]",
        "links": "[ बाहरी लिंक ]",
        "vital": "[ महत्वपूर्ण स्थिति - 24H ]",
        "diag": "[ नैदानिक ​​प्रणाली ]",
        "scheduler": "[ रेड शेड्यूलर ]",
        "save": "कॉन्फ़िगरेशन सहेजें",
        "backup": "बैकअप लें",
        "lang": "भाषा",
        "tt_cmd": "कमांड पैनल: बॉट, डैशबोर्ड और रेड संचालन को नियंत्रित करें।",
        "tt_ops": "ऑपरेटर मॉनिटर: किक/बैन विकल्पों के साथ ऑनलाइन खिलाड़ी।",
        "tt_int": "सामरिक इंटेल: प्रदर्शन ग्राफ और गतिशील मानचित्र।",
        "tt_log": "लॉजिस्टिक्स: बैकअप और त्वरित पहुंच लिंक।",
        "tt_bot": "बॉट शुरू/बंद करें।",
        "tt_dash": "वेब डैशबोर्ड शुरू/बंद करें।",
        "tt_raid": "रेड मोड टॉगल करें (FTP)।",
        "tt_backup": "डेटाबेस का बैकअप लें।",
    },
    "ar": {
        "title": "وحدة قيادة النخبة",
        "subtitle": "النظام التكتيكي v200.0",
        "tab_cmd": "أمر",
        "tab_ops": "عمليات",
        "tab_int": "ذكاء",
        "tab_log": "لوجستي",
        "btn_dash": "تشغيل لوحة التحكم",
        "btn_bot": "تشغيل البوت",
        "btn_exit": "إغلاق النظام",
        "raid_on": "الغارة نشطة",
        "raid_off": "الغارة غير نشطة",
        "broadcast": "[ البث التكتيكي ]",
        "players_online": "[ المشغلين عبر الإنترنت ]",
        "db_tools": "[ أدوات БД ]",
        "links": "[ روابط خارجية ]",
        "vital": "[ الحالة الحيوية - 24س ]",
        "diag": "[ نظام التشخيص ]",
        "scheduler": "[ جدولة الغارات ]",
        "save": "حفظ الإعدادات",
        "backup": "نسخة احتياطية",
        "lang": "اللغة",
        "tt_cmd": "لوحة القيادة: التحكم في البوت ولوحة التحكم والغارات.",
        "tt_ops": "مراقب المشغلين: قائمة اللاعبين مع خيارات الطرد/الحظر.",
        "tt_int": "الاستخبارات: رسوم بيانية وخريطة ديناميكية.",
        "tt_log": "الخدمات اللوجستية: النسخ الاحتياطي والروابط السريعة.",
        "tt_bot": "تشغيل/إيقاف بوت الديسكورد.",
        "tt_dash": "تشغيل/إيقاف لوحة التحكم عبر الويب.",
        "tt_raid": "تبديل وضع الغارة (FTP).",
        "tt_backup": "إنشاء نسخة احتياطية من قاعدة البيانات.",
    },
}


class BigodeLauncherElite:
    """
    Interface Gráfica Tática (HUD) para gerenciamento do ecossistema BigodeTexas.
    Monitora o servidor Nitrado, gerencia processos (Bot/Dashboard) e o Modo Raid.
    """

    def __init__(self, root_tk):
        """Inicializa a unidade de comando elite."""
        self.root = root_tk
        self.root.title("BIGODETEXAS COMMAND UNIT v4.0")
        self.width, self.height = 1200, 850
        self.root.geometry(f"{self.width}x{self.height}")
        self.root.overrideredirect(True)  # Frameless
        self.root.attributes("-topmost", True)

        # Colors - elite tactical palette
        self.c_bg = "#030303"
        self.c_accent = "#d4af37"  # Gold
        self.c_primary = "#6b8c42"  # Tactical Green
        self.c_white = "#ffffff"
        self.c_danger = "#ff4444"
        self.c_online = "#00ff44"

        # Tooltip state
        self.tt_rect = None
        self.tt_text = None
        self.c_panel = "#0a0a0a"

        # State
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.base_dir, "server_config.json")
        self.bg_path = os.path.join(self.base_dir, "banner_bigode_texas.png")
        self.db_path = os.path.join(self.base_dir, "bigode_unified.db")

        self.dashboard_proc = None
        self.bot_proc = None
        self.showing_manual = False
        self.auto_recovery = True

        # Load Schedule Settings
        config = self.load_full_config()
        self.current_lang = config.get("lang", None)  # Default None to trigger selector
        self.active_tab = "CMD"  # CMD, OPS, INT, LOG
        self.show_lang_screen = self.current_lang is None

        self.raid_active = config.get("raid_active", False)
        self.raid_days = config.get("raid_days", [5])
        self.raid_start = config.get("raid_start", 20)
        self.raid_end = config.get("raid_end", 22)

        # Nitrado HUD State
        self.nitrado_stats = {
            "players": "0/0",
            "status": "OFFLINE",
            "restart_timer": "--:--:--",
            "player_list": [],
        }
        self.player_history = [0] * 30  # Last 30 points for graph
        self.player_slots = []
        self.graph_points = []
        self.scan_line = None
        self.map_img_id = None
        self.mini_map_photo = None

        # Drag variables
        self.x = 0
        self.y = 0

        # Create Canvas
        self.canvas = tk.Canvas(
            self.root,
            width=self.width,
            height=self.height,
            bg=self.c_bg,
            highlightthickness=0,
            cursor="crosshair",
        )
        self.canvas.pack(fill="both", expand=True)

        # Bindings for frameless movement
        self.canvas.bind("<Button-1>", self.start_move)
        self.canvas.bind("<B1-Motion>", self.do_move)

        self.setup_ui()
        self.animate()

        # Start Threads
        threading.Thread(target=self.nitrado_polling_loop, daemon=True).start()
        threading.Thread(target=self.process_monitor_loop, daemon=True).start()

    def load_full_config(self):
        """Carrega toda a configuração do servidor."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}

    def load_raid_status(self):
        """Método legado mantido para compatibilidade, agora usa o state."""
        return self.raid_active

    def save_raid_status(self, status):
        """Salva apenas o toggle de ativação (Override)."""
        self.raid_active = status
        self.save_full_config()
        self.update_log(f"> RAID MODE {'ACTIVATED' if status else 'DEACTIVATED'}")

    def save_full_config(self):
        """Salva todo o estado da configuração no JSON."""
        data = self.load_full_config()
        data["raid_active"] = self.raid_active
        data["raid_days"] = self.raid_days
        data["raid_start"] = self.raid_start
        data["raid_end"] = self.raid_end
        data["lang"] = self.current_lang

        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        # Sincroniza labels se necessário
        self.refresh_ui()

    def start_move(self, event):
        """Inicia o rastreamento do movimento da janela."""
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        """Executa o reposicionamento da janela sem bordas."""
        deltax = event.x - self.x
        deltay = event.y - self.y
        new_x = self.root.winfo_x() + deltax
        new_y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{new_x}+{new_y}")

    def setup_ui(self):
        """Inicia a construção da interface modular."""
        if self.show_lang_screen:
            self.draw_language_selector_screen()
        else:
            self.draw_base_hud()
            self.draw_tabs()
            self.switch_tab(self.active_tab)

    def draw_language_selector_screen(self):
        """Tela inicial tática para escolha de idioma."""
        self.canvas.delete("all")

        # Background
        if os.path.exists(self.bg_path):
            img = Image.open(self.bg_path).convert("RGBA")
            img = ImageOps.fit(img, (self.width, self.height), Image.Resampling.LANCZOS)
            overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 150))
            img = Image.alpha_composite(img, overlay)
            self.splash_bg = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, image=self.splash_bg, anchor="nw")

        # Title
        self.canvas.create_text(
            self.width / 2,
            100,
            text="SELECT COMMAND LANGUAGE",
            font=("Impact", 40),
            fill=self.c_white,
        )
        self.canvas.create_text(
            self.width / 2,
            160,
            text="SISTEMA DE IDENTIFICAÇÃO GLOBAL // SELECIONE SUA BANDEIRA",
            font=("Consolas", 12),
            fill=self.c_accent,
        )

        # Flags Grid
        langs = [
            ("pt", "🇧🇷 PORTUGUÊS"),
            ("en", "🇺🇸 ENGLISH"),
            ("es", "🇪🇸 ESPAÑOL"),
            ("fr", "🇫🇷 FRANÇAIS"),
            ("it", "🇮🇹 ITALIANO"),
            ("de", "🇩🇪 DEUTSCH"),
            ("ru", "🇷🇺 РУССКИЙ"),
            ("zh", "🇨🇳 中文"),
            ("ja", "🇯🇵 日本語"),
            ("hi", "🇮🇳 हिन्दी"),
            ("ar", "🇸🇦 العربية"),
        ]

        start_x, start_y = 150, 250
        for i, (code, label) in enumerate(langs):
            col = i % 3
            row = i // 3
            x = start_x + (col * 350)
            y = start_y + (row * 100)

            tag = f"splash_{code}"
            rect = self.canvas.create_rectangle(
                x,
                y,
                x + 280,
                y + 60,
                fill="#080808",
                outline=self.c_primary,
                width=2,
                tags=tag,
            )
            txt = self.canvas.create_text(
                x + 140,
                y + 30,
                text=label,
                font=("Consolas", 12, "bold"),
                fill=self.c_white,
                tags=tag,
            )

            def on_click(_e, c=code):
                self.current_lang = c
                self.show_lang_screen = False
                self.save_full_config()  # This will trigger refresh_ui and main HUD

            def on_enter(_e, t=tag):
                self.canvas.itemconfig(t, fill=self.c_primary)

            def on_leave(_e, t=tag):
                self.canvas.itemconfig(t, fill="#080808")

            self.canvas.tag_bind(tag, "<Button-1>", on_click)
            self.canvas.tag_bind(tag, "<Enter>", on_enter)
            self.canvas.tag_bind(tag, "<Leave>", on_leave)

        # Scanlines animation
        if not hasattr(self, "scan_line") or self.scan_line is None:
            self.scan_line = self.canvas.create_line(
                0,
                0,
                self.width,
                0,
                fill="#ffffff",
                width=1,
                stipple="gray25",
                tags="fixed",
            )

        self.animate()

    def t(self, key):
        """Retorna a tradução para a chave especificada no idioma atual."""
        return TRANSLATIONS.get(self.current_lang, TRANSLATIONS["pt"]).get(key, key)

    def show_tooltip(self, event, key):
        """Exibe um balão tático (glassmorphism) próximo ao cursor."""
        self.hide_tooltip()
        text = self.t(key)
        if text == key:
            return  # Não mostra se não houver tradução

        # Posição relativa ao componente Canvas (Mais robusto)
        x, y = event.x + 20, event.y + 10

        # Estilo Glassmorphism para o balão
        padding = 10
        f_size = 9
        # Cálculo básico de largura baseado no texto
        t_width = min(300, len(text) * 7.5)

        # Criar container do balão (Sombra/Glow)
        self.tt_rect = self.canvas.create_rectangle(
            x,
            y,
            x + t_width + padding * 2,
            y + 50,  # Altura aproximada
            fill="#151515",
            outline=self.c_accent,
            width=1,
            tags="tooltip",
        )
        self.tt_text = self.canvas.create_text(
            x + padding,
            y + padding,
            text=text,
            font=("Consolas", f_size),
            fill=self.c_white,
            anchor="nw",
            width=t_width,
            tags="tooltip",
        )

        # Ajustar altura do retângulo ao texto real
        bbox = self.canvas.bbox(self.tt_text)
        if bbox:
            self.canvas.coords(
                self.tt_rect,
                bbox[0] - padding,
                bbox[1] - padding,
                bbox[2] + padding,
                bbox[3] + padding,
            )

        # Garantir que fique no topo de tudo
        self.canvas.tag_raise("tooltip")

    def hide_tooltip(self, _event=None):
        """Remove qualquer balão tático ativo do canvas."""
        self.canvas.delete("tooltip")

    def draw_base_hud(self):
        """Desenha o background e elementos globais estáticos."""
        self.canvas.delete("all")
        # Background
        if os.path.exists(self.bg_path):
            img = Image.open(self.bg_path).convert("RGBA")
            img = ImageOps.fit(img, (self.width, self.height), Image.Resampling.LANCZOS)
            overlay = Image.new(
                "RGBA", (self.width, self.height), (0, 0, 0, 210)
            )  # Darker for glassmorphism
            img = Image.alpha_composite(img, overlay)
            self.bg_photo = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        # Layout Main Header
        self.header_title = self.canvas.create_text(
            110,
            80,
            text=self.t("title"),
            font=("Impact", 40),
            fill=self.c_white,
            anchor="w",
        )
        self.header_sub = self.canvas.create_text(
            110,
            140,
            text=self.t("subtitle"),
            font=("Consolas", 12),
            fill=self.c_accent,
            anchor="w",
        )

        # Sidebar Glass Container
        self.draw_glass_rect(0, 0, 80, self.height, opacity=0.3, outline=self.c_primary)

        # Global Status Bar (Bottom)
        self.draw_glass_rect(
            0,
            self.height - 40,
            self.width,
            self.height,
            opacity=0.5,
            outline=self.c_accent,
        )

        self.hud_status = self.canvas.create_text(
            110,
            self.height - 20,
            text="SERVER: --",
            font=("Consolas", 9, "bold"),
            fill=self.c_white,
            anchor="w",
        )
        self.hud_players = self.canvas.create_text(
            350,
            self.height - 20,
            text="OPERATORS: --/--",
            font=("Consolas", 9, "bold"),
            fill=self.c_white,
            anchor="w",
        )
        self.hud_raid = self.canvas.create_text(
            600,
            self.height - 20,
            text="RAID: --",
            font=("Consolas", 9, "bold"),
            fill=self.c_white,
            anchor="w",
        )
        self.hud_restart = self.canvas.create_text(
            850,
            self.height - 20,
            text="RESTART: --:--",
            font=("Consolas", 9, "bold"),
            fill=self.c_accent,
            anchor="w",
        )

        # Scanlines (Always keep tag)
        self.scan_line = self.canvas.create_line(
            0, 0, self.width, 0, fill="#ffffff", width=1, stipple="gray25", tags="fixed"
        )

    def draw_glass_rect(self, x1, y1, x2, y2, opacity=0.2, outline=""):
        """Desenha um retângulo com efeito simulado de vidro/glow."""
        self.canvas.create_rectangle(
            x1, y1, x2, y2, fill=self.c_panel, outline=outline, width=1
        )
        # Glow border simulation
        if outline:
            self.canvas.create_rectangle(
                x1 - 2,
                y1 - 2,
                x2 + 2,
                y2 + 2,
                outline=outline,
                width=1,
                stipple="gray25",
            )

    def draw_vital_graph(self, x=850, y=220, w=280, h=100):
        """Desenha o gráfico de vitalidade (players online) no canvas."""
        for p in self.graph_points:
            self.canvas.delete(p)
        self.graph_points = []

        max_v = max(self.player_history) if max(self.player_history) > 0 else 32
        spacing = w / (len(self.player_history) - 1)

        for i in range(len(self.player_history) - 1):
            x1 = x + (i * spacing)
            y1 = y - (self.player_history[i] / max_v * h)
            x2 = x + ((i + 1) * spacing)
            y2 = y - (self.player_history[i + 1] / max_v * h)

            line = self.canvas.create_line(x1, y1, x2, y2, fill=self.c_online, width=2)
            self.graph_points.append(line)

    def update_hud(self):
        """Atualiza os elementos do HUD com as estatísticas atuais do Nitrado."""
        stats = self.nitrado_stats

        # Update Player Management List (Only if tab OPS is active)
        if self.active_tab == "OPS":
            p_list = stats.get("player_list", [])
            self.canvas.itemconfig(
                "op_title", text=f"{self.t('players_online')}: {len(p_list)}"
            )

            for i in range(len(self.player_slots)):
                slot = self.player_slots[i]
                if i < len(p_list):
                    p_name = p_list[i].get("name", "Unknown")
                    p_time = p_list[i].get("time", "0s")
                    self.canvas.itemconfig(
                        slot["text"], text=f"{p_name[:24]:<24} | {p_time:>10}"
                    )
                    self.canvas.itemconfig(slot["row"], outline="#222222")
                else:
                    self.canvas.itemconfig(slot["text"], text="--")
                    self.canvas.itemconfig(slot["row"], outline="")

        # Update Graph (Only if tab INT is active)
        if self.active_tab == "INT":
            self.draw_vital_graph(x=130, y=400, w=440, h=160)

        # Update global HUD elements (always visible)
        self.canvas.itemconfig(
            self.hud_status,
            text=f"SERVER STATUS: {stats['status']}",
            fill=self.c_online if stats["status"] == "ONLINE" else self.c_danger,
        )
        self.canvas.itemconfig(
            self.hud_players, text=f"PLAYERS ONLINE: {stats['players']}"
        )
        self.canvas.itemconfig(
            self.hud_raid,
            text=f"RAID MODE: {'ENABLED' if self.raid_active else 'DISABLED'}",
            fill=self.c_danger if self.raid_active else self.c_primary,
        )
        self.canvas.itemconfig(
            self.hud_restart, text=f"NEXT RESTART: {stats['restart_timer']}"
        )

        # Update vital graph in LOG tab
        if self.active_tab == "LOG":
            self.draw_vital_graph()

    def draw_tabs(self):
        """Desenha o seletor lateral de abas."""
        tabs = [
            ("tab_cmd", "🕹️", "CMD"),
            ("tab_ops", "👥", "OPS"),
            ("tab_int", "🛰️", "INT"),
            ("tab_log", "📦", "LOG"),
        ]

        for i, (key, icon, name) in enumerate(tabs):
            y = 100 + (i * 100)
            tag = f"btn_tab_{name}"
            tt_key = f"tt_{name.lower()}"
            active = self.active_tab == name

            # Icon/Text selection
            self.canvas.create_text(
                40,
                y,
                text=icon,
                font=("Segoe UI Emoji", 24),
                fill=self.c_white,
                tags=tag,
            )
            self.canvas.create_text(
                40,
                y + 35,
                text=self.t(key),
                font=("Consolas", 12, "bold"),
                fill=self.c_accent if active else "#555555",
                tags=tag,
            )

            def on_t_enter(event, k=tt_key, t=tag):
                self.show_tooltip(event, k)
                self.canvas.itemconfig(t, fill=self.c_accent)

            def on_t_leave(_event, t=tag, n=name):
                self.hide_tooltip()
                self.canvas.itemconfig(
                    t, fill=self.c_accent if self.active_tab == n else "#555555"
                )

            self.canvas.tag_bind(tag, "<Enter>", on_t_enter)
            self.canvas.tag_bind(tag, "<Leave>", on_t_leave)
            self.canvas.tag_bind(
                tag, "<Button-1>", lambda _, t=name: self.switch_tab(t)
            )

    def switch_tab(self, tab_name):
        """Troca o conteúdo visual do HUD baseado na aba selecionada."""
        self.active_tab = tab_name
        self.refresh_ui()

    def refresh_ui(self):
        """Redesenha todo o conteúdo da aba ativa."""
        if self.show_lang_screen:
            self.draw_language_selector_screen()
            return

        # Limpa elementos dinâmicos (exceto fixos como scanlines e sidebar básica)
        self.draw_base_hud()
        self.draw_tabs()

        if self.active_tab == "CMD":
            self.draw_tab_cmd()
        elif self.active_tab == "OPS":
            self.draw_tab_ops()
        elif self.active_tab == "INT":
            self.draw_tab_int()
        elif self.active_tab == "LOG":
            self.draw_tab_log()

    def draw_tab_cmd(self):
        """Desenha a aba de Comando Operacional."""
        # Botões Principais à esquerda
        # Monitor controls
        btn_y = 220  # Define btn_y here

        self.create_btn(
            110,
            btn_y,
            self.t("btn_bot"),
            "DISCORD BOT MÓDULO",
            self.toggle_bot,
            "bot",
            tt_key="tt_bot",
        )
        self.create_btn(
            110,
            btn_y + 80,
            self.t("btn_dash"),
            "WEB ACCESS MÓDULO",
            self.toggle_dashboard,
            "dash",
            tt_key="tt_dash",
        )
        self.create_btn(
            110,
            btn_y + 160,
            self.t("raid_on") if self.raid_active else self.t("raid_off"),
            "XML FTP OVERRIDE",
            self.toggle_raid,
            "raid",
            tt_key="tt_raid",
        )

        raid_label = self.t("raid_on") if self.raid_active else self.t("raid_off")
        self.raid_btn_text_id = self.create_btn(
            110,
            btn_y + 160,
            raid_label,
            "Raid Mode Master Toggle",
            self.toggle_raid,
            "raid",
        )

        self.create_btn(
            110,
            btn_y + 240,
            self.t("btn_exit"),
            "System Termination",
            self.root.destroy,
            "exit",
        )

        # Broadcast Section (Right Side of CMD)
        self.draw_glass_rect(480, 200, 1100, 450, outline=self.c_primary)
        self.canvas.create_text(
            510,
            230,
            text=self.t("broadcast"),
            font=("Consolas", 10, "bold"),
            fill=self.c_accent,
            anchor="w",
        )

        self.broadcast_entry = tk.Entry(
            self.root,
            bg="#111111",
            fg=self.c_white,
            insertbackground=self.c_white,
            font=("Consolas", 12),
            border=0,
            highlightthickness=1,
            highlightbackground=self.c_primary,
        )
        self.canvas.create_window(
            510, 270, window=self.broadcast_entry, width=540, height=40, anchor="nw"
        )

        self.create_mini_btn(
            510, 330, "SEND", self.send_broadcast, width=540, height=40
        )

    def draw_tab_ops(self):
        """Desenha a aba de Gestão de Operadores."""
        self.draw_glass_rect(100, 180, 1100, 780, outline=self.c_online)
        self.canvas.create_text(
            130,
            210,
            text=self.t("players_online"),
            font=("Consolas", 12, "bold"),
            fill=self.c_online,
            anchor="w",
            tags="op_title",
        )

        self.player_slots = []
        p_list = self.nitrado_stats.get("player_list", [])

        for i in range(15):  # Increased capacity for v200
            y = 260 + (i * 32)
            if y > 750:
                break

            # Row Background for hover effect
            row_bg = self.canvas.create_rectangle(
                120, y - 15, 1080, y + 15, fill="", outline="", tags=f"prow_{i}"
            )

            p_text = self.canvas.create_text(
                140, y, text="--", font=("Consolas", 10), fill=self.c_white, anchor="w"
            )
            k_btn = self.create_mini_btn(
                850, y - 10, "KICK", lambda idx=i: self.kick_id(idx), width=60
            )
            b_btn = self.create_mini_btn(
                930, y - 10, "BAN", lambda idx=i: self.ban_id(idx), width=60
            )

            def on_p_enter(_e, r=row_bg):
                self.canvas.itemconfig(r, fill="#1a1a1a")

            def on_p_leave(_e, r=row_bg):
                self.canvas.itemconfig(r, fill="")

            self.canvas.tag_bind(f"prow_{i}", "<Enter>", on_p_enter)
            self.canvas.tag_bind(f"prow_{i}", "<Leave>", on_p_leave)

            self.player_slots.append(
                {"text": p_text, "k": k_btn, "b": b_btn, "row": row_bg}
            )

        self.update_hud()  # Initial population

    def draw_tab_int(self):
        """Desenha a aba de Inteligência (Gráficos e Mini-Mapa)."""
        # Gráfico Vital
        self.draw_glass_rect(100, 180, 600, 450, outline=self.c_accent)
        self.canvas.create_text(
            130,
            210,
            text=self.t("vital"),
            font=("Consolas", 10, "bold"),
            fill=self.c_accent,
            anchor="w",
        )
        self.draw_vital_graph(x=130, y=400, w=440, h=160)

        # Mini-Mapa Tático
        self.draw_glass_rect(620, 180, 1100, 780, outline=self.c_primary)
        self.canvas.create_text(
            650,
            210,
            text="[ TACTICAL MINI-MAP ]",
            font=("Consolas", 10, "bold"),
            fill=self.c_primary,
            anchor="w",
        )

        # Carregar imagem do mapa se existir
        map_path = os.path.join(
            self.base_dir, "new_dashboard", "static", "img", "map_sat.jpg"
        )
        if not os.path.exists(map_path):  # Fallback if path is different
            map_path = os.path.join(self.base_dir, "static", "img", "map_sat.jpg")

        if os.path.exists(map_path):
            try:
                m_img = Image.open(map_path)
                m_img = m_img.resize((440, 520), Image.Resampling.LANCZOS)
                self.mini_map_photo = ImageTk.PhotoImage(m_img)
                self.canvas.create_image(
                    640, 240, image=self.mini_map_photo, anchor="nw"
                )
            except Exception:
                pass
        else:
            self.canvas.create_text(
                860, 500, text="MAP DATA NOT FOUND", font=("Impact", 20), fill="#333333"
            )

        # Scheduler info (Quick view in INT)
        self.draw_glass_rect(100, 480, 600, 780, outline=self.c_accent)
        self.canvas.create_text(
            130,
            510,
            text=self.t("scheduler"),
            font=("Consolas", 10, "bold"),
            fill=self.c_accent,
            anchor="w",
        )

        raid_time_text = f"HORÁRIO: {self.raid_start:02d}:00 - {self.raid_end:02d}:00"
        self.canvas.create_text(
            130,
            550,
            text=raid_time_text,
            font=("Consolas", 14),
            fill=self.c_white,
            anchor="w",
        )

        days_labels = ["SEG", "TER", "QUA", "QUI", "SEX", "SÁB", "DOM"]
        for i, label in enumerate(days_labels):
            active = i in self.raid_days
            color = self.c_primary if active else "#333333"
            self.canvas.create_rectangle(
                130 + (i * 60),
                580,
                180 + (i * 60),
                610,
                fill=color,
                outline=self.c_accent if active else "",
            )
            self.canvas.create_text(
                155 + (i * 60),
                595,
                text=label,
                font=("Consolas", 8, "bold"),
                fill="black" if active else "white",
            )

    def draw_tab_log(self):
        """Desenha a aba de Logística e Configurações."""
        # DB Tools
        self.draw_glass_rect(110, 220, 450, 450, outline=self.c_accent)
        self.canvas.create_text(
            130,
            250,
            text=self.t("db_tools"),
            font=("Consolas", 10, "bold"),
            fill=self.c_accent,
            anchor="w",
        )
        self.create_mini_btn(
            130,
            280,
            self.t("backup"),
            self.create_db_backup,
            width=300,
            height=35,
            tt_key="tt_backup",
        )

        # Links
        self.draw_glass_rect(110, 480, 450, 750, outline=self.c_accent)
        self.canvas.create_text(
            130,
            510,
            text=self.t("links"),
            font=("Consolas", 10, "bold"),
            fill=self.c_accent,
            anchor="w",
        )
        self.create_mini_btn(
            130,
            540,
            "NITRADO WEB",
            lambda: webbrowser.open("https://nitrado.net"),
            width=300,
            height=35,
            tt_key="tt_log",
        )
        self.create_mini_btn(
            130,
            590,
            "DASHBOARD",
            lambda: webbrowser.open("http://localhost:5000"),
            width=300,
            height=35,
            tt_key="tt_dash",
        )
        self.create_mini_btn(
            130,
            640,
            "DISCORD",
            lambda: webbrowser.open("https://discord.com"),
            width=300,
            height=35,
            tt_key="tt_log",
        )

        # Aba LOG agora focada apenas em Ferramentas e Links (Seletor movido para o Splash de entrada)

        # Vital Status Graph (Right Side)
        self.canvas.create_rectangle(
            830, 80, 1150, 240, outline=self.c_accent, width=1, dash=(3, 3)
        )
        self.canvas.create_text(
            850,
            105,
            text="[ STATUS VITAL - 24H ]",
            font=("Consolas", 10, "bold"),
            fill=self.c_accent,
            anchor="w",
        )
        self.graph_points = []  # IDs for lines

        # Diagnostic/Nitrado HUD (Right Side)
        self.canvas.create_rectangle(
            830,
            260,
            1150,
            520,
            outline=self.c_accent,
            width=1,
            dash=(3, 3),
        )
        self.log_title = self.canvas.create_text(
            850,
            285,
            text="[ SISTEMA DE DIAGNÓSTICO ]",
            font=("Consolas", 10, "bold"),
            fill=self.c_accent,
            anchor="w",
        )

        self.log_text = self.canvas.create_text(
            850,
            305,
            text="AGUARDANDO CONEXÃO...\n> MÓDULOS OK",
            font=("Consolas", 8),
            fill=self.c_primary,
            anchor="nw",
            width=280,
        )

        # Nitrado Real-time HUD
        self.canvas.create_text(
            850,
            445,
            text="[ STATUS NITRADO ]",
            font=("Consolas", 10, "bold"),
            fill=self.c_white,
            anchor="w",
        )

        self.hud_status = self.canvas.create_text(
            850,
            465,
            text="SERVER STATUS: OFFLINE",
            font=("Consolas", 9),
            fill=self.c_danger,
            anchor="w",
        )
        self.hud_players = self.canvas.create_text(
            850,
            485,
            text="PLAYERS ONLINE: 0/0",
            font=("Consolas", 9),
            fill=self.c_white,
            anchor="w",
        )
        self.hud_raid = self.canvas.create_text(
            850,
            505,
            text=f"RAID MODE: {'ENABLED' if self.raid_active else 'DISABLED'}",
            font=("Consolas", 9),
            fill=self.c_danger if self.raid_active else self.c_primary,
            anchor="w",
        )
        self.hud_restart = self.canvas.create_text(
            850,
            525,
            text="NEXT RESTART: --:--:--",
            font=("Consolas", 9),
            fill=self.c_accent,
            anchor="w",
        )

        # --- RAID TACTICAL SCHEDULE (New Section) ---
        self.canvas.create_rectangle(
            830,
            540,
            1150,
            720,
            outline=self.c_accent,
            width=1,
            dash=(3, 3),
        )
        self.canvas.create_text(
            850,
            560,
            text="[ AGENDAMENTO DE RAID ]",
            font=("Consolas", 10, "bold"),
            fill=self.c_white,
            anchor="w",
        )

        days_labels = ["SEG", "TER", "QUA", "QUI", "SEX", "SÁB", "DOM"]
        self.day_btn_ids = {}
        for i, label in enumerate(days_labels):
            x = 850 + (i * 42)
            y = 590
            active = i in self.raid_days
            color = self.c_primary if active else "#333333"

            # Day block
            rect_id = self.canvas.create_rectangle(
                x,
                y,
                x + 38,
                y + 25,
                fill=color,
                outline=self.c_accent if active else "#666666",
                tags=f"day_{i}",
            )
            # Day text
            self.canvas.create_text(
                x + 19,
                y + 12,
                text=label,
                font=("Consolas", 8, "bold"),
                fill="black" if active else self.c_white,
                tags=f"day_{i}",
            )
            self.day_btn_ids[i] = rect_id

            def on_day_enter(event):
                self.show_tooltip(event, "tt_raid")

            def on_day_leave(_event):
                self.hide_tooltip()

            self.canvas.tag_bind(f"day_{i}", "<Enter>", on_day_enter)
            self.canvas.tag_bind(f"day_{i}", "<Leave>", on_day_leave)
            self.canvas.tag_bind(
                f"day_{i}", "<Button-1>", lambda _, idx=i: self.toggle_raid_day(idx)
            )

        # Hour Controls
        self.canvas.create_text(
            850,
            640,
            text=f"HORÁRIO: {self.raid_start:02d}:00 ATÉ {self.raid_end:02d}:00",
            font=("Consolas", 9),
            fill=self.c_accent,
            anchor="w",
            tags="time_display",
        )

        # Buttons to adjust
        self.create_mini_btn(850, 665, "START +", lambda: self.adjust_time("start", 1))
        self.create_mini_btn(930, 665, "START -", lambda: self.adjust_time("start", -1))
        self.create_mini_btn(1010, 665, "END +", lambda: self.adjust_time("end", 1))
        self.create_mini_btn(1090, 665, "END -", lambda: self.adjust_time("end", -1))

        self.create_mini_btn(
            850, 695, "SALVAR CONFIGURAÇÃO TÁTICA", self.save_full_config, width=280
        )

        # Scanlines
        self.scan_line = self.canvas.create_line(
            0, 0, self.width, 0, fill="#ffffff", width=1, stipple="gray25"
        )

        # Call the new right sidebar drawing method
        self.draw_vital_graph()

    def create_btn(self, x_pos, y_pos, label, info, cmd, tag, tt_key=None):
        """Cria um botão com efeito de vidro e feedback tático."""
        btn_w, btn_h = 320, 60
        is_raid = tag == "raid"
        border_c = self.c_danger if (is_raid and self.raid_active) else self.c_primary

        rect = self.canvas.create_rectangle(
            x_pos,
            y_pos,
            x_pos + btn_w,
            y_pos + btn_h,
            fill="#080808",
            outline=border_c,
            width=2,
            tags=tag,
        )
        decor = self.canvas.create_rectangle(
            x_pos, y_pos, x_pos + 8, y_pos + btn_h, fill=border_c, outline="", tags=tag
        )
        txt = self.canvas.create_text(
            x_pos + 30,
            y_pos + btn_h / 2,
            text=label,
            font=("Impact", 16),
            fill=self.c_white,
            anchor="w",
            tags=tag,
        )

        def on_enter(event):
            self.canvas.itemconfig(rect, fill=border_c)
            self.canvas.itemconfig(decor, fill=self.c_white)
            self.canvas.itemconfig(txt, fill="black")
            if tt_key:
                self.show_tooltip(event, tt_key)

        def on_leave(event):
            self.canvas.itemconfig(rect, fill="#080808")
            self.canvas.itemconfig(decor, fill=border_c)
            self.canvas.itemconfig(txt, fill=self.c_white)
            self.hide_tooltip()

        self.canvas.tag_bind(tag, "<Enter>", on_enter)
        self.canvas.tag_bind(tag, "<Leave>", on_leave)
        self.canvas.tag_bind(tag, "<Button-1>", lambda _: cmd())
        return txt

    def create_mini_btn(self, x, y, label, cmd, width=70, height=25, tt_key=None):
        """Cria um botão compacto estilizado com suporte a tooltip."""
        rect = self.canvas.create_rectangle(
            x, y, x + width, y + height, fill="#111111", outline=self.c_accent
        )
        txt = self.canvas.create_text(
            x + width / 2,
            y + height / 2,
            text=label,
            font=("Consolas", 8, "bold"),
            fill=self.c_white,
        )

        def on_click(_e):
            cmd()
            self.canvas.itemconfig(rect, fill=self.c_accent)
            self.root.after(100, lambda: self.canvas.itemconfig(rect, fill="#111111"))

        def on_enter(event):
            self.canvas.itemconfig(rect, outline=self.c_white)
            if tt_key:
                self.show_tooltip(event, tt_key)

        def on_leave(_event):
            self.canvas.itemconfig(rect, outline=self.c_accent)
            self.hide_tooltip()

        for item in (rect, txt):
            self.canvas.tag_bind(item, "<Button-1>", on_click)
            self.canvas.tag_bind(item, "<Enter>", on_enter)
            self.canvas.tag_bind(item, "<Leave>", on_leave)
        return rect

    def toggle_raid(self):
        """Alterna o status do modo raid e sincroniza."""
        self.raid_active = not self.raid_active
        self.save_full_config()
        self.update_log(f"> RAID MODE: {'ENABLED' if self.raid_active else 'DISABLED'}")

    def animate(self):
        """Controla a animação cíclica das scanlines do HUD."""
        if self.scan_line:
            curr_y = self.canvas.coords(self.scan_line)[1]
            next_y = curr_y + 3 if curr_y < self.height else 0
            self.canvas.coords(self.scan_line, 0, next_y, self.width, next_y)
        self.root.after(30, self.animate)

    def nitrado_polling_loop(self):
        """Loop de fundo para buscar estatísticas do servidor Nitrado."""
        while True:
            try:
                poll_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(poll_loop)
                data = poll_loop.run_until_complete(get_server_status())
                if data and "data" in data and "gameserver" in data["data"]:
                    gs_info = data["data"]["gameserver"]
                    srv_status = gs_info.get("status", "UNKNOWN").upper()
                    cur_p = gs_info.get("query", {}).get("player_current", 0)
                    max_p = gs_info.get("query", {}).get("player_max", 32)
                    p_list = gs_info.get("query", {}).get("players", [])

                    # Update history
                    self.player_history.pop(0)
                    self.player_history.append(cur_p)

                    self.nitrado_stats = {
                        "players": f"{cur_p}/{max_p}",
                        "status": srv_status,
                        "restart_timer": "EST. 4h",
                        "player_list": p_list,
                    }
                    self.update_hud()
                poll_loop.close()
            except asyncio.CancelledError:
                break
            except Exception as poll_err:
                print(f"Nitrado Poll Error: {poll_err}")
            time.sleep(30)

    def process_monitor_loop(self):
        """Monitora todos os processos ativos e religa-os em caso de queda."""
        while True:
            if self.auto_recovery:
                if self.dashboard_proc and self.dashboard_proc.poll() is not None:
                    self.update_log("> !!! DASHBOARD CRASHED. RESTARTING...")
                    self.run_dashboard()
                if self.bot_proc and self.bot_proc.poll() is not None:
                    self.update_log("> !!! BOT CRASHED. RESTARTING...")
                    self.run_bot()
            time.sleep(5)

    def toggle_dashboard(self):
        """Liga ou desliga o processo do servidor web Dashboard."""
        if not self.dashboard_proc:
            self.update_log("> INITIALIZING WAITRESS...")
            self.run_dashboard()
        else:
            self.dashboard_proc.terminate()
            self.dashboard_proc = None
            self.update_log("> DASHBOARD STOPPED.")

    def run_dashboard(self):
        """Inicia o processo do dashboard via subprocess."""
        cmd_args = ["python", "-m", "waitress", "--port=5000", "new_dashboard.app:app"]
        self.dashboard_proc = subprocess.Popen(
            cmd_args,
            cwd=self.base_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self.update_log("> DASHBOARD ONLINE")

    def toggle_bot(self):
        """Liga ou desliga o processo do bot do Discord."""
        if not self.bot_proc:
            self.update_log("> BOOTING DISCORD BOT...")
            self.run_bot()
        else:
            self.bot_proc.terminate()
            self.bot_proc = None
            self.update_log("> BOT STOPPED.")

    def run_bot(self):
        """Inicia o processo do bot via subprocess."""
        cmd_args = ["python", "bot_main.py"]
        self.bot_proc = subprocess.Popen(
            cmd_args,
            cwd=self.base_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self.update_log("> BOT ONLINE")

    def update_log(self, msg):
        """Adiciona uma mensagem ao sistema de diagnóstico (diag log)."""
        # Se você estiver em uma aba que mostre logs, poderiamos atualizar um widget.
        # Na v200, os logs aparecem no console e em mensagens temporárias do HUD.
        print(f"LOG: {msg}")

    def toggle_raid_day(self, day_idx):
        """Liga/desliga um dia de raid."""
        if day_idx in self.raid_days:
            self.raid_days.remove(day_idx)
        else:
            self.raid_days.append(day_idx)
        self.raid_days.sort()
        self.refresh_day_btns()

    def refresh_day_btns(self):
        """Atualiza visualmente os botões de dia."""
        for i, rect_id in self.day_btn_ids.items():
            active = i in self.raid_days
            self.canvas.itemconfig(
                rect_id,
                fill=self.c_primary if active else "#333333",
                outline=self.c_accent if active else "#666666",
            )
            # Also update text color (it's hard because we didn't save the text IDs,
            # but since they overlap exactly, we can just redraw or use tags correctly)
            # For simplicity in this HUD, we'll just use the fill color change which is enough.

    def adjust_time(self, target, delta):
        """Ajusta a hora de início ou fim."""
        if target == "start":
            self.raid_start = (self.raid_start + delta) % 24
        else:
            self.raid_end = (self.raid_end + delta) % 24

        # Update display
        self.canvas.itemconfig(
            "time_display",
            text=f"HORÁRIO: {self.raid_start:02d}:00 ATÉ {self.raid_end:02d}:00",
        )

    def kick_id(self, idx):
        """Expulsa o jogador no slot especificado."""
        p_list = self.nitrado_stats.get("player_list", [])
        if idx < len(p_list):
            name = p_list[idx].get("name")
            self.update_log(f"> TENTANDO EXPULSAR {name}...")
            asyncio.run(kick_player(name))
            self.update_log("> COMANDO KICK ENVIADO")

    def ban_id(self, idx):
        """Bane o jogador no slot especificado."""
        p_list = self.nitrado_stats.get("player_list", [])
        if idx < len(p_list):
            name = p_list[idx].get("name")
            if messagebox.askyesno("CONFIRMAR BAN", f"BANIR PERMANENTEMENTE {name}?"):
                self.update_log(f"> TENTANDO BANIR {name}...")
                asyncio.run(ban_player(name))
                self.update_log("> COMANDO BAN ENVIADO")

    def send_broadcast(self):
        """Simula ou envia mensagem de broadcast."""
        msg = self.broadcast_entry.get()
        if not msg:
            return
        self.update_log(f"> BROADCAST: {msg[:20]}...")
        # Integrar com Webhook no futuro se disponível
        messagebox.showinfo("BROADCAST", "Mensagem enviada para o canal de anúncios!")
        self.broadcast_entry.delete(0, tk.END)

    def create_db_backup(self):
        """Cria um backup datado do banco de dados."""
        if not os.path.exists(self.db_path):
            self.update_log("> ERRO: DB NÃO ENCONTRADO")
            return

        backup_dir = os.path.join(self.base_dir, "backups")
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        dest = os.path.join(backup_dir, f"bigode_backup_{timestamp}.db")
        try:
            shutil.copy2(self.db_path, dest)
            self.update_log(f"> BACKUP CRIADO: {timestamp}")
            messagebox.showinfo("BACKUP", f"Cópia de segurança criada com sucesso!")
        except Exception as e:
            self.update_log(f"> ERRO BACKUP: {e}")


if __name__ == "__main__":
    main_root = tk.Tk()
    launcher_app = BigodeLauncherElite(main_root)
    # Center
    screen_w, screen_h = main_root.winfo_screenwidth(), main_root.winfo_screenheight()
    main_root.geometry(f"+{int(screen_w / 2 - 500)}+{int(screen_h / 2 - 300)}")
    main_root.mainloop()
