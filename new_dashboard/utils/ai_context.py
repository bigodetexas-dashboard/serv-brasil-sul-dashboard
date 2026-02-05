"""
AI Context Builder - RAG System
Retrieves relevant game data from database to provide context for AI responses
"""

from typing import Dict, List, Optional
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repositories.base_repository import BaseRepository


class AIContextBuilder(BaseRepository):
    """Builds context for AI by querying game database"""

    def get_recent_kills(self, discord_id: str, limit: int = 5) -> List[Dict]:
        """Get user's recent kills"""
        query = """
            SELECT
                killer_name,
                victim_name,
                weapon,
                distance,
                timestamp
            FROM events
            WHERE event_type = 'kill' AND killer_name = (
                SELECT nitrado_gamertag FROM users WHERE discord_id = ?
            )
            ORDER BY timestamp DESC
            LIMIT ?
        """
        try:
            return self.execute_query(query, (discord_id, limit)) or []
        except Exception as e:
            print(f"[AI Context] Erro ao buscar kills: {e}")
            return []

    def get_recent_deaths(self, discord_id: str, limit: int = 5) -> List[Dict]:
        """Get user's recent deaths"""
        query = """
            SELECT
                killer_name,
                victim_name,
                weapon,
                distance,
                timestamp
            FROM events
            WHERE event_type = 'kill' AND victim_name = (
                SELECT nitrado_gamertag FROM users WHERE discord_id = ?
            )
            ORDER BY timestamp DESC
            LIMIT ?
        """
        try:
            return self.execute_query(query, (discord_id, limit)) or []
        except Exception as e:
            print(f"[AI Context] Erro ao buscar mortes: {e}")
            return []

    def get_user_stats(self, discord_id: str) -> Optional[Dict]:
        """Get user's overall stats"""
        # Try to get basic stats. Since kills/deaths might not be in users table yet,
        # we try to get them safely or default to 0.
        query = """
            SELECT
                discord_username,
                nitrado_gamertag,
                balance
            FROM users
            WHERE discord_id = ?
        """
        try:
            result = self.execute_query(query, (discord_id,))
            if not result:
                return None

            user_data = result[0]
            gt = user_data.get("nitrado_gamertag")

            # Dynamic kills/deaths calculation from events table
            if gt:
                k_query = "SELECT COUNT(*) as k FROM events WHERE killer_name = ? AND event_type = 'kill'"
                d_query = "SELECT COUNT(*) as d FROM events WHERE victim_name = ? AND event_type = 'kill'"

                k_res = self.execute_query(k_query, (gt,))
                d_res = self.execute_query(d_query, (gt,))

                user_data["kills"] = k_res[0]["k"] if k_res else 0
                user_data["deaths"] = d_res[0]["d"] if d_res else 0

                kills = user_data["kills"]
                deaths = user_data["deaths"]
                user_data["kd_ratio"] = (kills / deaths) if deaths > 0 else kills
            else:
                user_data["kills"] = 0
                user_data["deaths"] = 0
                user_data["kd_ratio"] = 0

            return user_data
        except Exception as e:
            print(f"[AI Context] Erro ao buscar stats: {e}")
            return None

    def get_clan_info(self, discord_id: str) -> Optional[Dict]:
        """Get user's clan information"""
        query = """
            SELECT
                c.name as clan_name,
                c.balance as clan_balance,
                cm.role as user_role,
                (SELECT COUNT(*) FROM clan_members WHERE clan_id = c.id) as member_count
            FROM clans c
            JOIN clan_members cm ON c.id = cm.clan_id
            WHERE cm.discord_id = ?
        """
        try:
            result = self.execute_query(query, (discord_id,))
            return result[0] if result else None
        except Exception as e:
            print(f"[AI Context] Erro ao buscar clan: {e}")
            return None

    def get_top_players(self, metric: str = "kills", limit: int = 5) -> List[Dict]:
        """Get leaderboard"""
        valid_metrics = ["kills", "balance", "deaths"]
        if metric not in valid_metrics:
            metric = "kills"

        query = f"""
            SELECT
                discord_username,
                nitrado_gamertag,
                {metric}
            FROM users
            WHERE {metric} > 0
            ORDER BY {metric} DESC
            LIMIT ?
        """
        try:
            # Note: Leaderboards might be simplified if kills/deaths columns are missing in users
            return self.execute_query(query, (limit,)) or []
        except Exception as e:
            print(f"[AI Context] Erro ao buscar top players: {e}")
            return []

    def get_server_activity_summary(self, hours: int = 24) -> Dict:
        """Get server activity in last N hours"""
        query = """
            SELECT
                COUNT(*) as total_kills,
                COUNT(DISTINCT killer_name) as unique_killers,
                COUNT(DISTINCT victim_name) as unique_victims,
                AVG(distance) as avg_kill_distance
            FROM events
            WHERE event_type = 'kill' AND timestamp > datetime('now', '-' || ? || ' hours')
        """
        try:
            result = self.execute_query(query, (hours,))
            return result[0] if result else {}
        except Exception as e:
            print(f"[AI Context] Erro ao buscar atividade do servidor: {e}")
            return {}

    def get_recent_purchases(self, discord_id: str, limit: int = 3) -> List[Dict]:
        """Get user's recent shop purchases"""
        query = """
            SELECT
                item_name,
                status,
                created_at,
                processed_at
            FROM delivery_queue
            WHERE discord_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """
        try:
            return self.execute_query(query, (discord_id, limit)) or []
        except Exception as e:
            print(f"[AI Context] Erro ao buscar compras: {e}")
            return []

    def build_context_string(self, discord_id: str, question: str) -> str:
        """
        Build a context string for AI based on user question
        """
        context_parts = []

        # Adicionar conhecimento da base de dados
        try:
            from utils.ai_knowledge import get_knowledge_context

            knowledge = get_knowledge_context(question)
            if knowledge:
                context_parts.append(f"CONHECIMENTO DO SERVIDOR:\n{knowledge}")
        except Exception as e:
            print(f"[Knowledge] Erro ao buscar: {e}")

        # Always include user stats
        stats = self.get_user_stats(discord_id)
        if stats:
            context_parts.append(
                f"UsuÃ¡rio: {stats.get('discord_username')} (Gamertag: {stats.get('nitrado_gamertag')})\n"
                f"Stats: {stats.get('kills')} kills, {stats.get('deaths')} deaths, "
                f"K/D: {stats.get('kd_ratio', 0):.2f}, Saldo: {stats.get('balance')} DZCoins"
            )

        # Check if question is about kills/deaths
        if any(
            word in question.lower()
            for word in ["matei", "kill", "eliminei", "morte", "morri"]
        ):
            recent_kills = self.get_recent_kills(discord_id, limit=3)
            recent_deaths = self.get_recent_deaths(discord_id, limit=3)

            if recent_kills:
                kills_text = "\n".join(
                    [
                        f"- Matou {k['victim_name']} com {k['weapon']} a {k['distance']}m"
                        for k in recent_kills
                    ]
                )
                context_parts.append(f"Ãšltimas eliminaÃ§Ãµes:\n{kills_text}")

            if recent_deaths:
                deaths_text = "\n".join(
                    [
                        f"- Morreu para {d['killer_name']} ({d['weapon']}) a {d['distance']}m"
                        for d in recent_deaths
                    ]
                )
                context_parts.append(f"Ãšltimas mortes:\n{deaths_text}")

        # Check if question is about clan
        if any(word in question.lower() for word in ["clan", "clÃ£", "grupo"]):
            clan = self.get_clan_info(discord_id)
            if clan and isinstance(clan, dict):  # Check if clan is a valid dict
                context_parts.append(
                    f"ClÃ£: {clan.get('clan_name')} ({clan.get('member_count')} membros)\n"
                    f"Cargo: {clan.get('user_role')}, Banco do ClÃ£: {clan.get('clan_balance')} DZCoins"
                )

        # Check if question is about leaderboard/ranking
        if any(
            word in question.lower() for word in ["ranking", "top", "melhor", "lÃ­der"]
        ):
            top_players = self.get_top_players("kills", limit=5)
            if top_players:
                rank_text = "\n".join(
                    [
                        f"{i + 1}. {p['discord_username']} - {p['kills']} kills"
                        for i, p in enumerate(top_players)
                    ]
                )
                context_parts.append(f"Top 5 Jogadores:\n{rank_text}")

        # Check if question is about server activity
        if any(
            word in question.lower()
            for word in ["servidor", "ativo", "online", "guerra"]
        ):
            activity = self.get_server_activity_summary(24)
            if activity:
                context_parts.append(
                    f"Atividade do Servidor (24h):\n"
                    f"- {activity.get('total_kills', 0)} kills totais\n"
                    f"- {activity.get('unique_killers', 0)} jogadores ativos em combate\n"
                    f"- DistÃ¢ncia mÃ©dia de kill: {activity.get('avg_kill_distance', 0):.0f}m"
                )

        # Check if question is about purchases
        if any(
            word in question.lower() for word in ["compra", "item", "entrega", "loja"]
        ):
            purchases = self.get_recent_purchases(discord_id, limit=3)
            if purchases:
                purchase_text = "\n".join(
                    [f"- {p['item_name']}: {p['status']}" for p in purchases]
                )
                context_parts.append(f"Ãšltimas compras:\n{purchase_text}")

        if context_parts:
            return "CONTEXTO DO JOGO:\n" + "\n\n".join(context_parts)
        else:
            return ""
