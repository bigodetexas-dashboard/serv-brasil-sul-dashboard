"""
Administrative commands cog for BigodeBot.
Provides server management, spawn system, and gameplay configuration commands.
"""

import asyncio
import os
from datetime import datetime

import discord
from discord.ext import commands, tasks

from utils.decorators import require_admin_password
from utils.helpers import load_json, save_json
from utils.nitrado import restart_server
from utils.ftp_helpers import connect_ftp
from repositories.player_repository import PlayerRepository
from repositories.item_repository import ItemRepository
from security import backup_manager, security_logger
import spawn_system
import gameplay_editor


CONFIG_FILE = "config.json"
PLAYERS_DB_FILE = "players_db.json"
FOOTER_ICON = os.getenv("FOOTER_ICON")


class Admin(commands.Cog):
    """Administrative commands for server management and gameplay configuration."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the Admin cog."""
        self.bot = bot
        self.item_repo = ItemRepository()
        self.player_repo = PlayerRepository()
        self.backup_loop.start()

    async def cog_unload(self):
        """Cleanup when cog is unloaded."""
        self.backup_loop.cancel()

    @tasks.loop(hours=1)
    async def backup_loop(self):
        """Cria backup automático dos arquivos críticos a cada hora"""
        critical_files = [
            # JSONs depreciados removidos, backups agora focam no DB e Configs
            "bigode_unified.db",
            CONFIG_FILE,
            "bot_state.json",
        ]

        print("[BACKUP] Iniciando backup automático...")
        backup_manager.backup_all(critical_files)
        print(f"[BACKUP] Backup concluído em {datetime.now().strftime('%H:%M:%S')}")

    @commands.command(name="set_killfeed")
    @require_admin_password()
    async def set_killfeed(self, ctx):
        """Define o canal atual como canal de Killfeed."""
        config = load_json(CONFIG_FILE)
        config["killfeed_channel"] = ctx.channel.id
        save_json(CONFIG_FILE, config)
        await ctx.send(f"✅ Canal de Killfeed definido para: {ctx.channel.mention}")

    @commands.command(name="restart")
    @require_admin_password()
    async def restart(self, ctx):
        """(Admin) Reinicia o servidor DayZ imediatamente."""
        await ctx.send("⏳ **Enviando comando de restart para a Nitrado...**")
        success, msg = await restart_server()
        if success:
            await ctx.send("✅ **Servidor reiniciando!** Aguarde alguns minutos para voltar.")
        else:
            await ctx.send(f"❌ **Falha ao reiniciar:** {msg}")

    @commands.command(name="clear", aliases=["limpar"])
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int = 10):
        """Limpa as últimas X mensagens do chat."""
        await ctx.channel.purge(limit=amount + 1)
        msg = await ctx.send(f"🧹 Limpei {amount} mensagens!")
        await asyncio.sleep(3)
        await msg.delete()

    @commands.command(name="desvincular")
    @require_admin_password()
    async def desvincular(self, ctx, gamertag: str):
        """(Admin) Remove vinculação de uma gamertag."""
        if self.player_repo.remove_gamertag(gamertag):
            # Tenta remover do legado por segurança se ainda existir
            try:
                links = load_json("links.json")
                if gamertag in links:
                    del links[gamertag]
                    save_json("links.json", links)
            except (FileNotFoundError, KeyError, ValueError):
                pass  # Legacy file cleanup, safe to ignore
            await ctx.send(f"✅ Gamertag **{gamertag}** desvinculada com sucesso!")
        else:
            await ctx.send(f"❌ Gamertag **{gamertag}** não encontrada ou erro no banco.")

    # --- COMANDOS DE SPAWN ---

    @commands.command(name="spawn")
    @require_admin_password()
    async def spawn(self, ctx, item_name: str, quantidade: int, *, gamertag: str):
        """Spawna item próximo a um jogador (última posição conhecida)"""
        if quantidade < 1 or quantidade > 10:
            await ctx.send("❌ Quantidade deve ser entre 1 e 10!")
            return

        item = self.item_repo.get_item_by_key(item_name.lower())
        if not item:
            await ctx.send(f"❌ Item `{item_name}` não encontrado!")
            return

        item_classname = item["name"]
        default_x, default_z = 7500, 7500

        spawn_id = spawn_system.add_to_spawn_queue(
            item_name=item_classname,
            x=default_x,
            z=default_z,
            quantity=quantidade,
            requested_by=ctx.author.id,
            gamertag=gamertag,
        )

        embed = discord.Embed(title="📦 SPAWN ADICIONADO À FILA", color=discord.Color.green())
        embed.add_field(name="🎯 Item", value=f"`{item_classname}` x{quantidade}", inline=True)
        embed.add_field(name="🎮 Jogador", value=gamertag, inline=True)
        embed.add_field(name="🆔 ID do Spawn", value=f"`{spawn_id}`", inline=True)
        embed.set_footer(text="BigodeTexas • Admin Spawner", icon_url=self.bot.footer_icon)
        await ctx.send(embed=embed)

        security_logger.log_admin_action(ctx.author.id, f"spawn {item_classname} para {gamertag}")

    @commands.command(name="spawn_coords")
    @require_admin_password()
    async def spawn_coords(self, ctx, item_name: str, quantidade: int, x: float, z: float):
        """Spawna item em coordenadas específicas"""
        if quantidade < 1 or quantidade > 10:
            await ctx.send("❌ Quantidade deve ser entre 1 e 10!")
            return

        item = self.item_repo.get_item_by_key(item_name.lower())
        if not item:
            await ctx.send(f"❌ Item `{item_name}` não encontrado!")
            return

        spawn_id = spawn_system.add_to_spawn_queue(
            item_name=item["name"],
            x=x,
            z=z,
            quantity=quantidade,
            requested_by=ctx.author.id,
        )

        embed = discord.Embed(title="📦 SPAWN ADICIONADO À FILA", color=discord.Color.green())
        embed.add_field(name="🎯 Item", value=f"`{item['name']}` x{quantidade}", inline=True)
        embed.add_field(name="📍 Coords", value=f"({x}, {z})", inline=True)
        embed.add_field(name="🆔 ID do Spawn", value=f"`{spawn_id}`", inline=True)
        embed.set_footer(text="BigodeTexas • Admin Spawner", icon_url=self.bot.footer_icon)
        await ctx.send(embed=embed)

    @commands.command(name="spawn_list")
    async def spawn_list(self, ctx):
        """Lista todos os spawns pendentes"""
        pending = spawn_system.get_pending_spawns()
        if not pending:
            await ctx.send("✅ Nenhum spawn pendente na fila!")
            return

        embed = discord.Embed(title="📋 FILA DE SPAWNS PENDENTES", color=discord.Color.blue())
        for s in pending[:10]:
            embed.add_field(
                name=f"🆔 {s['id']}",
                value=f"🎯 `{s['item']}` x{s['quantity']} @ ({s['x']:.0f}, {s['z']:.0f})",
                inline=False,
            )
        await ctx.send(embed=embed)

    @commands.command(name="process_spawns")
    @require_admin_password()
    async def process_spawns(self, ctx):
        """Processa todos os spawns pendentes (era XMLs e faz upload)"""
        pending = spawn_system.get_pending_spawns()
        if not pending:
            await ctx.send("✅ Nenhum spawn pendente para processar!")
            return

        await ctx.send(f"⏳ Processando {len(pending)} spawn(s)...")

        events_xml = "events_custom.xml"
        positions_xml = "cfgeventspawns_custom.xml"
        success_count = 0

        try:
            for sp_item in pending:
                success, _ = spawn_system.create_complete_spawn(
                    events_xml,
                    positions_xml,
                    sp_item["item"],
                    sp_item["x"],
                    sp_item["z"],
                    sp_item["quantity"],
                )
                if success:
                    spawn_system.mark_spawn_processed(sp_item["id"])
                    success_count += 1

            if success_count > 0:
                ftp = connect_ftp()
                if ftp:
                    with open(events_xml, "rb") as f:
                        ftp.storbinary(
                            "STOR /dayzxb_missions/dayzOffline.chernarusplus/db/events.xml",
                            f,
                        )
                    with open(positions_xml, "rb") as f:
                        ftp.storbinary(
                            "STOR /dayzxb_missions/dayzOffline.chernarusplus/db/cfgeventspawns.xml",
                            f,
                        )
                    ftp.quit()
                    await ctx.send(
                        f"✅ **{success_count}** spawns processados e enviados! Reinicie o servidor."
                    )
                else:
                    await ctx.send("❌ Erro ao conectar no FTP!")
        except (IOError, OSError) as e:
            await ctx.send(f"❌ Erro ao processar spawns: {e}")

    # --- COMANDOS DE GAMEPLAY ---

    @commands.group(name="gameplay", invoke_without_command=True)
    @require_admin_password()
    async def gameplay(self, ctx):
        """Sistema de Editor de Gameplay"""
        await ctx.send("⚙️ Use `!gameplay ajuda` para ver os comandos.")

    @gameplay.command(name="status")
    async def gameplay_status(self, ctx):
        """Mostra resumo das configurações atuais"""
        config = gameplay_editor.load_gameplay_config()
        embed = discord.Embed(title="⚙️ Configurações de Gameplay", color=discord.Color.blue())
        # Resumo simplificado
        gen = config.get("GeneralData", {})
        embed.add_field(
            name="Base Damage",
            value="Desabilitado" if gen.get("disableBaseDamage") else "Habilitado",
        )
        embed.add_field(
            name="Stamina",
            value="Desabilitada"
            if config.get("StaminaData", {}).get("disableStamina")
            else "Habilitada",
        )
        await ctx.send(embed=embed)

    @gameplay.command(name="ajuda")
    async def gameplay_ajuda(self, ctx):
        """Ajuda do editor de gameplay"""
        msg = (
            "⚙️ **COMANDOS GAMEPLAY**\n"
            "`!gameplay status` - Ver resumo\n"
            "`!gameplay set <param> <valor>` - Alterar valor\n"
            "`!gameplay restore` - Restaurar último backup"
        )
        await ctx.send(msg)


async def setup(bot):
    await bot.add_cog(Admin(bot))
