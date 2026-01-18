"""
Tools Cog

Provides utility commands for base alarms and bounty system.
Includes commands for setting up base protection and placing bounties on players.
"""

import math

import discord
from discord.ext import commands

from repositories.bounty_repository import BountyRepository
from repositories.clan_repository import ClanRepository
from repositories.player_repository import PlayerRepository


class Tools(commands.Cog):
    """
    Utility commands cog for base alarms and bounties.

    Provides:
    - Base alarm system for territory protection
    - Bounty system for placing rewards on players
    """

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the Tools cog."""
        self.bot = bot
        self.clan_repo = ClanRepository()
        self.player_repo = PlayerRepository()
        self.bounty_repo = BountyRepository()

    @commands.group(invoke_without_command=True)
    async def alarme(self, ctx: commands.Context) -> None:
        """
        Base alarm system main command.

        Shows help message if no subcommand is provided.
        Use subcommands: set, lista
        """
        await ctx.send(
            "🚨 **Sistema de Alarmes**\nUse `!alarme set <nome> <X> <Z> <raio>` para proteger sua base."
        )

    @alarme.command()
    async def set(self, ctx: commands.Context, nome: str, x: float, z: float, raio: int) -> None:
        """
        Set up a base alarm at specified coordinates.

        Args:
            nome: Name for the base
            x: X coordinate
            z: Z coordinate
            raio: Protection radius (max 500m)

        Cost: 10,000 DZ Coins
        Limit: 1 base per player

        Example:
            !alarme set BasePrincipal 4500 10200 100
        """
        if raio > 500:
            await ctx.send("❌ Raio máximo permitido: 500 metros.")
            return

        cost = 10000
        bal = self.player_repo.get_balance(ctx.author.id)
        if bal < cost:
            await ctx.send(f"❌ Custa {cost} DZ Coins para instalar um sistema de segurança.")
            return

        # Busca bases existentes no DB
        bases = self.player_repo.get_all_bases()

        # Verifica limite (1 base por user)
        for b in bases:
            if b["owner_id"] == str(ctx.author.id):
                await ctx.send("❌ **Limite Atingido!**\nVocê já possui uma base registrada.")
                return

        user_clan_data = self.clan_repo.get_user_clan(ctx.author.id)
        user_clan_id = user_clan_data["id"] if user_clan_data else None

        for b in bases:
            dist = math.sqrt((x - b["x"]) ** 2 + (z - b["z"]) ** 2)
            if dist < (raio + b["radius"]):
                owner_clan_data = self.clan_repo.get_user_clan(b["owner_id"])
                owner_clan_id = owner_clan_data["id"] if owner_clan_data else None

                if b["owner_id"] != str(ctx.author.id):
                    if user_clan_id is None or owner_clan_id != user_clan_id:
                        await ctx.send(
                            "❌ **Acesso Negado!**\nEsta área já é monitorada por outro clã."
                        )
                        return

        # Processa Pagamento
        self.player_repo.update_balance(ctx.author.id, -cost, "purchase")

        # Salva no DB
        # TODO: Add add_base to PlayerRepository if not there
        conn = self.player_repo.get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO bases (owner_id, name, x, z, radius) VALUES (?, ?, ?, ?, ?)",
            (str(ctx.author.id), nome, x, z, raio),
        )
        conn.commit()
        conn.close()

        await ctx.send(f"🚨 **Alarme Instalado!**\nBase: {nome} em {x}, {z}")

    @alarme.command()
    async def lista(self, ctx: commands.Context) -> None:
        """
        List all your active base alarms.

        Shows name, coordinates, and protection radius for each alarm.
        """
        bases = self.player_repo.get_all_bases()
        msg = "🚨 **Seus Alarmes Ativos**\n"
        count = 0
        for b in bases:
            if b["owner_id"] == str(ctx.author.id):
                msg += f"📡 **{b['name']}**: {b['x']}x {b['z']}z ({b['radius']}m)\n"
                count += 1
        if count == 0:
            msg += "Nenhum alarme."
        await ctx.send(msg)

    @commands.command(name="procurado")
    async def procurado(self, ctx: commands.Context, gamertag: str, valor: int) -> None:
        """
        Place a bounty on a player's head.

        Args:
            gamertag: Target player's gamertag
            valor: Bounty amount (minimum 1000 DZ Coins)

        The bounty is added to any existing bounty on the player.
        Costs are deducted from your balance immediately.

        Example:
            !procurado BadPlayer 5000
        """
        if valor < 1000:
            await ctx.send("❌ Valor mínimo: 1000 DZ Coins.")
            return

        bal = self.player_repo.get_balance(ctx.author.id)
        if bal < valor:
            await ctx.send("❌ Saldo insuficiente.")
            return

        self.player_repo.update_balance(ctx.author.id, -valor, "purchase")

        self.bounty_repo.add_or_update_bounty(gamertag, valor, ctx.author.id)
        current_bounty = self.bounty_repo.get_bounty(gamertag)

        embed = discord.Embed(
            title="🤠 PROCURADO!",
            description=f"Recompensa por **{gamertag}**!",
            color=discord.Color.orange(),
        )
        embed.add_field(name="💰 Valor", value=f"{current_bounty['amount']} DZ Coins")
        embed.set_image(url="https://i.imgur.com/S71j4qO.png")  # Imagem de Wanted
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Load the Tools cog."""
    await bot.add_cog(Tools(bot))
