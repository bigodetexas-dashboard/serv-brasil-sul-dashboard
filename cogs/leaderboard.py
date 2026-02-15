"""Cog de leaderboard com rankings de jogadores por diferentes categorias."""

import os
import sys

import discord
from discord.ext import commands

# Adicionar o diretório pai ao path para imports funcionarem
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database
from utils.helpers import calculate_kd


class Leaderboard(commands.Cog):
    """Sistema de rankings e leaderboards para jogadores."""

    def __init__(self, bot):
        self.bot = bot
        self.footer_icon = (
            self.bot.footer_icon if hasattr(self.bot, "footer_icon") else None
        )

    @commands.command(name="top")
    async def top(self, ctx, categoria: str = None):
        """Sistema de Leaderboard - Rankings de jogadores"""
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
            embed.set_footer(
                text="BigodeTexas • Sistema de Rankings", icon_url=self.footer_icon
            )
            await ctx.send(embed=embed)
            return

        categoria = categoria.lower()
        players_db = database.get_all_players()
        economy = database.get_all_economy()

        if not players_db and categoria != "coins":
            await ctx.send("❌ Ainda não há dados suficientes!")
            return

        if categoria == "kills":
            await self.show_kills(ctx, players_db)
        elif categoria == "kd":
            await self.show_kd(ctx, players_db)
        elif categoria == "streak":
            await self.show_streak(ctx, players_db)
        elif categoria == "playtime":
            await self.show_playtime(ctx, players_db)
        elif categoria == "coins":
            await self.show_coins(ctx, economy)
        else:
            await ctx.send(
                "❌ Categoria invalida! Use: `kills`, `kd`, `streak`, `coins`, `playtime`."
            )

    async def show_kills(self, ctx, players_db):
        sorted_players = sorted(
            players_db.items(),
            key=lambda x: x[1].get("kills", 0),
            reverse=True,
        )[:10]

        embed = discord.Embed(title="🔫 TOP 10 MATADORES", color=discord.Color.red())
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        for idx, (player, stats) in enumerate(sorted_players):
            kills = stats.get("kills", 0)
            kd = calculate_kd(kills, stats.get("deaths", 0))
            embed.add_field(
                name=f"{medals[idx]} {player}",
                value=f"💀 Kills: **{kills}** | 🎯 K/D: **{kd}**",
                inline=False,
            )
        await ctx.send(embed=embed)

    async def show_kd(self, ctx, players_db):
        # Filtra jogadores com pelo menos 5 kills para evitar K/D inflado
        eligible = {p: s for p, s in players_db.items() if s.get("kills", 0) >= 5}
        if not eligible:
            await ctx.send(
                "❌ Nenhum jogador com kills suficientes para ranking de K/D."
            )
            return

        sorted_players = sorted(
            eligible.items(),
            key=lambda x: (x[1].get("kills", 0) / max(x[1].get("deaths", 1), 1)),
            reverse=True,
        )[:10]

        embed = discord.Embed(title="🎯 TOP 10 K/D RATIO", color=discord.Color.purple())
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        for idx, (player, stats) in enumerate(sorted_players):
            kills = stats.get("kills", 0)
            deaths = stats.get("deaths", 0)
            kd = calculate_kd(kills, deaths)
            embed.add_field(
                name=f"{medals[idx]} {player}",
                value=f"🎯 K/D: **{kd}** | 💀 {kills}K / {deaths}D",
                inline=False,
            )
        embed.set_footer(text="Minimo 5 kills para aparecer", icon_url=self.footer_icon)
        await ctx.send(embed=embed)

    async def show_streak(self, ctx, players_db):
        sorted_players = sorted(
            players_db.items(),
            key=lambda x: x[1].get("best_killstreak", 0),
            reverse=True,
        )[:10]

        if not sorted_players or sorted_players[0][1].get("best_killstreak", 0) == 0:
            await ctx.send("❌ Nenhum jogador com killstreak registrada.")
            return

        embed = discord.Embed(
            title="🔥 TOP 10 KILLSTREAK", color=discord.Color.dark_orange()
        )
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        for idx, (player, stats) in enumerate(sorted_players):
            streak = stats.get("best_killstreak", 0)
            if streak == 0:
                break
            embed.add_field(
                name=f"{medals[idx]} {player}",
                value=f"🔥 Streak: **{streak} kills seguidas**",
                inline=False,
            )
        await ctx.send(embed=embed)

    async def show_playtime(self, ctx, players_db):
        sorted_players = sorted(
            players_db.items(),
            key=lambda x: x[1].get("total_playtime", 0),
            reverse=True,
        )[:10]

        if not sorted_players or sorted_players[0][1].get("total_playtime", 0) == 0:
            await ctx.send("❌ Nenhum jogador com tempo de jogo registrado.")
            return

        embed = discord.Embed(
            title="⏰ TOP 10 TEMPO JOGADO", color=discord.Color.green()
        )
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        for idx, (player, stats) in enumerate(sorted_players):
            seconds = stats.get("total_playtime", 0)
            if seconds == 0:
                break
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            embed.add_field(
                name=f"{medals[idx]} {player}",
                value=f"⏰ **{hours}h {minutes}m** jogados",
                inline=False,
            )
        await ctx.send(embed=embed)

    async def show_coins(self, ctx, economy):
        sorted_players = sorted(
            economy.items(),
            key=lambda x: x[1].get("balance", 0),
            reverse=True,
        )[:10]

        embed = discord.Embed(title="💰 TOP 10 MAIS RICOS", color=discord.Color.gold())
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        for idx, (uid, data) in enumerate(sorted_players):
            bal = data.get("balance", 0)
            gt = data.get("gamertag", "???")
            embed.add_field(
                name=f"{medals[idx]} {gt}",
                value=f"💵 **{bal:,} DZ Coins**",
                inline=False,
            )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
