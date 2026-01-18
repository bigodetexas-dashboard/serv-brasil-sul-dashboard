"""
AI Cog

Provides AI-powered commands using Google Gemini integration.
Includes Q&A, event generation, and log analysis features.
"""

import asyncio

import discord
from discord.ext import commands

import ai_integration
from repositories.player_repository import PlayerRepository
from utils.decorators import rate_limit, require_admin_password


class AI(commands.Cog):
    """
    AI-powered commands using Google Gemini.

    Provides intelligent responses, event generation, and log analysis.
    """

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the AI cog."""
        self.bot = bot
        self.player_repo = PlayerRepository()

    @commands.command(name="ia", aliases=["duvida", "pergunta", "bot", "bigodeia", "ask"])
    @rate_limit()
    async def ask_ai(self, ctx: commands.Context, *, question: str) -> None:
        """
        Ask a question to the server's AI (BigodeAI).

        The AI has context about your account (balance, stats) and can answer
        questions about DayZ, server rules, and general gameplay.

        Args:
            question: Your question for the AI

        Example:
            !ia Qual a melhor arma para sniper?
            !ia Como faço para criar um clã?
        """
        async with ctx.typing():
            # Tenta pegar contexto básico do usuário (ex: saldo)
            user_balance = self.player_repo.get_balance(ctx.author.id)
            context = f"Infos do usuário: Saldo {user_balance} DZ Coins."

            response = await ai_integration.ask_gemini(question, context_data=context)

            # Divide a resposta se for muito longa (limite Discord: 2000 chars)
            if len(response) > 2000:
                parts = [response[i : i + 1900] for i in range(0, len(response), 1900)]
                for part in parts:
                    await ctx.send(part)
            else:
                await ctx.send(response)

    @commands.command(name="gerarevento", aliases=["eventoa", "eventia"])
    @require_admin_password()
    async def generate_event(self, ctx: commands.Context) -> None:
        """
        Generate a random event idea using AI (ADMIN ONLY).

        Creates creative event suggestions with title, description,
        location, rewards, and difficulty level.

        Requires admin password authentication.
        """
        async with ctx.typing():
            event_data = await ai_integration.generate_event_idea()

            if not event_data:
                await ctx.send(
                    "❌ Não consegui pensar em nada agora. Verifique a API Key ou tente novamente."
                )
                return

            embed = discord.Embed(
                title=f"🎲 Sugestão de Evento: {event_data.get('title')}",
                description=event_data.get("description"),
                color=discord.Color.purple(),
            )
            embed.add_field(name="📍 Local", value=event_data.get("location", "N/A"), inline=True)
            embed.add_field(
                name="🎁 Recompensa", value=event_data.get("reward", "N/A"), inline=True
            )
            embed.add_field(
                name="💀 Dificuldade",
                value=event_data.get("difficulty", "N/A"),
                inline=True,
            )
            embed.set_footer(
                text="Gerações automáticas via BigodeAI", icon_url=self.bot.footer_icon
            )

            await ctx.send(embed=embed)

    @commands.command(name="analisarlogs")
    @require_admin_password()
    async def analyze_logs(self, ctx: commands.Context, lines: int = 20) -> None:
        """
        Use AI to analyze recent PvP kill logs (ADMIN ONLY).

        Analyzes patterns, identifies potential cheaters, and provides
        insights about player behavior based on recent kills.

        Args:
            lines: Number of recent log entries to analyze (default: 20)

        Requires admin password authentication.

        Example:
            !analisarlogs 30
        """
        async with ctx.typing():
            try:
                # Helper para rodar em thread (evita bloquear loop)
                def fetch_logs_sync():
                    conn = self.player_repo.get_conn()
                    try:
                        cur = conn.cursor()
                        cur.execute(
                            "SELECT killer_name, victim_name, weapon, distance, timestamp FROM pvp_kills ORDER BY timestamp DESC LIMIT ?",
                            (lines,),
                        )
                        return cur.fetchall()
                    finally:
                        conn.close()

                rows = await asyncio.to_thread(fetch_logs_sync)

                if not rows:
                    await ctx.send("Sem eventos recentes no banco para analisar.")
                    return

                log_data = [
                    f"{row['timestamp']} - {row['killer_name']} matou {row['victim_name']} com {row['weapon']} ({row['distance']}m)"
                    for row in rows
                ]

                analysis = await ai_integration.analyze_behavior(log_data)

                embed = discord.Embed(
                    title="🕵️ Análise de Inteligência (IA)",
                    description=analysis,
                    color=discord.Color.dark_grey(),
                )
                embed.set_footer(text="Processado via BigodeAI", icon_url=self.bot.footer_icon)
                await ctx.send(embed=embed)

            except Exception as e:
                await ctx.send(f"Erro ao buscar logs: {e}")


async def setup(bot: commands.Bot) -> None:
    """Load the AI cog."""
    await bot.add_cog(AI(bot))
