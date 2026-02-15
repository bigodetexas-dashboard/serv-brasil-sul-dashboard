"""Cog de economia do bot com sistema de loja, inventário e transações."""

import asyncio
import os
import random
import re
import sys
from datetime import datetime, timedelta

import discord
from discord.ext import commands

# Adicionar o diretório pai ao path para imports funcionarem
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database
from utils.decorators import rate_limit
from utils.ftp_helpers import upload_spawn_request
from utils.helpers import calculate_kd, find_item_by_key, load_json


class ShopPaginator(discord.ui.View):
    """Paginador para exibir itens da loja em múltiplas páginas."""

    def __init__(
        self, items_list, category_name, category_emoji, footer_icon, items_per_page=5
    ):
        super().__init__(timeout=60)
        self.items_list = items_list
        self.category_name = category_name
        self.category_emoji = category_emoji
        self.items_per_page = items_per_page
        self.footer_icon = footer_icon
        self.current_page = 0
        self.max_pages = (len(items_list) - 1) // items_per_page + 1

    def get_embed(self):
        start = self.current_page * self.items_per_page
        end = start + self.items_per_page
        page_items = self.items_list[start:end]
        embed = discord.Embed(
            title=f"{self.category_emoji} LOJA: {self.category_name.upper()}",
            description=f"Use `!comprar <codigo>` para adquirir.\nPágina {self.current_page + 1}/{self.max_pages}",
            color=discord.Color.gold(),
        )
        for k, v in page_items:
            embed.add_field(
                name=f"{v['name']} (`{k}`)",
                value=f"💰 {v['price']} DZ Coins\n_{v.get('description', 'Sem descrição')}_",
                inline=False,
            )
        embed.set_footer(
            text="BigodeTexas • Qualidade Garantida", icon_url=self.footer_icon
        )
        return embed

    @discord.ui.button(label="◀️ Anterior", style=discord.ButtonStyle.primary)
    async def previous_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)
        else:
            await interaction.response.send_message(
                "Você já está na primeira página!", ephemeral=True
            )

    @discord.ui.button(label="▶️ Próximo", style=discord.ButtonStyle.primary)
    async def next_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if self.current_page < self.max_pages - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)
        else:
            await interaction.response.send_message(
                "Você já está na última página!", ephemeral=True
            )


