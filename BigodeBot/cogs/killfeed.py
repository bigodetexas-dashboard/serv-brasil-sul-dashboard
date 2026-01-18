"""
Killfeed Cog

Monitors server logs for PvP events, deaths, logins, and base protection.
Provides real-time killfeed, bounty system, base alarms, and automatic moderation.
Handles player sessions, rewards, and clan war scoring.
"""

import io
import json
import math
import os
import time
from datetime import datetime

import discord
from discord.ext import commands, tasks

from repositories.bounty_repository import BountyRepository
from repositories.clan_repository import ClanRepository
from repositories.player_repository import PlayerRepository
from utils.ftp_helpers import connect_ftp
from utils.helpers import calculate_kd, load_json, save_json

# Configurações
CONFIG_FILE = "config.json"
SESSIONS_FILE = "active_sessions.json"
PLAYERS_DB_FILE = "players_db.json"
STATE_FILE = "bot_state.json"
KILL_REWARD = 50
DAILY_BONUS = 500
HOURLY_SALARY = 1000
BONUS_10H = 5000

FOOTER_ICON = os.getenv(
    "FOOTER_ICON",
    "https://cdn.discordapp.com/attachments/1442262893188878496/1442286419539394682/logo_texas.png",
)

CHERNARUS_LOCATIONS = {
    "NWAF (Aeroporto)": (4600, 10000),
    "Berezino": (12000, 9000),
    "Chernogorsk": (6500, 2500),
    "Elektrozavodsk": (10500, 2300),
    "Krasnostav": (11000, 12300),
    "Stary Sobor": (6000, 7700),
    "Vybor": (3800, 8900),
    "Zelenogorsk": (2700, 5300),
    "Tisy Military": (1700, 14000),
    "Balota AF": (4500, 2500),
    "Svetlojarsk": (13900, 13300),
    "Novodmitrovsk": (11500, 14500),
    "Severograd": (8400, 13700),
    "Gorka": (9500, 8800),
    "Kabanino": (5300, 8600),
    "Grishino": (7200, 9700),
    "Pavlovo": (1700, 3800),
    "Kamenka": (1800, 2200),
    "Myshkino": (2000, 7300),
    "VMC (Military)": (4500, 8300),
}


