"""
Economy COG - Manages the shop, inventory, and currency system.
"""

import asyncio
import random
import re
from datetime import datetime, timedelta

import discord
from discord.ext import commands

from repositories.player_repository import PlayerRepository
from repositories.item_repository import ItemRepository
from utils.helpers import calculate_kd
from utils.decorators import rate_limit
from utils.ftp_helpers import upload_spawn_request
from utils.achievements import ACHIEVEMENTS_DEF, check_new_achievements


class ShopPaginator(discord.ui.View):
    """View to handle shop pagination buttons."""

    def __init__(self, items_list, category_name, category_emoji, footer_icon, items_per_page=5):
        super().__init__(timeout=60)
        self.items_list = items_list
        self.category_name = category_name
        self.category_emoji = category_emoji
        self.items_per_page = items_per_page
        self.footer_icon = footer_icon
        self.current_page = 0
        self.max_pages = (len(items_list) - 1) // items_per_page + 1

    def get_embed(self):
        """Generates the embed for the current page."""
        start = self.current_page * self.items_per_page
        end = start + self.items_per_page
        page_items = self.items_list[start:end]
        embed = discord.Embed(
            title=f"{self.category_emoji} LOJA: {self.category_name.upper()}",
            description=(
                f"Use `!comprar <codigo>` para adquirir.\n"
                f"Página {self.current_page + 1}/{self.max_pages}"
            ),
            color=discord.Color.gold(),
        )
        for item in page_items:
            embed.add_field(
                name=f"{item['name']} (`{item['item_key']}`)",
                value=f"💰 {item['price']} DZ Coins\n_{item.get('description', 'Sem descrição')}_",
                inline=False,
            )
        embed.set_footer(text="BigodeTexas • Qualidade Garantida", icon_url=self.footer_icon)
        return embed

    @discord.ui.button(label="◀️ Anterior", style=discord.ButtonStyle.primary)
    async def previous_button(self, interaction: discord.Interaction, _: discord.ui.Button):
        """Handle previous page button click."""
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)
        else:
            await interaction.response.send_message(
                "Você já está na primeira página!", ephemeral=True
            )

    @discord.ui.button(label="▶️ Próximo", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, _: discord.ui.Button):
        """Handle next page button click."""
        if self.current_page < self.max_pages - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)
        else:
            await interaction.response.send_message(
                "Você já está na última página!", ephemeral=True
            )


