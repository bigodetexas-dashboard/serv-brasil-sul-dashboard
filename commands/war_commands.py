# -*- coding: utf-8 -*-
"""
Comandos Discord para Sistema de Guerra entre Clãs
BigodeTexas v2.3
"""
import discord
from discord.ext import commands
from discord import app_commands
import sys
import os

# Adicionar raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import war_system
import database


class WarCommands(commands.Cog):
    """Comandos de Guerra entre Clãs"""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="war_start", description="Inicia uma guerra entre dois clãs")
    @app_commands.describe(
        clan1="Tag do primeiro clã (ex: TXS)",
        clan2="Tag do segundo clã (ex: INIMIGOS)"
    )
    async def war_start(self, interaction: discord.Interaction, clan1: str, clan2: str):
        """Inicia uma guerra entre dois clãs"""

        # Verificar permissões (apenas ADMIN)
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Apenas administradores podem iniciar guerras!",
                ephemeral=True
            )
            return

        clan1 = clan1.upper().strip()
        clan2 = clan2.upper().strip()

        if clan1 == clan2:
            await interaction.response.send_message(
                "❌ Os clãs devem ser diferentes!",
                ephemeral=True
            )
            return

        # Verificar se os clãs existem
        conn = database.get_connection()
        if conn:
            cur = conn.cursor()

            # Verificar clan1
            cur.execute("SELECT COUNT(*) FROM clans WHERE tag = ?", (clan1,))
            if cur.fetchone()[0] == 0:
                await interaction.response.send_message(
                    f"❌ Clã '{clan1}' não encontrado no sistema!",
                    ephemeral=True
                )
                conn.close()
                return

            # Verificar clan2
            cur.execute("SELECT COUNT(*) FROM clans WHERE tag = ?", (clan2,))
            if cur.fetchone()[0] == 0:
                await interaction.response.send_message(
                    f"❌ Clã '{clan2}' não encontrado no sistema!",
                    ephemeral=True
                )
                conn.close()
                return

            conn.close()

        # Criar guerra
        conn = war_system.get_war_db()
        if not conn:
            await interaction.response.send_message(
                "❌ Erro ao conectar ao banco de dados!",
                ephemeral=True
            )
            return

        try:
            cur = conn.cursor()

            # Normalizar ordem alfabética
            clan_a, clan_b = sorted([clan1, clan2])

            # Verificar se já existe guerra ativa
            cur.execute("""
                SELECT id FROM clan_wars
                WHERE ((clan1_tag = ? AND clan2_tag = ?) OR (clan1_tag = ? AND clan2_tag = ?))
                AND is_active = 1
            """, (clan_a, clan_b, clan_b, clan_a))

            if cur.fetchone():
                await interaction.response.send_message(
                    f"⚠️ Já existe uma guerra ativa entre **{clan1}** e **{clan2}**!",
                    ephemeral=True
                )
                conn.close()
                return

            # Criar nova guerra
            cur.execute("""
                INSERT INTO clan_wars (clan1_tag, clan2_tag, clan1_kills, clan2_kills, is_active)
                VALUES (?, ?, 0, 0, 1)
            """, (clan_a, clan_b))

            conn.commit()
            conn.close()

            # Criar embed de confirmação
            embed = discord.Embed(
                title="⚔️ GUERRA DECLARADA!",
                description=f"Uma guerra foi iniciada entre os clãs!",
                color=discord.Color.red()
            )
            embed.add_field(name="🔴 Clã 1", value=f"**{clan1}**", inline=True)
            embed.add_field(name="🔵 Clã 2", value=f"**{clan2}**", inline=True)
            embed.add_field(name="📊 Placar", value="**0 x 0**", inline=False)
            embed.set_footer(text="Use /war_status para ver o placar atualizado")

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            await interaction.response.send_message(
                f"❌ Erro ao criar guerra: {e}",
                ephemeral=True
            )
            if conn:
                conn.close()

    @app_commands.command(name="war_status", description="Exibe o status de uma guerra")
    @app_commands.describe(
        clan1="Tag do primeiro clã",
        clan2="Tag do segundo clã"
    )
    async def war_status(self, interaction: discord.Interaction, clan1: str, clan2: str):
        """Exibe o placar de uma guerra"""

        clan1 = clan1.upper().strip()
        clan2 = clan2.upper().strip()

        conn = war_system.get_war_db()
        if not conn:
            await interaction.response.send_message(
                "❌ Erro ao conectar ao banco de dados!",
                ephemeral=True
            )
            return

        try:
            cur = conn.cursor()

            # Normalizar ordem alfabética
            clan_a, clan_b = sorted([clan1, clan2])

            # Buscar guerra
            cur.execute("""
                SELECT clan1_tag, clan2_tag, clan1_kills, clan2_kills, started_at, is_active
                FROM clan_wars
                WHERE ((clan1_tag = ? AND clan2_tag = ?) OR (clan1_tag = ? AND clan2_tag = ?))
                AND is_active = 1
            """, (clan_a, clan_b, clan_b, clan_a))

            war = cur.fetchone()
            conn.close()

            if not war:
                await interaction.response.send_message(
                    f"⚠️ Não há guerra ativa entre **{clan1}** e **{clan2}**!",
                    ephemeral=True
                )
                return

            war_clan1, war_clan2, kills1, kills2, started_at, is_active = war

            # Determinar kills corretos baseado na ordem
            if war_clan1 == clan1.upper():
                score_clan1 = kills1
                score_clan2 = kills2
            else:
                score_clan1 = kills2
                score_clan2 = kills1

            # Criar embed de status
            embed = discord.Embed(
                title="⚔️ STATUS DA GUERRA",
                description=f"Guerra entre **{clan1}** e **{clan2}**",
                color=discord.Color.orange()
            )

            embed.add_field(name=f"🔴 {clan1}", value=f"**{score_clan1} kills**", inline=True)
            embed.add_field(name=f"🔵 {clan2}", value=f"**{score_clan2} kills**", inline=True)
            embed.add_field(name="📊 Placar", value=f"**{score_clan1} x {score_clan2}**", inline=False)
            embed.add_field(name="📅 Iniciada em", value=started_at, inline=False)

            # Determinar líder
            if score_clan1 > score_clan2:
                leader = f"🏆 **{clan1}** está na liderança!"
            elif score_clan2 > score_clan1:
                leader = f"🏆 **{clan2}** está na liderança!"
            else:
                leader = "⚖️ **Empate!**"

            embed.add_field(name="Líder", value=leader, inline=False)
            embed.set_footer(text="O placar é atualizado automaticamente a cada kill")

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            await interaction.response.send_message(
                f"❌ Erro ao buscar status: {e}",
                ephemeral=True
            )
            if conn:
                conn.close()

    @app_commands.command(name="war_end", description="Finaliza uma guerra entre clãs")
    @app_commands.describe(
        clan1="Tag do primeiro clã",
        clan2="Tag do segundo clã"
    )
    async def war_end(self, interaction: discord.Interaction, clan1: str, clan2: str):
        """Finaliza uma guerra"""

        # Verificar permissões (apenas ADMIN)
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Apenas administradores podem finalizar guerras!",
                ephemeral=True
            )
            return

        clan1 = clan1.upper().strip()
        clan2 = clan2.upper().strip()

        conn = war_system.get_war_db()
        if not conn:
            await interaction.response.send_message(
                "❌ Erro ao conectar ao banco de dados!",
                ephemeral=True
            )
            return

        try:
            cur = conn.cursor()

            # Normalizar ordem alfabética
            clan_a, clan_b = sorted([clan1, clan2])

            # Buscar guerra antes de finalizar
            cur.execute("""
                SELECT clan1_tag, clan2_tag, clan1_kills, clan2_kills
                FROM clan_wars
                WHERE ((clan1_tag = ? AND clan2_tag = ?) OR (clan1_tag = ? AND clan2_tag = ?))
                AND is_active = 1
            """, (clan_a, clan_b, clan_b, clan_a))

            war = cur.fetchone()

            if not war:
                await interaction.response.send_message(
                    f"⚠️ Não há guerra ativa entre **{clan1}** e **{clan2}**!",
                    ephemeral=True
                )
                conn.close()
                return

            war_clan1, war_clan2, kills1, kills2 = war

            # Finalizar guerra
            cur.execute("""
                UPDATE clan_wars
                SET is_active = 0, ended_at = CURRENT_TIMESTAMP
                WHERE ((clan1_tag = ? AND clan2_tag = ?) OR (clan1_tag = ? AND clan2_tag = ?))
                AND is_active = 1
            """, (clan_a, clan_b, clan_b, clan_a))

            conn.commit()
            conn.close()

            # Determinar vencedor
            if kills1 > kills2:
                winner = war_clan1
                loser = war_clan2
                winner_kills = kills1
                loser_kills = kills2
            elif kills2 > kills1:
                winner = war_clan2
                loser = war_clan1
                winner_kills = kills2
                loser_kills = kills1
            else:
                winner = None
                winner_kills = kills1
                loser_kills = kills2

            # Criar embed de finalização
            embed = discord.Embed(
                title="🏁 GUERRA FINALIZADA!",
                description=f"A guerra entre **{clan1}** e **{clan2}** foi encerrada!",
                color=discord.Color.green()
            )

            embed.add_field(name="📊 Placar Final", value=f"**{kills1} x {kills2}**", inline=False)

            if winner:
                embed.add_field(
                    name="🏆 Vencedor",
                    value=f"**{winner}** com **{winner_kills}** kills!",
                    inline=False
                )
            else:
                embed.add_field(name="⚖️ Resultado", value="**EMPATE!**", inline=False)

            embed.set_footer(text="Use /war_start para iniciar uma nova guerra")

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            await interaction.response.send_message(
                f"❌ Erro ao finalizar guerra: {e}",
                ephemeral=True
            )
            if conn:
                conn.close()

    @app_commands.command(name="war_list", description="Lista todas as guerras ativas")
    async def war_list(self, interaction: discord.Interaction):
        """Lista todas as guerras ativas"""

        conn = war_system.get_war_db()
        if not conn:
            await interaction.response.send_message(
                "❌ Erro ao conectar ao banco de dados!",
                ephemeral=True
            )
            return

        try:
            cur = conn.cursor()

            cur.execute("""
                SELECT clan1_tag, clan2_tag, clan1_kills, clan2_kills, started_at
                FROM clan_wars
                WHERE is_active = 1
                ORDER BY started_at DESC
            """)

            wars = cur.fetchall()
            conn.close()

            if not wars:
                await interaction.response.send_message(
                    "ℹ️ Não há guerras ativas no momento.",
                    ephemeral=True
                )
                return

            # Criar embed com lista de guerras
            embed = discord.Embed(
                title="⚔️ GUERRAS ATIVAS",
                description=f"Total de guerras em andamento: **{len(wars)}**",
                color=discord.Color.blue()
            )

            for clan1, clan2, kills1, kills2, started_at in wars:
                score = f"{kills1} x {kills2}"
                leader = f"🏆 {clan1}" if kills1 > kills2 else (f"🏆 {clan2}" if kills2 > kills1 else "⚖️ Empate")

                embed.add_field(
                    name=f"⚔️ {clan1} vs {clan2}",
                    value=f"**Placar**: {score}\n{leader}\n📅 Desde: {started_at[:10]}",
                    inline=False
                )

            embed.set_footer(text="Use /war_status [clan1] [clan2] para ver detalhes")

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            await interaction.response.send_message(
                f"❌ Erro ao listar guerras: {e}",
                ephemeral=True
            )
            if conn:
                conn.close()


async def setup(bot):
    """Registrar comandos de guerra"""
    await bot.add_cog(WarCommands(bot))
