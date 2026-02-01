import asyncio
import discord
from discord.ext import commands
from security import rate_limiter, security_logger

# Para require_admin_password, precisamos acessar a whitelist e a senha
# Como elas são carregadas do .env no bot_main, podemos importá-las ou passar par ao decorator.
# Uma forma comum em Cogs é usar o bot.admin_password se anexarmos ao bot.


def rate_limit():
    """Decorator que aplica rate limiting em comandos"""

    async def predicate(ctx):
        if not rate_limiter.is_allowed(ctx.author.id):
            security_logger.log_rate_limit(ctx.author.id)
            await ctx.send(
                "⏰ **Calma lá, parceiro!** Você está enviando comandos muito rápido. Aguarde um momento."
            )
            return False
        return True

    return commands.check(predicate)


def require_admin_password():
    """Decorator que solicita senha E verifica whitelist antes de executar comandos admin"""

    async def predicate(ctx):
        # Acessa os dados através do objeto bot
        admin_whitelist = getattr(ctx.bot, "admin_whitelist", None)
        admin_password = getattr(ctx.bot, "admin_password", None)

        if not admin_whitelist or not admin_whitelist.is_admin(ctx.author.id):
            security_logger.log_failed_auth(ctx.author.id, ctx.command.name)
            await ctx.send(
                "❌ **Acesso Negado!** Você não está autorizado a usar comandos administrativos."
            )
            return False

        await ctx.send("🔐 **Comando Administrativo**\nDigite a senha de acesso:")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg = await ctx.bot.wait_for("message", check=check, timeout=30.0)

            if msg.content == admin_password:
                try:
                    await msg.delete()
                except Exception:
                    pass
                security_logger.log_admin_action(ctx.author.id, ctx.command.name)
                return True
            else:
                await ctx.send("❌ **Senha incorreta!** Acesso negado.")
                security_logger.log_failed_auth(
                    ctx.author.id, f"{ctx.command.name} - wrong password"
                )
                try:
                    await msg.delete()
                except Exception:
                    pass
                return False

        except asyncio.TimeoutError:
            await ctx.send("⏰ **Tempo esgotado!** Autenticação cancelada.")
            return False

    return commands.check(predicate)
