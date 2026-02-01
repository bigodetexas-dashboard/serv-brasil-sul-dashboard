import discord
from discord.ext import commands
import os
import google.generativeai as genai
from utils.dashboard_api import send_dashboard_event


class AIAgent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Configurar Gemini
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            genai.configure(api_key=gemini_key)
            self.model = genai.GenerativeModel("gemini-pro")
        else:
            self.model = None

    @commands.command(name="ia")
    async def ask_ai(self, ctx, *, question):
        """🤖 Pergunta algo para a IA do servidor (BigodeAI)."""
        if not self.model:
            await ctx.send("❌ IA não configurada (API Key faltando).")
            return

        async with ctx.typing():
            try:
                response = self.model.generate_content(question)
                await ctx.send(f"🤖 **BigodeAI:** {response.text}")
            except Exception as e:
                await ctx.send(f"❌ Erro na IA: {e}")

    @commands.command(name="gerarevento")
    @commands.has_permissions(administrator=True)
    async def generate_event(self, ctx):
        """🎲 (ADMIN) Gera uma ideia de evento aleatória usando IA."""
        if not self.model:
            await ctx.send("❌ IA não configurada.")
            return

        async with ctx.typing():
            prompt = "Sugira um evento criativo para um servidor de DayZ em Chernarus. Seja breve e épico."
            try:
                response = self.model.generate_content(prompt)
                embed = discord.Embed(
                    title="🎲 Sugestão de Evento",
                    description=response.text,
                    color=discord.Color.gold(),
                )
                embed.set_footer(text="Gerado por BigodeAI")
                await ctx.send(embed=embed)
            except Exception as e:
                await ctx.send(f"❌ Erro: {e}")


async def setup(bot):
    await bot.add_cog(AIAgent(bot))
