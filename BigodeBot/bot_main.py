import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from flask import Flask
import threading

from repositories.clan_repository import ClanRepository

from security import AdminWhitelist

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
FOOTER_ICON = os.getenv("FOOTER_ICON")

# Configuração de Segurança Admin
admin_ids_str = os.getenv("ADMIN_DISCORD_IDS", "")
admin_ids = [int(x.strip()) for x in admin_ids_str.split(",") if x.strip().isdigit()]
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Anexa configurações de segurança ao bot para uso nos decoradores
bot.admin_whitelist = AdminWhitelist(admin_ids)
bot.admin_password = ADMIN_PASSWORD

if not admin_ids:
    print(
        "[WARNING] ADMIN_DISCORD_IDS não configurado! Comandos admin ficarão bloqueados."
    )
if not ADMIN_PASSWORD:
    print("[WARNING] ADMIN_PASSWORD não configurado! Comandos admin falharão.")

# Saúde do Bot (Dashboard base)
health_app = Flask(__name__)


@health_app.route("/")
def home():
    return "BigodeTexas Bot is Online!"


def run_health_server():
    # Restricted to localhost for safety, use environment variable if needed for external access
    host = os.getenv("HEALTH_HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "3000"))
    health_app.run(host=host, port=port)


# REPOSITÓRIOS
clan_repo = ClanRepository()


@bot.event
async def on_ready():
    print(f"Bot online como {bot.user}")

    # Carregar Cogs
    initial_extensions = [
        "cogs.economy",
        "cogs.clans",
        "cogs.killfeed",
        "cogs.admin",
        "cogs.ai",
        "cogs.leaderboard",
        "cogs.tools",
    ]

    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)
            print(f"Cog {extension} carregada.")
        except Exception as e:
            print(f"Erro ao carregar {extension}: {e}")

    # Define o ícone global para uso em cogs
    bot.footer_icon = FOOTER_ICON
    print("BigodeTexas Bot totalmente carregado!")


@bot.command()
async def ajuda(ctx):
    """Exibe os comandos principais do bot."""
    embed = discord.Embed(
        title="🤠 MENU DE COMANDOS - BIGODE TEXAS",
        description="Confira o que eu posso fazer por você, sobrevivente!",
        color=discord.Color.blue(),
    )

    embed.add_field(
        name="💰 Economia",
        value="`!saldo`, `!daily`, `!transferir`, `!loja`, `!registrar`",
        inline=False,
    )
    embed.add_field(
        name="🛡️ Clãs",
        value="`!clan info`, `!clan novo`, `!clan convidar`, `!clan sair`",
        inline=False,
    )
    embed.add_field(
        name="📊 Rankings",
        value="`!top kills`, `!top coins`, `!top kd`, `!heatmap`",
        inline=False,
    )
    embed.add_field(
        name="🤖 Inteligência Artificial",
        value="`!ia <pergunta>`, `!analisarlogs` (Admin)",
        inline=False,
    )
    embed.add_field(
        name="🚨 Utilidades",
        value="`!alarme set`, `!alarme lista`, `!procurado`",
        inline=False,
    )
    embed.add_field(
        name="⚙️ Admin",
        value="`!restart`, `!clear`, `!spawn`, `!gameplay status` (Admin + Senha)",
        inline=False,
    )

    embed.set_footer(text="BigodeTexas • Servidor Hardcore", icon_url=FOOTER_ICON)
    await ctx.send(embed=embed)


# --- COMANDOS GAMEPLAY E GUERRA MOVIDOS PARA COGS ---

if __name__ == "__main__":
    # Rodar servidor de saúde em thread separada
    threading.Thread(target=run_health_server, daemon=True).start()

    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"\n[ERRO CRITICO] O bot falhou ao iniciar: {e}")
        input("Pressione ENTER para fechar...")
