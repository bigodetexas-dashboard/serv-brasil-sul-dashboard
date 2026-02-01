import discord
from discord.ext import commands
import subprocess
import os
from datetime import datetime
import math
from utils.helpers import load_json, save_json
import database


class PVP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.alarms_file = "alarms.json"
        self.bounties_file = "bounties.json"
        self.footer_icon = (
            self.bot.footer_icon if hasattr(self.bot, "footer_icon") else None
        )

    @commands.command(name="heatmap")
    async def heatmap(self, ctx):
        """Gera o mapa de calor de mortes recentes."""
        await ctx.send("🛰️ **Gerando satélite...** Aguarde.")

        def run_script():
            try:
                result = subprocess.run(
                    ["python", "generate_heatmap.py"], capture_output=True, text=True
                )
                return result.returncode == 0, result.stdout + result.stderr
            except Exception as e:
                return False, str(e)

        success, output = await self.bot.loop.run_in_executor(None, run_script)

        if success and os.path.exists("heatmap.png"):
            file = discord.File("heatmap.png", filename="heatmap.png")
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

        alarms = load_json(self.alarms_file)
        alarm_id = f"{ctx.author.id}_{nome}"

        alarms[alarm_id] = {
            "owner_id": str(ctx.author.id),
            "name": nome,
            "x": x,
            "z": z,
            "radius": raio,
            "telegram_id": telegram_id,
            "is_group": is_group,
            "created_at": datetime.now().isoformat(),
        }

        save_json(self.alarms_file, alarms)

        msg = f"✅ **Alarme '{nome}' configurado!**\n📍 Coords: {x}, {z}\n📏 Raio: {raio}m\n📱 Telegram ID: `{telegram_id}`"
        if is_group:
            msg += " (Grupo)"

        await ctx.send(msg)


async def setup(bot):
    await bot.add_cog(PVP(bot))
