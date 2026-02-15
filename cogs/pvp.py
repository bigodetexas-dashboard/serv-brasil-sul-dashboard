"""Cog de PVP com heatmap, recompensas e sistema de alarmes de base."""

import asyncio
import os
import subprocess
import sys
from datetime import datetime

import discord
from discord.ext import commands

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database
from utils.n8n_dispatcher import send_n8n_base_alert


class PVP(commands.Cog):
    """Comandos de PVP, heatmap de mortes, recompensas e alarmes de base."""

    def __init__(self, bot):
        self.bot = bot
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.footer_icon = (
            self.bot.footer_icon if hasattr(self.bot, "footer_icon") else None
        )

    @commands.command(name="heatmap")
    async def heatmap(self, ctx):
        """Gera o mapa de calor de mortes recentes."""
        await ctx.send("🛰️ **Gerando satélite...** Aguarde.")

        script_path = os.path.join(self.base_dir, "generate_heatmap.py")
        heatmap_path = os.path.join(self.base_dir, "heatmap.png")

        def run_script():
            try:
                result = subprocess.run(
                    ["python", script_path],
                    capture_output=True,
                    text=True,
                    cwd=self.base_dir,
                    check=True,
                )
                return result.returncode == 0, result.stdout + result.stderr
            except Exception as e:
                return False, str(e)

        success, output = await asyncio.to_thread(run_script)

        if success and os.path.exists(heatmap_path):
            file = discord.File(heatmap_path, filename="heatmap.png")
            embed = discord.Embed(
                title="🔥 BigodeTexas - PvP Heatmap", color=discord.Color.dark_orange()
            )
            embed.set_image(url="attachment://heatmap.png")
            await ctx.send(embed=embed, file=file)
        else:
            await ctx.send(f"❌ Erro ao gerar heatmap: {output[:500]}")

    @commands.command(name="procurado")
    async def procurado(self, ctx, gamertag: str, valor: int):
        """Adiciona uma recompensa por um jogador."""
        if valor < 1000:
            await ctx.send("❌ Valor mínimo: 1000 DZ Coins.")
            return

        bal = database.get_balance(ctx.author.id)
        if bal < valor:
            await ctx.send("❌ Saldo insuficiente.")
            return

        database.update_balance(
            ctx.author.id, -valor, "bounty", f"Recompensa por {gamertag}"
        )
        database.save_bounty(gamertag, valor, ctx.author.id)

        await ctx.send(
            f"🤠 **PROCURADO!** Recompensa de **{valor} DZ Coins** por **{gamertag}**!"
        )

    @commands.group(name="alarme", invoke_without_command=True)
    async def alarme(self, ctx):
        """Sistema de Alarme de Base via Telegram/Discord."""
        embed = discord.Embed(
            title="🚨 Sistema de Alarme de Base",
            description="Proteja seu território com alertas em tempo real!",
            color=discord.Color.red(),
        )
        embed.add_field(
            name="📌 Como configurar:",
            value="`!alarme set <nome> <x> <z> <raio> <telegram_id> [is_group: true/false]`",
            inline=False,
        )
        embed.add_field(
            name="📍 Exemplo:",
            value="`!alarme set MinhaBase 4500 10200 300 123456789 false`",
            inline=False,
        )
        embed.set_footer(text="BigodeTexas Security", icon_url=self.footer_icon)
        await ctx.send(embed=embed)

    @alarme.command(name="set")
    async def set_alarme(
        self,
        ctx,
        nome: str,
        x: float,
        z: float,
        raio: int,
        telegram_id: str,
        is_group: bool = False,
    ):
        """Registra um novo alarme de base."""
        if raio < 50 or raio > 1000:
            await ctx.send("❌ O raio deve estar entre 50m e 1000m.")
            return

        alarm_key = f"{ctx.author.id}_{nome}"
        alarm_data = {
            "owner_id": str(ctx.author.id),
            "name": nome,
            "x": x,
            "z": z,
            "radius": raio,
            "telegram_id": telegram_id,
            "is_group": is_group,
            "created_at": datetime.now().isoformat(),
        }
        database.save_alarm(alarm_key, alarm_data)

        await send_n8n_base_alert(
            player_name=ctx.author.name,
            coords=f"{x:.0f}, {z:.0f}",
            base_name=nome,
            chat_id=telegram_id,
            is_group=is_group,
            event_type="Nova Base Registrada",
        )

        msg = f"✅ **Alarme '{nome}' configurado!**\n📍 Coords: {x}, {z}\n📏 Raio: {raio}m\n📱 Telegram ID: `{telegram_id}`"
        if is_group:
            msg += " (Grupo)"

        await ctx.send(msg)


async def setup(bot):
    """Função de setup para carregar o cog PVP."""
    await bot.add_cog(PVP(bot))
