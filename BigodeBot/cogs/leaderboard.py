"""
Leaderboard Cog

Provides ranking and leaderboard commands for various player statistics.
Includes kills, K/D ratio, killstreaks, coins, playtime, and PvP heatmap generation.
"""

import os

import discord
from discord.ext import commands

from repositories.player_repository import PlayerRepository
from utils.helpers import calculate_kd


class Leaderboard(commands.Cog):
    """
    Leaderboard and ranking system.

    Provides commands to view top players in various categories:
    - Kills, K/D ratio, killstreaks
    - Coins/balance, playtime
    - PvP heatmap visualization
    """

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the Leaderboard cog."""
        self.bot = bot
        self.repo = PlayerRepository()
        # Footer icon is attached to the bot instance
        self.footer_icon = getattr(bot, "footer_icon", None)

    def calculate_level(self, kills: int) -> int:
        """Calculate player level based on kills (1 level per 10 kills)."""
        return int(kills // 10) + 1

    @commands.command(name="top", aliases=["ranking", "leaderboard"])
    async def top(self, ctx: commands.Context, categoria: str | None = None) -> None:
        """
        Display leaderboards for various player statistics.

        Args:
            categoria: Category to display (kills/kd/streak/coins/playtime)
                      If not provided, shows available categories

        Examples:
            !top kills - Top killers
            !top kd - Best K/D ratio
            !top streak - Highest killstreaks
            !top coins - Richest players
            !top playtime - Most playtime
        """
        if not categoria:
            embed = discord.Embed(
                title="🏆 LEADERBOARD - BIGODE TEXAS",
                description="Escolha uma categoria para ver o ranking:",
                color=discord.Color.gold(),
            )
            embed.add_field(
                name="📊 Categorias Disponíveis",
                value=(
                    "🔫 `!top kills` - Top Matadores\n"
                    "🎯 `!top kd` - Melhor K/D Ratio\n"
                    "🔥 `!top streak` - Maior Killstreak\n"
                    "💰 `!top coins` - Mais Rico\n"
                    "⏰ `!top playtime` - Mais Tempo Jogado"
                ),
                inline=False,
            )
            embed.set_footer(text="BigodeTexas • Sistema de Rankings", icon_url=self.footer_icon)
            await ctx.send(embed=embed)
            return

        categoria = categoria.lower()

        if categoria == "kills":
            await self.show_kills(ctx)
        elif categoria == "kd":
            await self.show_kd(ctx)
        elif categoria == "streak":
            await self.show_streak(ctx)
        elif categoria == "coins":
            await self.show_coins(ctx)
        elif categoria == "playtime":
            await self.show_playtime(ctx)
        else:
            await ctx.send("❌ Categoria inválida! Use `!top` para ver as opções.")

    async def show_kills(self, ctx):
        top_players = self.repo.get_top_kills(10)

        if not top_players:
            await ctx.send("❌ Nenhum dado de kills encontrado.")
            return

        embed = discord.Embed(title="🔫 TOP 10 MATADORES", color=discord.Color.red())
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

        for idx, p in enumerate(top_players):
            player_name = p["nitrado_gamertag"] or "Desconhecido"
            kills = p["kills"]
            kd = calculate_kd(kills, p["deaths"])
            lvl = self.calculate_level(kills)
            embed.add_field(
                name=f"{medals[idx]} {player_name}",
                value=f"💀 Kills: **{kills}** | 🎯 K/D: **{kd}** | ⭐ Nivel: **{lvl}**",
                inline=False,
            )
        embed.set_footer(text="BigodeTexas • Atualizado em tempo real", icon_url=self.footer_icon)
        await ctx.send(embed=embed)

    async def show_kd(self, ctx):
        top_players = self.repo.get_top_kd(10, min_kills=5)

        if not top_players:
            await ctx.send("❌ Mínimo 5 kills para aparecer no ranking de K/D.")
            return

        embed = discord.Embed(title="🎯 TOP 10 K/D RATIO", color=discord.Color.blue())
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

        for idx, p in enumerate(top_players):
            player_name = p["nitrado_gamertag"] or "Desconhecido"
            kd = round(p["kd"], 2)
            embed.add_field(
                name=f"{medals[idx]} {player_name}",
                value=f"🎯 K/D: **{kd}** | 💀 Kills: **{p['kills']}**",
                inline=False,
            )
        embed.set_footer(text="BigodeTexas • Atualizado em tempo real", icon_url=self.footer_icon)
        await ctx.send(embed=embed)

    async def show_streak(self, ctx):
        top_players = self.repo.get_top_streak(10)

        if not top_players:
            await ctx.send("❌ Nenhum recorde de killstreak encontrado.")
            return

        embed = discord.Embed(title="🔥 TOP 10 KILLSTREAKS", color=discord.Color.orange())
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

        for idx, p in enumerate(top_players):
            player_name = p["nitrado_gamertag"] or "Desconhecido"
            best = p["best_killstreak"]
            if best == 0:
                break
            embed.add_field(
                name=f"{medals[idx]} {player_name}",
                value=f"🏆 Melhor: **{best}** kills",
                inline=False,
            )
        embed.set_footer(text="BigodeTexas • Atualizado em tempo real", icon_url=self.footer_icon)
        await ctx.send(embed=embed)

    async def show_coins(self, ctx):
        top_players = self.repo.get_top_balances(10)

        if not top_players:
            await ctx.send("❌ Nenhum dado de economia encontrado.")
            return

        embed = discord.Embed(title="💰 TOP 10 MAIS RICOS", color=discord.Color.gold())
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

        for idx, p in enumerate(top_players):
            # Tenta pegar username do discord se possível, senão gamertag
            player_name = p["nitrado_gamertag"] or f"Discord ID: {p['discord_id']}"
            balance = p["balance"]
            embed.add_field(
                name=f"{medals[idx]} {player_name}",
                value=f"💰 **{balance:,}** DZ Coins",
                inline=False,
            )
        embed.set_footer(text="BigodeTexas • Sistema Bancário", icon_url=self.footer_icon)
        await ctx.send(embed=embed)

    async def show_playtime(self, ctx):
        top_players = self.repo.get_top_playtime(10)

        if not top_players:
            await ctx.send("❌ Nenhum dado de tempo de jogo encontrado.")
            return

        embed = discord.Embed(title="⏰ TOP 10 TEMPO JOGADO", color=discord.Color.purple())
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

        for idx, p in enumerate(top_players):
            player_name = p["nitrado_gamertag"] or "Desconhecido"
            pt = p["total_playtime"]
            if pt == 0:
                break
            h, m = int(pt // 3600), int((pt % 3600) // 60)
            embed.add_field(
                name=f"{medals[idx]} {player_name}",
                value=f"⏰ **{h}h {m}m** jogadas",
                inline=False,
            )
        embed.set_footer(text="BigodeTexas • Atualizado em tempo real", icon_url=self.footer_icon)
        await ctx.send(embed=embed)

    @commands.command(name="heatmap", aliases=["mapa_calor", "pontoquente"])
    async def heatmap(self, ctx: commands.Context) -> None:
        """
        Generate a PvP heatmap showing recent kill locations.

        Creates a visual heatmap overlay on the DayZ map showing
        where most PvP encounters occur. Generation may take a few seconds.

        The heatmap is generated from recent PvP kill coordinates.
        """
        await ctx.send("⏳ Gerando mapa de calor pvp... isso pode levar alguns segundos.")

        def run_script():
            import subprocess
            import os

            try:
                result = subprocess.run(
                    ["python", "generate_heatmap.py"],
                    capture_output=True,
                    text=True,
                    cwd=os.getcwd(),
                    check=False,
                )
                return result.returncode == 0, result.stdout + result.stderr
            except Exception as e:
                return False, str(e)

        success, output = await self.bot.loop.run_in_executor(None, run_script)

        if success and os.path.exists("heatmap.png"):
            from datetime import datetime

            file = discord.File("heatmap.png", filename="heatmap.png")
            embed = discord.Embed(
                title="🔥 BigodeTexas - PvP Heatmap", color=discord.Color.dark_orange()
            )
            embed.set_image(url="attachment://heatmap.png")
            embed.set_footer(
                text=f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                icon_url=self.footer_icon,
            )
            await ctx.send(embed=embed, file=file)
        else:
            await ctx.send(f"❌ **Erro ao gerar heatmap:**\n```{output[:1000]}```")


async def setup(bot: commands.Bot) -> None:
    """Load the Leaderboard cog."""
    await bot.add_cog(Leaderboard(bot))
