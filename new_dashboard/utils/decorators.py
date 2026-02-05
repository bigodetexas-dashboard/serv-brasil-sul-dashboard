import asyncio
from discord.ext import commands
import discord
from security import rate_limiter, security_logger

# Para require_admin_password, precisamos acessar a whitelist e a senha
# Como elas sÃ£o carregadas do .env no bot_main, podemos importÃ¡-las ou passar par ao decorator.
# Uma forma comum em Cogs Ã© usar o bot.admin_password se anexarmos ao bot.


def rate_limit():
    """Decorator que aplica rate limiting em comandos"""

    async def predicate(ctx):
        if not rate_limiter.is_allowed(ctx.author.id):
            security_logger.log_rate_limit(ctx.author.id)
            await ctx.send(
                "â° **Calma lÃ¡, parceiro!** VocÃª estÃ¡ enviando comandos muito rÃ¡pido. Aguarde um momento."
            )
            return False
        return True

    return commands.check(predicate)


def require_admin_password():
    """Decorator que solicita senha E verifica whitelist antes de executar comandos admin"""

    async def predicate(ctx):
        # Acessa os dados atravÃ©s do objeto bot
        admin_whitelist = getattr(ctx.bot, "admin_whitelist", None)
        admin_password = getattr(ctx.bot, "admin_password", None)

        if not admin_whitelist or not admin_whitelist.is_admin(ctx.author.id):
            security_logger.log_failed_auth(ctx.author.id, ctx.command.name)
            await ctx.send(
                "âŒ **Acesso Negado!** VocÃª nÃ£o estÃ¡ autorizado a usar comandos administrativos."
            )
            return False

        # Try to send DM first
        try:
            dm_channel = await ctx.author.create_dm()
            await dm_channel.send(
                f"ðŸ” **AutenticaÃ§Ã£o Administrativa para: {ctx.command.name}**\nPor favor, digite a senha de acesso:"
            )
            await ctx.send(
                f"ðŸ“© {ctx.author.mention}, enviei uma solicitaÃ§Ã£o de autenticaÃ§Ã£o no seu **Privado (DM)**."
            )
        except discord.Forbidden:
            await ctx.send(
                "âŒ **Erro:** NÃ£o consegui te enviar DM. Verifique se suas mensagens privadas estÃ£o abertas para membros do servidor."
            )
            return False

        def check(m):
            return m.author == ctx.author and isinstance(m.channel, discord.DMChannel)

        try:
            msg = await ctx.bot.wait_for("message", check=check, timeout=60.0)

            if msg.content == admin_password:
                await dm_channel.send("âœ… **Senha correta!** Executando comando...")
                security_logger.log_admin_action(ctx.author.id, ctx.command.name)
                return True
            else:
                await dm_channel.send("âŒ **Senha incorreta!** Acesso negado.")
                security_logger.log_failed_auth(
                    ctx.author.id, f"{ctx.command.name} - wrong password"
                )
                return False

        except asyncio.TimeoutError:
            await dm_channel.send("â° **Tempo esgotado!** AutenticaÃ§Ã£o cancelada.")
            return False

    return commands.check(predicate)
