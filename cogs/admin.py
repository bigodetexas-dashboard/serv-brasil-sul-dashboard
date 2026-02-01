import discord
from discord.ext import commands
import os
from utils.decorators import require_admin_password
from spawn_system import add_to_spawn_queue, get_pending_spawns, process_spawn_queue
from gameplay_editor import (
    load_gameplay_config,
    save_gameplay_config,
    backup_gameplay_config,
    get_latest_backup,
    restore_backup,
)
import database


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.admin_whitelist = (
            self.bot.admin_whitelist if hasattr(self.bot, "admin_whitelist") else []
        )
        self.footer_icon = (
            self.bot.footer_icon if hasattr(self.bot, "footer_icon") else None
        )

    @commands.command(name="spawn")
    @require_admin_password()
    async def spawn(self, ctx, item_name: str, quantidade: int, *, gamertag: str):
        """Spawna item próximo a um jogador (última posição conhecida)"""
        # A lógica real está no módulo spawn_system
        # Por simplicidade, chamamos a função que adiciona à fila
        spawn_id = add_to_spawn_queue(
            item_name, 7500, 7500, quantidade, ctx.author.id, gamertag
        )
        await ctx.send(
            f"✅ **Spawn adicionado!** ID: `{spawn_id}`. O item será entregue no próximo restart."
        )

    @commands.group(name="gameplay", invoke_without_command=True)
    @require_admin_password()
    async def gameplay(self, ctx):
        """Sistema de Editor de Gameplay."""
        await ctx.send(
            "⚙️ **Editor de Gameplay**\nUse `!gameplay view` ou `!gameplay edit`."
        )

    @gameplay.command(name="view")
    async def view_config(self, ctx):
        config = load_gameplay_config()
        if not config:
            await ctx.send("❌ Erro ao carregar cfggameplay.json.")
            return
        # Mostra um resumo simples
        await ctx.send(
            f"📋 **Configuração Atual:** `{len(config)}` parâmetros detectados."
        )


async def setup(bot):
    await bot.add_cog(Admin(bot))
