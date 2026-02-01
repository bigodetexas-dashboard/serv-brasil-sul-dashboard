import discord
from discord.ext import commands
import json
from datetime import datetime
from utils.helpers import load_json, save_json
import database


class Clans(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.clans_file = "clans.json"

    def load_clans(self):
        return load_json(self.clans_file)

    def save_clans(self, data):
        save_json(self.clans_file, data)

    def get_user_clan(self, user_id):
        """Retorna a tag do clã e os dados do clã do usuário."""
        # Tenta pegar do banco de dados primeiro se a tabela existir
        # Mas por compatibilidade com bot_main.py legado, varremos o JSON
        clans = self.load_clans()
        uid = str(user_id)
        for tag, data in clans.items():
            members = data.get("members", [])
            if isinstance(members, str):
                try:
                    members = json.loads(members)
                except:
                    members = []
            if data.get("leader") == uid or uid in [str(m) for m in members]:
                return tag, data
        return None, None

    @commands.group(name="clan", invoke_without_command=True)
    async def clan(self, ctx):
        """🛡️ Sistema de Clãs. Use !clan ajuda para ver os comandos."""
        await ctx.send(
            "🛡️ **Sistema de Clãs**\nUse `!clan ajuda` para ver os comandos disponíveis."
        )

    @clan.command(name="ajuda")
    async def clan_ajuda(self, ctx):
        msg = """
**🛡️ Comandos de Clã**
`!clan criar <nome>` - Cria um novo clã (Custo: 50.000 DZ Coins)
`!clan convidar <@usuario>` - Convida um jogador para o clã
`!clan entrar` - Aceita um convite pendente
`!clan sair` - Sai do clã atual
`!clan info` - Mostra informações do seu clã
`!clan kick <@usuario>` - (Líder) Expulsa um membro
"""
        await ctx.send(msg)

    @clan.command(name="criar")
    async def criar(self, ctx, *, nome: str):
        """Cria um novo clã."""
        clan_name, _ = self.get_user_clan(ctx.author.id)
        if clan_name:
            await ctx.send(f"❌ Você já está no clã **{clan_name}**. Saia primeiro.")
            return

        COST = 50000
        bal = database.get_balance(ctx.author.id)
        if bal < COST:
            await ctx.send(
                f"❌ Você precisa de **{COST} DZ Coins** para fundar um clã."
            )
            return

        clans = self.load_clans()
        for cname in clans:
            if cname.lower() == nome.lower():
                await ctx.send(f"❌ Já existe um clã com o nome **{nome}**.")
                return

        database.update_balance(ctx.author.id, -COST, "other", "Criação de Clã")
        clans[nome] = {
            "leader": str(ctx.author.id),
            "members": [],
            "created_at": datetime.now().isoformat(),
            "invites": [],
        }
        self.save_clans(clans)
        await ctx.send(
            f"🏰 **Clã {nome} fundado com sucesso por {ctx.author.mention}!**"
        )

    @clan.command(name="convidar")
    async def convidar(self, ctx, member: discord.Member):
        clan_name, clan_data = self.get_user_clan(ctx.author.id)
        if not clan_data or str(clan_data["leader"]) != str(ctx.author.id):
            await ctx.send("❌ Apenas o líder do clã pode convidar.")
            return

        clans = self.load_clans()
        if str(member.id) not in clans[clan_name]["invites"]:
            clans[clan_name]["invites"].append(str(member.id))
            self.save_clans(clans)
            await ctx.send(
                f"✉️ {member.mention}, você foi convidado para o clã **{clan_name}**! Use `!clan entrar` para aceitar."
            )
        else:
            await ctx.send(f"⚠️ {member.name} já foi convidado.")

    @clan.command(name="entrar")
    async def entrar(self, ctx):
        current_clan, _ = self.get_user_clan(ctx.author.id)
        if current_clan:
            await ctx.send(f"❌ Você já está no clã **{current_clan}**.")
            return

        clans = self.load_clans()
        found_invite = False
        uid = str(ctx.author.id)

        for name, data in clans.items():
            invites = [str(i) for i in data.get("invites", [])]
            if uid in invites:
                data["invites"] = [i for i in invites if i != uid]
                data["members"].append(uid)
                self.save_clans(clans)
                await ctx.send(f"✅ **Bem-vindo ao clã {name}, {ctx.author.mention}!**")
                found_invite = True
                break

        if not found_invite:
            await ctx.send("❌ Você não tem convites pendentes.")

    @clan.command(name="info")
    async def info(self, ctx):
        clan_name, clan_data = self.get_user_clan(ctx.author.id)
        if not clan_data:
            await ctx.send("❌ Você não tem clã.")
            return

        try:
            leader = await self.bot.fetch_user(int(clan_data["leader"]))
            leader_name = leader.name
        except:
            leader_name = str(clan_data["leader"])

        member_names = []
        for mid in clan_data["members"]:
            try:
                m = await self.bot.fetch_user(int(mid))
                member_names.append(m.name)
            except:
                member_names.append(str(mid))

        embed = discord.Embed(title=f"🛡️ Clã: {clan_name}", color=discord.Color.blue())
        embed.add_field(name="👑 Líder", value=leader_name, inline=True)
        embed.add_field(name="👥 Membros", value=f"{len(member_names)}", inline=True)
        if member_names:
            embed.add_field(name="Lista", value=", ".join(member_names), inline=False)

        await ctx.send(embed=embed)

    @commands.group(name="guerra", invoke_without_command=True)
    async def guerra(self, ctx):
        """Comandos de Guerra de Clãs"""
        await ctx.send(
            "⚔️ **Sistema de Guerras**\nUse `!guerra declarar <TAG>` para iniciar um conflito."
        )

    @guerra.command(name="declarar")
    async def guerra_declarar(self, ctx, tag_inimiga: str):
        """Declara guerra contra outro clã"""
        tag_inimiga = tag_inimiga.upper()
        my_tag, my_clan = self.get_user_clan(ctx.author.id)

        if not my_tag:
            await ctx.send("❌ Você não tem um clã!")
            return

        if str(my_clan["leader"]) != str(ctx.author.id):
            await ctx.send("❌ Apenas o líder pode declarar guerra!")
            return

        enemy_clan = database.get_clan(tag_inimiga)
        if not enemy_clan:
            await ctx.send("❌ Clã inimigo não encontrado!")
            return

        if tag_inimiga == my_tag:
            await ctx.send("❌ Você não pode declarar guerra a si mesmo!")
            return

        clans = self.load_clans()
        if "wars" not in clans:
            clans["wars"] = {}

        # Lógica de declaração simplificada para o Cog
        war_id = f"{my_tag}_vs_{tag_inimiga}"
        clans["wars"][war_id] = {
            "clan1": my_tag,
            "clan2": tag_inimiga,
            "active": True,
            "started_at": datetime.now().isoformat(),
            "score": {my_tag: 0, tag_inimiga: 0},
        }
        self.save_clans(clans)
        await ctx.send(
            f"⚔️ **GUERRA DECLARADA!**\n{my_tag} desafiou {tag_inimiga} para um banho de sangue!"
        )

    @guerra.command(name="status")
    async def guerra_status(self, ctx):
        clans = self.load_clans()
        wars = clans.get("wars", {})
        if not wars:
            await ctx.send("🕊️ Nenhuma guerra ativa no momento.")
            return

        embed = discord.Embed(title="⚔️ Guerras Ativas", color=discord.Color.red())
        for wid, data in wars.items():
            if data.get("active"):
                c1, c2 = data["clan1"], data["clan2"]
                s1, s2 = data["score"][c1], data["score"][c2]
                embed.add_field(
                    name=f"{c1} vs {c2}", value=f"Placar: **{s1} - {s2}**", inline=False
                )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Clans(bot))
