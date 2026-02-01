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
        self.footer_icon = self.bot.footer_icon if hasattr(self.bot, 'footer_icon') else None

    @commands.command(name="heatmap")
    async def heatmap(self, ctx):
        """Gera o mapa de calor de mortes recentes."""
        await ctx.send("🛰️ **Gerando satélite...** Aguarde.")
        
        def run_script():
            try:
                result = subprocess.run(["python", "generate_heatmap.py"], capture_output=True, text=True)
                return result.returncode == 0, result.stdout + result.stderr
            except Exception as e:
                return False, str(e)

        success, output = await self.bot.loop.run_in_executor(None, run_script)

        if success and os.path.exists("heatmap.png"):
            file = discord.File("heatmap.png", filename="heatmap.png")
            embed = discord.Embed(title="🔥 BigodeTexas - PvP Heatmap", color=discord.Color.dark_orange())
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

        database.update_balance(ctx.author.id, -valor, "bounty", f"Recompensa por {gamertag}")
        await ctx.send(f"🤠 **PROCURADO!** Recompensa de **{valor} DZ Coins** por **{gamertag}**!")

async def setup(bot):
    await bot.add_cog(PVP(bot))
