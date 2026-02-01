import discord
from discord.ext import commands
from utils.helpers import load_json, calculate_kd, calculate_level


class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players_db_file = "players_db.json"
        self.economy_file = "economy.json"
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
        players_db = load_json(self.players_db_file)
        economy = load_json(self.economy_file)

        if not players_db and categoria != "coins":
            await ctx.send("❌ Ainda não há dados suficientes!")
            return

        if categoria == "kills":
            await self.show_kills(ctx, players_db)
        elif categoria == "kd":
            await self.show_kd(ctx, players_db)
        elif categoria == "coins":
            await self.show_coins(ctx, economy)
        else:
            await ctx.send("❌ Categoria inválida ou ainda não migrada!")

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