class Economy(commands.Cog):
    """Comandos de economia, loja e sistema de transações."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="saldo")
    async def saldo(self, ctx):
        bal = database.get_balance(ctx.author.id)
        eco = database.get_economy(ctx.author.id)
        gamertag = eco.get("gamertag", "Não vinculada")
        embed = discord.Embed(title="💰 Saldo", color=discord.Color.gold())
        embed.add_field(name="Usuário", value=ctx.author.mention, inline=True)
        embed.add_field(name="Gamertag", value=gamertag, inline=True)
        embed.add_field(name="DZ Coins", value=f"**{bal}** 💵", inline=False)
        embed.set_footer(
            text="BigodeTexas • Sistema Bancário", icon_url=self.bot.footer_icon
        )
        await ctx.send(embed=embed)

    @commands.command(name="daily")
    async def daily(self, ctx):
        eco = database.get_economy(ctx.author.id)
        last = eco.get("last_daily")
        if last:
            last_date = datetime.fromisoformat(last)
            if datetime.now() - last_date < timedelta(hours=24):
                await ctx.send("⏳ Você já pegou hoje.")
                return
        reward = random.randint(100, 500)
        database.update_balance(ctx.author.id, reward, "daily", "Bônus diário")
        eco = database.get_economy(ctx.author.id)
        eco["last_daily"] = datetime.now().isoformat()
        database.save_economy(ctx.author.id, eco)
        await ctx.send(f"🎁 Ganhou **{reward} DZ Coins**!")

    @commands.command(name="registrar")
    @rate_limit()
    async def registrar(self, ctx, gamertag: str):
        uid = str(ctx.author.id)
        existing = database.get_link_by_discord(ctx.author.id)
        if existing:
            await ctx.send("❌ Você já está registrado.")
            return
        database.save_link(gamertag, ctx.author.id)
        eco = database.get_economy(uid)
        if not eco:
            eco = {"discord_id": uid, "balance": 0}
        eco["gamertag"] = gamertag
        database.save_economy(uid, eco)
        await ctx.send(f"✅ Gamertag **{gamertag}** vinculada!")

    @commands.command(name="loja")
    async def loja(self, ctx, categoria: str = None):
        items_data = load_json("items.json")
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
            for cat in items_data.keys():
                msg += f"{emojis.get(cat, '📦')} **{cat.capitalize()}**\n"
            await ctx.send(msg)
        else:
            cat = categoria.lower()
            if cat not in items_data:
                await ctx.send("❌ Categoria não encontrada.")
                return
            paginator = ShopPaginator(
                list(items_data[cat].items()),
                cat,
                emojis.get(cat, "📦"),
                self.bot.footer_icon,
            )
            await ctx.send(embed=paginator.get_embed(), view=paginator)

    @commands.command(name="comprar")
    async def comprar(self, ctx, item_key: str):
        item = find_item_by_key(item_key.lower())
        if not item:
            await ctx.send("❌ Item não encontrado.")
            return

        price = item["price"]
        bal = database.get_balance(ctx.author.id)
        if bal < price:
            await ctx.send(f"❌ Falta dinheiro. Custa {price}, você tem {bal}.")
            return

        await ctx.send(
            f"📍 **Onde você quer receber o {item['name']}?**\nDigite `X Z` (Ex: `4500 10200`) ou `cancelar`."
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

            database.update_balance(
                ctx.author.id, -price, "purchase", f"Compra: {item['name']}"
            )
            database.add_to_inventory(ctx.author.id, item_key.lower(), item["name"])

            if upload_spawn_request(item["name"], coords_text):
                await ctx.send(
                    f"✅ **Compra realizada!**\nO drone do Bigode logo deixará seu {item['name']} em `{coords_text}`! 🚁"
                )
            else:
                await ctx.send(
                    "✅ Compra realizada, mas erro no drone. Item está no seu inventário virtual."
                )
        except asyncio.TimeoutError:
            await ctx.send("⏰ Tempo esgotado.")

    @commands.command(name="inventario")
    async def inventario(self, ctx):
        eco = database.get_economy(ctx.author.id)
        inv = eco.get("inventory", {})
        if not inv:
            await ctx.send("🎒 Seu inventário está vazio.")
            return

        embed = discord.Embed(
            title="🎒 Seu Inventário Virtual", color=discord.Color.blue()
        )
        for k, v in inv.items():
            embed.add_field(
                name=v["name"], value=f"Quantidade: {v['count']}", inline=False
            )
        await ctx.send(embed=embed)

    @commands.command(name="transferir")
    async def transferir(self, ctx, user: discord.Member, amount: int):
        if amount <= 0:
            await ctx.send("❌ Valor inválido.")
            return

        bal = database.get_balance(ctx.author.id)
        if bal < amount:
            await ctx.send("❌ Saldo insuficiente.")
            return

        database.update_balance(
            ctx.author.id,
            -amount,
            "transfer",
            f"Transferência para {user.display_name}",
        )
        database.update_balance(
            user.id, amount, "transfer", f"Recebido de {ctx.author.display_name}"
        )
        await ctx.send(f"💸 Transferido **{amount} DZ Coins** para {user.mention}!")

    @commands.command(name="conquistas")
    async def conquistas(self, ctx):
        eco = database.get_economy(ctx.author.id)
        unlocked = eco.get("achievements", {})

        embed = discord.Embed(title="🏆 Suas Conquistas", color=discord.Color.purple())
        for ach_id, ach_def in database.ACHIEVEMENTS_DEF.items():
            status = (
                "✅ Desbloqueado"
                if unlocked.get(ach_id, {}).get("unlocked")
                else "🔒 Bloqueado"
            )
            embed.add_field(
                name=f"{ach_def['name']} ({status})",
                value=ach_def["description"],
                inline=False,
            )
        await ctx.send(embed=embed)

    @commands.command(name="perfil")
    async def perfil(self, ctx, usuario: discord.Member = None):
        """Mostra o perfil completo de um jogador"""
        target = usuario or ctx.author
        eco = database.get_economy(target.id)
        if not eco:
            await ctx.send(f"❌ {target.name} ainda não está registrado.")
            return

        gamertag = eco.get("gamertag", "Não vinculada")
        stats = database.get_player(gamertag) if gamertag != "Não vinculada" else {}

        kills = stats.get("kills", 0)
        deaths = stats.get("deaths", 0)
        kd = calculate_kd(kills, deaths)

        achievements = eco.get("achievements", {})
        unlocked_count = sum(1 for a in achievements.values() if a.get("unlocked"))

        embed = discord.Embed(
            title=f"👤 Perfil de {target.name}", color=discord.Color.blue()
        )
        embed.set_thumbnail(url=target.avatar.url if target.avatar else None)
        embed.add_field(name="🎮 Gamertag", value=gamertag, inline=True)
        embed.add_field(
            name="💰 DZ Coins", value=f"{eco.get('balance', 0):,}", inline=True
        )
        embed.add_field(
            name="🏆 Conquistas",
            value=f"{unlocked_count}/{len(database.ACHIEVEMENTS_DEF)}",
            inline=True,
        )

        if kills > 0 or deaths > 0:
            embed.add_field(name="💀 Kills", value=str(kills), inline=True)
            embed.add_field(name="☠️ Deaths", value=str(deaths), inline=True)
            embed.add_field(name="📊 K/D", value=str(kd), inline=True)

        badges = [
            database.ACHIEVEMENTS_DEF[ach_id]["name"].split()[0]
            for ach_id, ach_data in achievements.items()
            if ach_data.get("unlocked") and ach_id in database.ACHIEVEMENTS_DEF
        ]

        if badges:
            embed.add_field(name="🎖️ Badges", value=" ".join(badges), inline=False)

        embed.set_footer(text="BigodeTexas • Perfil", icon_url=self.bot.footer_icon)
        await ctx.send(embed=embed)

    @commands.command(name="extrato")
    async def extrato(self, ctx, limite: int = 10):
        """Mostra o histórico de transações"""
        eco = database.get_economy(ctx.author.id)
        trans = eco.get("transactions", [])
        if not trans:
            await ctx.send("📜 Você ainda não tem transações registradas.")
            return

        transactions = trans[-limite:]
        transactions.reverse()
        embed = discord.Embed(title="📜 Extrato Bancário", color=discord.Color.blue())
        for t in transactions:
            amount_str = f"+{t['amount']}" if t["amount"] > 0 else str(t["amount"])
            ts = datetime.fromisoformat(t["timestamp"]).strftime("%d/%m %H:%M")
            emoji = {
                "kill": "🔫",
                "purchase": "🛒",
                "daily": "🎁",
                "transfer": "💸",
                "transfer_in": "📥",
                "transfer_out": "📤",
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
        """(Admin) Remove vinculação de uma gamertag"""
        if ctx.author.id not in self.bot.admin_whitelist:
            await ctx.send("❌ Apenas Admins podem desvincular contas.")
            return

        discord_id = database.get_link_by_gamertag(gamertag)
        if not discord_id:
            await ctx.send(f"❌ Gamertag **{gamertag}** não encontrada.")
            return

        database.remove_link(gamertag)
        eco = database.get_economy(discord_id)
        if eco:
            eco["gamertag"] = None
            database.save_economy(discord_id, eco)
        await ctx.send(f"✅ Gamertag **{gamertag}** desvinculada.")

    @commands.command(name="favoritar")
    async def favoritar(self, ctx, item_key: str):
        eco = database.get_economy(ctx.author.id)
        favs = eco.get("favorites", [])
        if item_key.lower() not in favs:
            favs.append(item_key.lower())
            eco["favorites"] = favs
            database.save_economy(ctx.author.id, eco)
            await ctx.send(f"⭐️ Item `{item_key}` favoritado!")

    @commands.command(name="favoritos")
    async def favoritos(self, ctx):
        eco = database.get_economy(ctx.author.id)
        favs = eco.get("favorites", [])
        if not favs:
            await ctx.send("⭐️ Você não tem itens favoritos.")
            return
        await ctx.send(f"⭐️ **Seus favoritos:** `{', '.join(favs)}`")

    @commands.command(name="desfavoritar")
    async def desfavoritar(self, ctx, item_key: str):
        eco = database.get_economy(ctx.author.id)
        favs = eco.get("favorites", [])
        if item_key.lower() in favs:
            favs.remove(item_key.lower())
            eco["favorites"] = favs
            database.save_economy(ctx.author.id, eco)
            await ctx.send(f"🗑️ `{item_key}` removido dos favoritos.")


async def setup(bot):
    await bot.add_cog(Economy(bot))