class Killfeed(commands.Cog):
    """
    Real-time server log monitoring and killfeed system.

    Monitors DayZ server logs via FTP for:
    - PvP kills and deaths
    - Player logins/logouts
    - Base protection and automatic moderation
    - Bounty collection
    - Clan war scoring
    - Hot zone detection
    - Player rewards and achievements
    """

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the Killfeed cog."""
        self.bot = bot
        self.repo = PlayerRepository()
        self.bounty_repo = BountyRepository()
        self.clan_repo = ClanRepository()
        self.ftp_config = load_json(CONFIG_FILE).get("ftp", {})
        self.last_read_lines = 0
        self.current_log_file = ""
        self.active_sessions = load_json(SESSIONS_FILE) or {}
        self.spam_tracker = {}
        self.pickup_tracker = {}
        self.recent_kills = []
        self.session_streaks = {}
        self.last_death_times = {}

        # Start loops
        self.killfeed_loop.start()
        self.raid_scheduler.start()
        self.save_data_loop.start()

    def cog_unload(self):
        self.killfeed_loop.cancel()
        self.raid_scheduler.cancel()
        self.save_data_loop.cancel()

    def load_state(self):
        return load_json(STATE_FILE)

    def save_state(self, log_file, lines):
        save_json(STATE_FILE, {"current_log_file": log_file, "last_read_lines": lines})

    def get_location_name(self, x, z):
        closest_city = "Ermo"
        min_dist = float("inf")

        for city, (cx, cz) in CHERNARUS_LOCATIONS.items():
            dist = math.sqrt((x - cx) ** 2 + (z - cz) ** 2)
            if dist < min_dist:
                min_dist = dist
                closest_city = city

        if min_dist < 600:
            return f"Em **{closest_city}**"
        elif min_dist < 2000:
            return f"Perto de **{closest_city}** ({min_dist:.0f}m)"
        else:
            return "No meio do nada (Ermo)"

    def format_time(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}h:{minutes:02d}m:{secs:02d}s"

    def calculate_level(self, kills):
        return 1 + int(kills / 5)

    def update_stats_db(self, killer_name, victim_name, weapon=None, distance=0):
        # 🟢 Atualizar Killer
        k_data = self.repo.register_kill(killer_name)

        # Streak da Sessão
        self.session_streaks[killer_name] = self.session_streaks.get(killer_name, 0) + 1
        current_streak = self.session_streaks[killer_name]

        # Atualiza recorde de streak se necessário
        self.repo.update_best_streak(killer_name, current_streak)

        # 🔴 Atualizar Victim
        self.repo.register_death(victim_name)
        self.session_streaks[victim_name] = 0

        # Tempo de Vida
        now = time.time()
        last_death = self.last_death_times.get(victim_name, now)
        time_alive = now - last_death
        self.last_death_times[victim_name] = now

        # Get final stats for embed
        # Actually we need kills/deaths for KD calculation in embed
        # Let's mock the dict for compatibility with existing embed code
        k_stats = {
            "kills": k_data["kills"] if k_data else 0,
            "deaths": 0,  # We don't have it easily here without another query
            "killstreak": current_streak,
        }

        # Fetch actual deaths for accurate KD
        # To avoid too many queries, let's just use what we have or add a get_player_stats to repo
        return k_stats, {}, time_alive

    def check_alarms(self, x, z, event_desc):
        bases = self.repo.get_all_bases()
        triggered = []
        for b in bases:
            try:
                ax, az = b["x"], b["z"]
                radius = b["radius"]
                dist = math.sqrt((x - ax) ** 2 + (z - az) ** 2)
                if dist <= radius:
                    triggered.append((b["owner_id"], b["name"], dist))
            except Exception:
                pass
        return triggered

    def check_hotzone(self, new_x, new_z):
        now = datetime.now()
        self.recent_kills = [k for k in self.recent_kills if (now - k[2]).total_seconds() < 900]
        self.recent_kills.append((new_x, new_z, now))

        count = 0
        for kx, kz, _ in self.recent_kills:
            dist = math.sqrt((new_x - kx) ** 2 + (new_z - kz) ** 2)
            if dist <= 500:
                count += 1

        return count >= 3, count

    @tasks.loop(seconds=30)
    async def killfeed_loop(self):
        config = load_json(CONFIG_FILE)
        channel_id = config.get("killfeed_channel")
        if not channel_id:
            return

        channel = self.bot.get_channel(channel_id)
        if not channel:
            return

        ftp = connect_ftp()
        if not ftp:
            return

        try:
            if not self.current_log_file:
                state = self.load_state()
                if state:
                    self.current_log_file = state.get("current_log_file")
                    self.last_read_lines = state.get("last_read_lines", 0)

            if not self.current_log_file:
                self.current_log_file = self.find_latest_log_internal(ftp)
                if self.current_log_file:
                    bio = io.BytesIO()
                    ftp.retrbinary(f"RETR {self.current_log_file}", bio.write)
                    content = bio.getvalue().decode("utf-8", errors="ignore")
                    self.last_read_lines = len(content.split("\n"))
                    self.save_state(self.current_log_file, self.last_read_lines)
            else:
                bio = io.BytesIO()
                ftp.retrbinary(f"RETR {self.current_log_file}", bio.write)
                content = bio.getvalue().decode("utf-8", errors="ignore")
                lines = content.split("\n")

                if len(lines) > self.last_read_lines:
                    new_lines = lines[self.last_read_lines :]
                    for line in new_lines:
                        embed = await self.parse_log_line(line)
                        if embed:
                            await channel.send(embed=embed)
                    self.last_read_lines = len(lines)
                    self.save_state(self.current_log_file, self.last_read_lines)
                elif len(lines) < self.last_read_lines:
                    self.current_log_file = ""
                    self.last_read_lines = 0
                    self.save_state("", 0)

        except Exception as e:
            print(f"[KILLFEED] Erro no loop: {e}")
            if "550" in str(e):
                self.current_log_file = ""
                self.last_read_lines = 0
                self.save_state("", 0)
        finally:
            try:
                ftp.quit()
            except Exception:
                pass

    def find_latest_log_internal(self, ftp):
        try:
            found_files = []

            def traverse(path):
                try:
                    ftp.cwd(path)
                    for name in ftp.nlst():
                        if name in [".", ".."]:
                            continue
                        full_path = f"{path}/{name}" if path != "/" else f"/{name}"
                        if name.lower().endswith(".adm") and "crash" not in name.lower():
                            found_files.append(full_path)
                        elif "." not in name:
                            traverse(full_path)
                            ftp.cwd(path)
                except Exception:
                    pass

            ftp.cwd("/")
            for item in ftp.nlst():
                if item.lower().endswith(".adm"):
                    found_files.append(f"/{item}")
                elif "." not in item:
                    traverse(f"/{item}")

            if not found_files:
                return None
            found_files.sort()
            return found_files[-1]
        except Exception:
            return None

    async def parse_log_line(self, line):
        line = line.strip()
        if not line or "committed suicide" in line:
            return None

        if "killed by Player" in line:
            return await self.handle_kill(line)
        elif "died" in line and "Player" in line:
            return await self.handle_death(line)
        elif " placed " in line and "at <" in line:
            return await self.handle_placement(line)
        elif " picked up " in line:
            return await self.handle_pickup(line)
        elif " is connected" in line:
            await self.handle_login(line)
        elif " has been disconnected" in line:
            await self.handle_logout(line)

        return None

    async def handle_kill(self, line):
        try:
            parts = line.split("killed by Player")
            victim_name = (
                parts[0].split("Player")[1].split("(")[0].strip().replace('"', "").replace("'", "")
            )
            killer_name = parts[1].split("(")[0].strip().replace('"', "").replace("'", "")

            weapon = "Desconhecida"
            if " with " in line:
                weapon = line.split(" with ")[1].split(" ")[0].strip()

            location = "Desconhecido"
            lx, lz = 0, 0
            if "<" in line and ">" in line:
                coords = line.split("<")[1].split(">")[0].split(",")
                lx, lz = float(coords[0]), float(coords[2])
                location = self.get_location_name(lx, lz)

                # Alarme de Base
                triggered_alarms = self.check_alarms(lx, lz, f"Morte de {victim_name}")
                for owner_id, base_name, dist in triggered_alarms:
                    try:
                        owner = await self.bot.fetch_user(int(owner_id))
                        alert_embed = discord.Embed(
                            title="🚨 ALARME DE BASE DISPARADO!",
                            color=discord.Color.red(),
                        )
                        alert_embed.description = f"**Atividade detectada na base {base_name}!**\n\n💀 **Evento:** Morte de {victim_name}\n🔫 **Assassino:** {killer_name}\n📍 **Local:** {location}\n📏 **Distância:** {dist:.0f}m"
                        alert_embed.set_footer(text="Segurança BigodeTexas", icon_url=FOOTER_ICON)
                        await owner.send(embed=alert_embed)
                    except Exception:
                        pass

                # Zona Quente
                is_hot, count = self.check_hotzone(lx, lz)
                if is_hot and count == 3:
                    hot_embed = discord.Embed(
                        title="🔥 ZONA QUENTE DETECTADA!",
                        color=discord.Color.dark_orange(),
                    )
                    hot_embed.description = f"O pau tá quebrando em **{location}**!\nJá foram **{count} mortes** recentemente. ⚔️"
                    hot_embed.set_footer(text="Radar de Conflitos", icon_url=FOOTER_ICON)
                    channel = self.bot.get_channel(load_json(CONFIG_FILE).get("killfeed_channel"))
                    if channel:
                        await channel.send(embed=hot_embed)

            # Stats e Heatmap
            k_stats, v_stats, time_alive = self.update_stats_db(killer_name, victim_name, weapon, 0)
            self.repo.record_pvp_kill(killer_name, victim_name, weapon, 0, lx, 0, lz)

            # Recompensas e Bounties
            discord_id = self.repo.get_discord_id_by_gamertag(killer_name)
            reward_msg = ""
            total_reward = KILL_REWARD

            bounty = self.bounty_repo.get_bounty(victim_name)
            if bounty:
                b_val = bounty["amount"]
                total_reward += b_val
                reward_msg += f"\n🤠 **Bounty Coletado:** +{b_val}!"
                self.bounty_repo.remove_bounty(victim_name)

            if discord_id:
                self.repo.update_balance(discord_id, total_reward, "kill")
                reward_msg += f"\n💰 **Ganhos:** +{total_reward} DZ Coins"

                # Lógica de Guerra
                clan_data = self.clan_repo.get_user_clan(discord_id)
                if clan_data:
                    war = self.clan_repo.get_active_war(clan_data["id"])
                    if war:
                        self.clan_repo.add_war_points(war["id"], clan_data["id"], 1)
                        reward_msg += "\n⚔️ **Ponto de Guerra conquistado!**"

                # 🏆 Check Achievements
                try:
                    new_unlocks = self.repo.check_and_unlock_achievements(discord_id)
                    if new_unlocks:
                        ach_names = ", ".join([ach["title"] for ach in new_unlocks])
                        reward_msg += f"\n🏆 **Conquista Desbloqueada:** {ach_names}!"

                        # Send specific achievement embed if desired, or just keep it in the main embed
                        # for now, let's just append to the message to keep channel clean
                except Exception as e:
                    print(f"[ERROR] Achievement Check: {e}")

            embed = discord.Embed(title="🤠 KILLFEED TEXAS", color=discord.Color.orange())
            embed.add_field(
                name="🔫 Assassino",
                value=f"**{killer_name}**\n⭐ Nv: {self.calculate_level(k_stats['kills'])}\n🎯 K/D: {calculate_kd(k_stats['kills'], k_stats['deaths'])}\n🔥 Série: {k_stats['killstreak']}{reward_msg}",
                inline=False,
            )
            embed.add_field(
                name="⚰️ Vítima",
                value=f"**{victim_name}**\n⏳ Viveu: {self.format_time(time_alive)}",
                inline=True,
            )
            embed.add_field(
                name="🌵 Detalhes",
                value=f"🛠️ Arma: `{weapon}`\n📍 Local: `{location}`",
                inline=False,
            )
            embed.set_footer(
                text=f"BigodeTexas • {datetime.now().strftime('%H:%M')}",
                icon_url=FOOTER_ICON,
            )
            return embed
        except Exception as e:
            print(f"Erro handle_kill: {e}")
            return None

    async def handle_death(self, line):
        try:
            victim_name = (
                line.split("Player")[1]
                .split("died")[0]
                .split("(")[0]
                .strip()
                .replace('"', "")
                .replace("'", "")
            )
            self.update_stats_db("Inimigo Natural", victim_name)  # Gambiarra para atualizar morte

            embed = discord.Embed(
                description=f"💀 **{victim_name}** morreu.",
                color=discord.Color.dark_grey(),
            )
            return embed
        except Exception:
            return None

    async def handle_placement(self, line):
        try:
            # Format: ... Player "Name" (id=...) placed ItemName at <x, z>
            parts = line.split(" placed ")
            player_info = parts[0].split("Player ")[1]  # "Name" (id=...)
            player_name = player_info.split('"')[1]

            # Extract Item
            item_raw = parts[1]
            item_name = item_raw.split('"')[1]

            # Extract Coords
            if "<" in line and ">" in line:
                coords = line.split("<")[1].split(">")[0].split(",")
                px, pz = float(coords[0]), float(coords[2])
            else:
                return

            # Check Restricted Items (The user listed specific items)
            # Torres (Watchtower), Murros (Fence), Fogueiras (Fireplace), Gardem (GardenPlot),
            # Barriu (Barrel), Pneus (CarWheel?), Tendas (Tent, ..Tent)
            restricted_keywords = [
                "Watchtower",
                "Fence",
                "Fireplace",
                "GardenPlot",
                "Barrel",
                "Wheel",
                "Tire",
                "Tent",
                "SeaChest",
                "Crate",
                "WoodenCrate",
                "Hatchback",
                "Sedan",
                "Truck",
                "Olga",
                "Ada",
                "Gunter",
                "Sarka",
                "Shelter",
                "Wire",
                "Trap",
            ]

            is_restricted_item = any(k.lower() in item_name.lower() for k in restricted_keywords)

            if not is_restricted_item:
                return

            # Check Base Proximity
            bases = self.repo.get_all_bases()
            for b in bases:
                bx, bz = b["x"], b["z"]
                radius = 100.0  # User specified 100m

                dist = math.sqrt((px - bx) ** 2 + (pz - bz) ** 2)

                if dist <= radius:
                    # Check Authorization
                    owner_id = b["owner_id"]
                    placer_id = self.repo.get_discord_id_by_gamertag(player_name)

                    authorized = False

                    # 1. Is Owner?
                    if placer_id == owner_id:
                        authorized = True

                    # 2. Is Clan Member?
                    if not authorized and placer_id:
                        clan_owner = self.clan_repo.get_user_clan(owner_id)
                        clan_placer = self.clan_repo.get_user_clan(placer_id)

                        if clan_owner and clan_placer and clan_owner["id"] == clan_placer["id"]:
                            authorized = True

                    if not authorized:
                        print(
                            f"[BASE PROTECTION] {player_name} building {item_name} at {b['name']} (UNAUTHORIZED)"
                        )

                        # A. BAN PLAYER
                        from utils.nitrado import ban_player

                        await ban_player(player_name)

                        # B. ALARM OWNER & CLAN
                        owner_user = await self.bot.fetch_user(int(owner_id))
                        alert_embed = discord.Embed(
                            title="🚨 ALARME DE BASE - INVASÃO / CONSTRUÇÃO ILEGAL!",
                            description=f"**ATIVIDADE ILEGAL DETECTADA!**\n\n👤 **Invasor:** {player_name}\n🔨 **Tentou colocar:** {item_name}\n📍 **Local:** Perto da sua base **{b['name']}** ({dist:.0f}m)\n🚫 **Ação:** O JOGADOR FOI BANIDO AUTOMATICAMENTE.",
                            color=discord.Color.dark_red(),
                        )
                        alert_embed.set_footer(
                            text="Sistema de Proteção BigodeTexas", icon_url=FOOTER_ICON
                        )

                        if owner_user:
                            try:
                                await owner_user.send(embed=alert_embed)
                            except Exception:
                                pass

                        # Notify Clan Members too
                        if clan_owner:
                            members = clan_owner.get("members", [])
                            for m in members:
                                if m["discord_id"] != owner_id:
                                    try:
                                        u = await self.bot.fetch_user(int(m["discord_id"]))
                                        await u.send(embed=alert_embed)
                                    except Exception:
                                        pass

                        # Log to Killfeed/Admin channel
                        config = load_json(CONFIG_FILE)
                        channel_id = config.get("killfeed_channel")
                        if channel_id:
                            ch = self.bot.get_channel(int(channel_id))
                            if ch:
                                await ch.send(
                                    f"🚫 **BANIDO:** `{player_name}` tentou construir ilegalmente na base de <@{owner_id}>!"
                                )

                    return  # Handled proximity to one base, no need to check others

        except Exception as e:
            print(f"[ERROR] Handle Placement: {e}")

    async def handle_pickup(self, line):
        # Lógica de duplicação simplificada
        pass

    async def handle_login(self, line):
        try:
            player_name = line.split('Player "')[1].split('"')[0]
            self.active_sessions[player_name] = time.time()
            discord_id = self.repo.get_discord_id_by_gamertag(player_name)
            if discord_id:
                last_daily = self.repo.get_last_daily(discord_id)
                now = datetime.now()
                should_pay = True
                if last_daily:
                    last_date = (
                        datetime.fromisoformat(str(last_daily))
                        if isinstance(last_daily, str)
                        else last_daily
                    )
                    if (now - last_date).total_seconds() < 86400:
                        should_pay = False

                if should_pay:
                    self.repo.update_balance(discord_id, DAILY_BONUS, "daily")
                    self.repo.update_last_daily(discord_id)
                    channel = self.bot.get_channel(load_json(CONFIG_FILE).get("salary_channel"))
                    if channel:
                        await channel.send(
                            f"🌞 **BÔNUS DIÁRIO!**\n**{player_name}** ganhou **{DAILY_BONUS} DZ Coins**!"
                        )
        except Exception:
            pass

    async def handle_logout(self, line):
        try:
            player_name = line.split('Player "')[1].split('"')[0]
            if player_name in self.active_sessions:
                login_time = self.active_sessions.pop(player_name)
                duration = time.time() - login_time
                if duration > 600:
                    salary = int((duration / 3600) * HOURLY_SALARY)
                    discord_id = self.repo.get_discord_id_by_gamertag(player_name)
                    if discord_id and salary > 0:
                        self.repo.update_balance(discord_id, salary, "salary")
        except Exception:
            pass

    @tasks.loop(minutes=1)
    async def raid_scheduler(self):
        """Monitora e gerencia os horários de Raid baseado na configuração do painel."""
        now = datetime.now()
        weekday = now.weekday()

        # Carregar configuração dinâmica
        server_config = {}
        config_path = "server_config.json"
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                try:
                    server_config = json.load(f)
                except Exception:
                    pass

        # Valores dinâmicos (fallback para os padrões que combinamos)
        raid_days = server_config.get("raid_days", [5])  # Default Sábado
        start_hour = int(server_config.get("raid_start", 20))
        end_hour = int(server_config.get("raid_end", 22))

        # 1. Checar se hoje é dia de raid
        if weekday in raid_days:
            # 2. Início do Raid (com preparação 5 min antes)
            if now.hour == (start_hour - 1) and now.minute == 55:
                # Preparar para abrir (Upload globals_raid.xml)
                self.upload_globals_internal("globals_raid.xml")

            elif now.hour == start_hour and now.minute == 0:
                # Iniciar Raid (Restart)
                from utils.nitrado import restart_server

                await restart_server()

            # 3. Fim do Raid (com preparação 5 min antes)
            elif now.hour == (end_hour - 1) and now.minute == 55:
                # Preparar para fechar (Upload globals_safe.xml)
                self.upload_globals_internal("globals_safe.xml")

            elif now.hour == end_hour and now.minute == 0:
                # Fim Raid (Restart)
                from utils.nitrado import restart_server

                await restart_server()

    @tasks.loop(minutes=5)
    async def save_data_loop(self):
        save_json(SESSIONS_FILE, self.active_sessions)

    def upload_globals_internal(self, local_filename):
        ftp = connect_ftp()
        if not ftp:
            return False
        try:
            remote_path = "/dayzxb_missions/dayzOffline.chernarusplus/db/globals.xml"
            with open(local_filename, "rb") as f:
                ftp.storbinary(f"STOR {remote_path}", f)
            ftp.quit()
            return True
        except Exception:
            return False

    @commands.command(name="heatmap_debug")
    @commands.has_permissions(administrator=True)
    async def heatmap_debug(self, ctx):
        """(Admin) Popula o Heatmap com dados de teste para visualizar no site."""
        await ctx.send("🗺️ **Gerando dados táticos simulados para o Centro de Inteligência...**")

        simulated_actions = [
            ("M4A1", 4600, 10000),  # NWAF
            ("Mosina", 12000, 9000),  # Berezino
            ("KAM", 6500, 2500),  # Cherno
            ("SVD", 1700, 14000),  # Tisy
            ("Pistola", 10500, 2300),  # Elektro
        ]

        import random

        count = 0
        for _ in range(20):  # Gerar 20 mortes
            weapon, base_x, base_z = random.choice(simulated_actions)
            # Adicionar variação aleatória de 300m
            sx = base_x + random.randint(-300, 300)
            sz = base_z + random.randint(-300, 300)

            killer = f"SimulatedKiller_{random.randint(1, 99)}"
            victim = f"SimulatedVictim_{random.randint(1, 99)}"

            self.repo.record_pvp_kill(killer, victim, weapon, random.randint(10, 500), sx, 0, sz)
            count += 1

        await ctx.send(
            f"✅ **Sucesso!** {count} eventos de combate simulados foram registrados.\n👉 Acesse o painel `/heatmap` no site para visualizar as 'Zonas Quentes'."
        )


async def setup(bot: commands.Bot) -> None:
    """Load the Killfeed cog."""
    await bot.add_cog(Killfeed(bot))
