"""
Clans Cog

Manages clan system including creation, membership, wars, and clan economy.
Provides commands for clan management, member invitations, and inter-clan warfare.
"""

import asyncio

import discord
from discord.ext import commands, tasks

from repositories.clan_repository import ClanRepository
from repositories.player_repository import PlayerRepository
from utils.decorators import rate_limit


class Clans(commands.Cog):
    """Clan management system with wars and economy."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the Clans cog."""
        self.bot = bot
        self.clan_repo = ClanRepository()
        self.player_repo = PlayerRepository()
        self.war_expiry_loop.start()

    def cog_unload(self):
        self.war_expiry_loop.cancel()

    @tasks.loop(minutes=30)
    async def war_expiry_loop(self):
        """Verifica e finaliza guerras expiradas."""
        conn = self.clan_repo.get_conn()
        if not conn:
            return
        try:
            cur = conn.cursor()
            # Select active wars that are past their expiry
            cur.execute("""
                SELECT * FROM clan_wars
                WHERE status = 'active' AND expires_at < datetime('now')
            """)
            expired_wars = cur.fetchall()

            for war in expired_wars:
                war_id = war["id"]
                c1_id = war["clan1_id"]
                c2_id = war["clan2_id"]
                p1 = war["clan1_points"]
                p2 = war["clan2_points"]

                # Update status
                cur.execute("UPDATE clan_wars SET status = 'finished' WHERE id = ?", (war_id,))

                # Find names for announcement (this is a bit heavy but ok for few ended wars)
                cur.execute("SELECT name FROM clans WHERE id = ?", (c1_id,))
                n1 = cur.fetchone()["name"]
                cur.execute("SELECT name FROM clans WHERE id = ?", (c2_id,))
                n2 = cur.fetchone()["name"]

                # Announcement
                try:
                    from utils.helpers import load_json

                    config = load_json("config.json")
                    channel_id = config.get("killfeed_channel")
                    if channel_id:
                        channel = self.bot.get_channel(int(channel_id))
                        if channel:
                            winner = n1 if p1 > p2 else n2 if p2 > p1 else "Empate"
                            color = (
                                discord.Color.gold()
                                if winner != "Empate"
                                else discord.Color.light_grey()
                            )

                            embed = discord.Embed(
                                title="🏁 FIM DA GUERRA!",
                                description=f"O conflito entre **{n1}** e **{n2}** chegou ao fim.",
                                color=color,
                            )
                            embed.add_field(name=n1, value=f"{p1} Pontos", inline=True)
                            embed.add_field(name=n2, value=f"{p2} Pontos", inline=True)

                            if winner != "Empate":
                                embed.add_field(
                                    name="🏆 Vencedor",
                                    value=f"**{winner}** com a glória da vitória!",
                                    inline=False,
                                )
                            else:
                                embed.add_field(
                                    name="⚖️ Resultado",
                                    value="Um empate sangrento! Ninguém venceu.",
                                    inline=False,
                                )

                            embed.set_footer(text="Guerra finalizada • BigodeTexas")
                            await channel.send(embed=embed)
                except Exception as ex:
                    print(f"[ERROR] War Announce: {ex}")

            conn.commit()
        except Exception as e:
            print(f"Erro no war_expiry_loop: {e}")
        finally:
            conn.close()

    @commands.command(name="clã", aliases=["clan", "meuclan"])
    async def clan_info(self, ctx, tag: str = None):
        """Mostra informações de um clã ou do seu próprio."""
        if tag:
            clan = self.clan_repo.get_clan_by_tag(tag)
        else:
            clan = self.clan_repo.get_user_clan(ctx.author.id)

        if not clan:
            await ctx.send("❌ Clã não encontrado ou você não pertence a um clã.")
            return

        embed = discord.Embed(title=f"🛡️ Clã: {clan['name']}", color=discord.Color.blue())
        if clan.get("banner_url"):
            embed.set_thumbnail(url=clan["banner_url"])

        leader = await self.bot.fetch_user(int(clan["leader_discord_id"]))
        embed.add_field(
            name="👑 Líder",
            value=leader.mention if leader else clan["leader_discord_id"],
            inline=True,
        )
        embed.add_field(name="💰 Saldo do Clã", value=f"{clan['balance']:,} DZ Coins", inline=True)

        # Members list
        members = clan.get("members", [])
        if members:
            m_list = []
            for m in members:
                m_list.append(f"<@{m['discord_id']}> ({m['role']})")
            embed.add_field(
                name=f"👥 Membros ({len(members)})",
                value="\n".join(m_list),
                inline=False,
            )
        else:
            embed.add_field(name="👥 Membros", value="Nenhum membro encontrado.", inline=False)

        embed.set_footer(text="BigodeTexas • Sistema de Clãs", icon_url=self.bot.footer_icon)
        await ctx.send(embed=embed)

    @commands.command(name="clãs", aliases=["clans", "ranking_clans"])
    async def list_clans(self, ctx):
        """Lista todos os clãs registrados."""
        clans = self.clan_repo.get_all_clans()
        if not clans:
            await ctx.send("📂 Nenhum clã registrado ainda.")
            return

        embed = discord.Embed(title="🏆 Ranking de Clãs (por Saldo)", color=discord.Color.gold())
        for i, clan in enumerate(clans[:10], 1):  # Top 10
            embed.add_field(
                name=f"{i}. {clan['name']}",
                value=f"💰 {clan['balance']:,} DZ Coins",
                inline=False,
            )

        embed.set_footer(text="BigodeTexas • Use !clã <tag> para detalhes")
        await ctx.send(embed=embed)

    @commands.command(name="criar_clã", aliases=["criarclan"])
    @rate_limit()
    async def create_clan(self, ctx, *, nome: str):
        """Cria um novo clã."""
        # 1. Verificar se já está em um clã
        existing = self.clan_repo.get_user_clan(ctx.author.id)
        if existing:
            await ctx.send(f"❌ Você já pertence ao clã **{existing['name']}**!")
            return

        # 2. Verificar se nome já existe
        if self.clan_repo.get_clan_by_tag(nome):
            await ctx.send(f"❌ Já existe um clã com o nome **{nome}**!")
            return

        # 3. Criar no Banco
        clan_id = self.clan_repo.create_clan(nome, ctx.author.id)
        if clan_id:
            await ctx.send(f"🎉 Clã **{nome}** criado com sucesso! Você é o líder.")
        else:
            await ctx.send("❌ Erro ao criar clã no banco de dados.")

    @commands.command(name="depositar_clã", aliases=["depclan"])
    async def deposit_clan(self, ctx, amount: int):
        """Deposita DZ Coins no banco do clã."""
        if amount <= 0:
            await ctx.send("❌ Valor inválido.")
            return

        clan = self.clan_repo.get_user_clan(ctx.author.id)
        if not clan:
            await ctx.send("❌ Você não pertence a um clã.")
            return

        user_bal = self.player_repo.get_balance(ctx.author.id)
        if user_bal < amount:
            await ctx.send("❌ Saldo insuficiente para o depósito.")
            return

        # 1. Deduz do jogador
        self.player_repo.update_balance(ctx.author.id, -amount, "clan_deposit")
        # 2. Adiciona ao clã
        self.clan_repo.update_balance(clan["id"], amount)

        await ctx.send(
            f"✅ Você depositou **{amount:,} DZ Coins** no banco do clã **{clan['name']}**!"
        )

    @commands.command(name="convidar_clã")
    async def invite_member(self, ctx, member: discord.Member):
        """Convida um jogador para o seu clã (Apenas Líder/Mod)."""
        clan = self.clan_repo.get_user_clan(ctx.author.id)
        if not clan:
            await ctx.send("❌ Você não pertence a um clã.")
            return
        if clan["role"] not in ["leader", "moderator"]:
            await ctx.send("❌ Apenas Líderes ou Moderadores podem convidar membros.")
            return

        target_clan = self.clan_repo.get_user_clan(member.id)
        if target_clan:
            await ctx.send(f"❌ {member.mention} já pertence ao clã **{target_clan['name']}**.")
            return

        # Simple invite flow (for now just direct add, ideally use wait_for for confirmation)
        await ctx.send(
            f"❓ {member.mention}, você foi convidado para o clã **{clan['name']}**. Digite `aceitar` para entrar ou `recusar`."
        )

        def check(m):
            return (
                m.author == member
                and m.channel == ctx.channel
                and m.content.lower() in ["aceitar", "recusar"]
            )

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=60.0)
            if msg.content.lower() == "aceitar":
                self.clan_repo.add_member(clan["id"], member.id)
                await ctx.send(f"✅ {member.mention} agora faz parte do clã **{clan['name']}**!")
            else:
                await ctx.send("🚫 Convite recusado.")
        except asyncio.TimeoutError:
            await ctx.send(f"⏰ Convite para {member.mention} expirou.")

    @commands.command(name="sair_clã")
    async def leave_clan(self, ctx):
        """Sai do seu clã atual."""
        clan = self.clan_repo.get_user_clan(ctx.author.id)
        if not clan:
            await ctx.send("❌ Você não está em um clã.")
            return

        if clan["role"] == "leader":
            await ctx.send(
                "❌ O líder não pode sair do clã. Você deve promover outro membro ou deletar o clã (em breve)."
            )
            return

        if self.clan_repo.remove_member(clan["id"], ctx.author.id):
            await ctx.send(f"👋 Você saiu do clã **{clan['name']}**.")
        else:
            await ctx.send("❌ Erro ao sair do clã.")

    @commands.group(name="guerra", invoke_without_command=True)
    async def guerra(self, ctx):
        """Sistema de Guerras entre Clãs."""
        await ctx.send(
            "⚔️ **Guerra de Clãs**\nUse `!guerra declarar <tag>` para iniciar um conflito."
        )

    @guerra.command(name="declarar")
    async def war_declare(self, ctx, tag: str):
        """Declara guerra contra outro clã."""
        my_clan = self.clan_repo.get_user_clan(ctx.author.id)
        if not my_clan:
            await ctx.send("❌ Você não pertence a um clã.")
            return
        if my_clan["role"] != "leader":
            await ctx.send("❌ Apenas Líderes de clã podem declarar guerra.")
            return

        target_clan = self.clan_repo.get_clan_by_tag(tag)
        if not target_clan:
            await ctx.send("❌ Clã alvo não encontrado.")
            return

        if my_clan["id"] == target_clan["id"]:
            await ctx.send("❌ Você não pode declarar guerra contra si mesmo.")
            return

        # Check if already in war
        if self.clan_repo.get_active_war(my_clan["id"]):
            await ctx.send("❌ Seu clã já está em uma guerra ativa.")
            return

        if self.clan_repo.get_active_war(target_clan["id"]):
            await ctx.send("❌ O clã alvo já está em uma guerra ativa.")
            return

        war_id = self.clan_repo.declare_war(my_clan["id"], target_clan["id"])
        if war_id:
            await ctx.send(
                f"⚔️ **GUERRA DECLARADA!**\n**{my_clan['name']}** VS **{target_clan['name']}**\nQue vença o melhor!"
            )
        else:
            await ctx.send("❌ Erro ao declarar guerra.")

    @guerra.command(name="placar")
    async def war_status(self, ctx):
        """Mostra o status da guerra atual."""
        clan = self.clan_repo.get_user_clan(ctx.author.id)
        if not clan:
            await ctx.send("❌ Você não está em um clã.")
            return

        war = self.clan_repo.get_active_war(clan["id"])
        if not war:
            await ctx.send("🏳️ Seu clã não está em nenhuma guerra ativa.")
            return

        # Need to fetch names for display
        c1 = self.clan_repo.get_all_clans()  # Lazy but works for small sets
        n1 = next((c["name"] for c in c1 if c["id"] == war["clan1_id"]), "Clã 1")
        n2 = next((c["name"] for c in c1 if c["id"] == war["clan2_id"]), "Clã 2")

        embed = discord.Embed(title="⚔️ Placar de Guerra", color=discord.Color.red())
        embed.add_field(name=n1, value=f"Points: {war['clan1_points']}", inline=True)
        embed.add_field(name="VS", value="\u200b", inline=True)
        embed.add_field(name=n2, value=f"Points: {war['clan2_points']}", inline=True)
        embed.set_footer(text=f"Expira em: {war['expires_at']}")
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Load the Clans cog."""
    await bot.add_cog(Clans(bot))