class Economy(commands.Cog):
    """Economy commands and events."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the Economy cog."""
        self.bot = bot
        self.repo = PlayerRepository()
        self.item_repo = ItemRepository()

    @commands.command(name="saldo", aliases=["banco", "balance", "money"])
    async def saldo(self, ctx):
        """Verifica seu saldo atual de DZ Coins."""
        balance = self.repo.get_balance(ctx.author.id)
        stats = self.repo.get_player_stats_by_discord_id(ctx.author.id)
        gamertag = (
            stats["nitrado_gamertag"] if stats and stats["nitrado_gamertag"] else "Não vinculada"
        )

        embed = discord.Embed(title="💰 Saldo", color=discord.Color.gold())
        embed.add_field(name="Usuário", value=ctx.author.mention, inline=True)
        embed.add_field(name="Gamertag", value=gamertag, inline=True)
        embed.add_field(name="DZ Coins", value=f"**{balance:,}** 💵", inline=False)
        embed.set_footer(text="BigodeTexas • Sistema Bancário", icon_url=self.bot.footer_icon)
        await ctx.send(embed=embed)

    @commands.command(name="daily", aliases=["diario"])
    async def daily(self, ctx):
        """Resgata seu bônus diário."""
        # Verifica se já pegou hoje
        last_daily = self.repo.get_last_daily(ctx.author.id)

        if last_daily:
            last_date = (
                datetime.fromisoformat(last_daily) if isinstance(last_daily, str) else last_daily
            )
            if datetime.now() - last_date < timedelta(hours=24):
                next_time = last_date + timedelta(hours=24)
                # Formata o tempo restante (simplificado)
                diff = next_time - datetime.now()
                hours = diff.seconds // 3600
                minutes = (diff.seconds % 3600) // 60
                await ctx.send(f"⏳ Você já pegou hoje. Volte em {hours}h {minutes}m.")
                return

        reward = random.randint(100, 500)

        # Atualiza saldo e timestamp
        self.repo.update_balance(ctx.author.id, reward, "daily")
        self.repo.update_last_daily(ctx.author.id)

        await ctx.send(f"🎁 Ganhou **{reward} DZ Coins**!")

    @commands.command(name="registrar")
    @rate_limit()
    async def registrar(self, ctx, gamertag: str):
        """Vincula sua gamertag do DayZ à sua conta Discord."""
        # Verifica se esta gamertag já está vinculada a alguém
        # (Para isso, precisaríamos de um método repo.find_user_by_gamertag,
        # mas por hora, vamos apenas setar no usuário atual)

        existing_gt = self.repo.get_gamertag(ctx.author.id)
        if existing_gt:
            await ctx.send(f"❌ Você já está registrado como **{existing_gt}**.")
            return

        # Salva no DB
        if self.repo.set_gamertag(ctx.author.id, gamertag):
            await ctx.send(f"✅ Gamertag **{gamertag}** vinculada com sucesso!")
        else:
            await ctx.send(
                f"❌ Erro ao registrar. A gamertag **{gamertag}** já está em uso "
                "por outro usuário ou ocorreu um erro."
            )

    @commands.command(name="loja")
    async def loja(self, ctx, categoria: str = None):
        """Mostra os itens disponíveis na loja."""
        categories = self.item_repo.get_all_categories()
        emojis = {
            "armas": "🔫",
            "municao": "🎯",
            "carregadores": "📦",
            "acessorios": "🔧",
            "construcao": "🏗️",
            "ferramentas": "🛠️",
            "medico": "💊",
            "roupas": "👕",
            "veiculos": "🚗",
        }

        if not categoria:
            msg = "🛒 **LOJA BIGODE TEXAS**\nCategorias:\n"
            for cat in categories:
                msg += f"{emojis.get(cat, '📦')} **{cat.capitalize()}**\n"
            await ctx.send(msg)
        else:
            cat = categoria.lower()
            if cat not in categories:
                await ctx.send("❌ Categoria não encontrada.")
                return

            items_in_category = self.item_repo.get_items_by_category(cat)
            paginator = ShopPaginator(
                items_in_category,
                cat,
                emojis.get(cat, "📦"),
                self.bot.footer_icon,
            )
            await ctx.send(embed=paginator.get_embed(), view=paginator)

    @commands.command(name="comprar")
    async def comprar(self, ctx, item_key: str):
        """Compra um item da loja."""
        item = self.item_repo.get_item_by_key(item_key.lower())
        if not item:
            await ctx.send("❌ Item não encontrado.")
            return

        price = item["price"]
        bal = self.repo.get_balance(ctx.author.id)

        if bal < price:
            await ctx.send(f"❌ Falta dinheiro. Custa {price:,}, você tem {bal:,}.")
            return

        await ctx.send(
            f"📍 **Onde você quer receber o {item['name']}?**\n"
            "Digite `X Z` (Ex: `4500 10200`) ou `cancelar`."
        )

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=60.0)
            if msg.content.lower() == "cancelar":
                await ctx.send("🚫 Compra cancelada.")
                return

            coords_text = msg.content.strip()
            if not re.match(r"^[\d\.\-]+\s+[\d\.\-]+$", coords_text):
                await ctx.send("⚠️ Formato inválido! Use `X Z`. Compra cancelada.")
                return

            # Debita e adiciona ao inventário (transacional seria melhor, mas ok por agora)
            if self.repo.update_balance(ctx.author.id, -price, "purchase") >= 0:
                self.repo.add_to_inventory(ctx.author.id, item_key.lower(), item["name"])

                if upload_spawn_request(item["name"], coords_text):
                    await ctx.send(
                        f"✅ **Compra realizada!**\n"
                        f"O drone do Bigode logo deixará seu {item['name']} em `{coords_text}`! 🚁"
                    )
                else:
                    await ctx.send(
                        "✅ Compra realizada, mas erro no drone. "
                        "Item está no seu inventário virtual."
                    )
            else:
                await ctx.send("❌ Erro ao processar pagamento.")

        except asyncio.TimeoutError:
            await ctx.send("⏰ Tempo esgotado.")

    @commands.command(name="inventario", aliases=["inv"])
    async def inventario(self, ctx):
        """Mostra seu inventário virtual."""
        inv = self.repo.get_inventory(ctx.author.id)

        if not inv:
            await ctx.send("🎒 Seu inventário está vazio.")
            return

        embed = discord.Embed(title="🎒 Seu Inventário Virtual", color=discord.Color.blue())
        for v in inv.values():
            embed.add_field(name=v["name"], value=f"Quantidade: {v['count']}", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="transferir", aliases=["pay", "pagar"])
    async def transferir(self, ctx, user: discord.Member, amount: int):
        """Transfere DZ Coins para outro jogador."""
        if amount <= 0:
            await ctx.send("❌ Valor inválido.")
            return

        bal = self.repo.get_balance(ctx.author.id)
        if bal < amount:
            await ctx.send("❌ Saldo insuficiente.")
            return

        self.repo.update_balance(ctx.author.id, -amount, "transfer")
        self.repo.update_balance(user.id, amount, "transfer")

        await ctx.send(f"💸 Transferido **{amount:,} DZ Coins** para {user.mention}!")

    @commands.command(name="conquistas")
    async def conquistas(self, ctx):
        """Mostra suas conquistas desbloqueadas."""
        # 1. Busca dados necessários para a verificação
        unlocked = self.repo.get_unlocked_achievements(ctx.author.id)
        balance = self.repo.get_balance(ctx.author.id)

        transactions = self.repo.get_transactions(ctx.author.id, limit=50)
        stats = self.repo.get_player_stats_by_discord_id(ctx.author.id) or {}

        # 2. Verifica se houve novas conquistas agora
        newly_unlocked = check_new_achievements(
            ctx.author.id, unlocked, stats, balance, transactions
        )

        if newly_unlocked:
            for ach_id, ach_def in newly_unlocked:
                self.repo.unlock_achievement(ctx.author.id, ach_id)
                if ach_def["reward"] > 0:
                    self.repo.update_balance(ctx.author.id, ach_def["reward"], "achievement_reward")
                await ctx.send(f"🎊 **PARABÉNS!** Você desbloqueou: **{ach_def['name']}**!")
            # Atualiza lista de desbloqueados para o embed
            unlocked.extend([aid for aid, _ in newly_unlocked])

        # 3. Gera o embed
        embed = discord.Embed(title="🏆 Suas Conquistas", color=discord.Color.purple())
        for ach_id, ach_def in ACHIEVEMENTS_DEF.items():
            status = "✅ Desbloqueado" if ach_id in unlocked else "🔒 Bloqueado"
            embed.add_field(
                name=f"{ach_def['name']} ({status})",
                value=ach_def["description"],
                inline=False,
            )
        embed.set_footer(text="BigodeTexas • Conquistas", icon_url=self.bot.footer_icon)
        await ctx.send(embed=embed)

    @commands.command(name="perfil")
    async def perfil(self, ctx, usuario: discord.Member = None):
        """Mostra o perfil completo de um jogador."""
        target = usuario or ctx.author

        stats = self.repo.get_player_stats_by_discord_id(target.id) or {}
        gamertag = stats.get("nitrado_gamertag") or "Não vinculada"
        balance = stats.get("balance", 0)

        kills = stats.get("kills", 0)
        deaths = stats.get("deaths", 0)
        kd = calculate_kd(kills, deaths)

        embed = discord.Embed(title=f"👤 Perfil de {target.name}", color=discord.Color.blue())
        embed.set_thumbnail(url=target.avatar.url if target.avatar else None)
        embed.add_field(name="🎮 Gamertag", value=gamertag, inline=True)
        embed.add_field(
            name="💰 DZ Coins",
            value=f"{balance:,}",
            inline=True,
        )

        if kills > 0 or deaths > 0:
            embed.add_field(name="💀 Kills", value=str(kills), inline=True)
            embed.add_field(name="☠️ Deaths", value=str(deaths), inline=True)
            embed.add_field(name="📊 K/D", value=str(kd), inline=True)

        embed.set_footer(text="BigodeTexas • Perfil", icon_url=self.bot.footer_icon)
        await ctx.send(embed=embed)

    @commands.command(name="extrato")
    async def extrato(self, ctx, limite: int = 10):
        """Mostra o histórico de transações."""
        transactions = self.repo.get_transactions(ctx.author.id, limite)

        if not transactions:
            await ctx.send("📜 Você ainda não tem transações registradas (no novo sistema).")
            return

        embed = discord.Embed(title="📜 Extrato Bancário", color=discord.Color.blue())
        for t in transactions:
            amount = t["amount"]
            amount_str = f"+{amount}" if amount > 0 else str(amount)
            # Tenta tratar timestamp
            ts_str = t["created_at"]
            try:
                ts = datetime.fromisoformat(ts_str).strftime("%d/%m %H:%M")
            except ValueError:
                ts = str(ts_str)

            emoji = {
                "kill": "🔫",
                "purchase": "🛒",
                "daily": "🎁",
                "transfer": "💸",
            }.get(t["type"], "💰")

            embed.add_field(
                name=f"{emoji} {t['type'].capitalize()}",
                value=f"{amount_str} DZ Coins - {t.get('description', '')}\n`{ts}`",
                inline=False,
            )
        await ctx.send(embed=embed)

    @commands.command(name="desvincular")
    @rate_limit()
    async def desvincular(self, ctx, gamertag: str):
        """(Admin) Remove vinculação de uma gamertag."""
        if ctx.author.id not in self.bot.admin_whitelist.admin_ids:
            await ctx.send("❌ Apenas Admins podem desvincular contas.")
            return

        if self.repo.remove_gamertag(gamertag):
            await ctx.send(f"✅ Gamertag **{gamertag}** desvinculada.")
        else:
            await ctx.send(f"❌ Gamertag **{gamertag}** não encontrada.")

    @commands.command(name="favoritar")
    async def favoritar(self, ctx, item_key: str):
        """Adiciona um item aos favoritos."""
        if self.repo.add_favorite(ctx.author.id, item_key):
            await ctx.send(f"⭐️ Item `{item_key}` favoritado!")
        else:
            await ctx.send("❌ Erro ao favoritar.")

    @commands.command(name="favoritos")
    async def favoritos(self, ctx):
        """Mostra seus itens favoritos."""
        favs = self.repo.get_favorites(ctx.author.id)

        if not favs:
            await ctx.send("⭐️ Você não tem itens favoritos.")
            return

        await ctx.send(f"⭐️ **Seus favoritos:** `{', '.join(favs)}`")

    @commands.command(name="desfavoritar")
    async def desfavoritar(self, ctx, item_key: str):
        """Remove um item dos favoritos."""
        if self.repo.remove_favorite(ctx.author.id, item_key):
            await ctx.send(f"🗑️ `{item_key}` removido dos favoritos.")
        else:
            await ctx.send("❌ Erro ao remover favorito ou item não estava na lista.")


async def setup(bot: commands.Bot) -> None:
    """Setup the Economy cog."""
    await bot.add_cog(Economy(bot))
