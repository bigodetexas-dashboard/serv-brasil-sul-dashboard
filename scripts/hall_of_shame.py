# -*- coding: utf-8 -*-
"""
Hall of Shame - Muro da Vergonha
Visualiza jogadores banidos automaticamente pelo sistema anti-cheat
"""
import os
import sys
import sqlite3
from datetime import datetime, timedelta

# Adicionar raiz ao path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Configurar UTF-8 no Windows
if sys.platform == "win32":
    import codecs
    if hasattr(sys.stdout, 'detach'):
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

DB_PATH = os.path.join(PROJECT_ROOT, "bigode_unified.db")


def get_hall_of_shame(limit=50, infraction_type=None, days=None):
    """
    Retorna lista do Muro da Vergonha

    Args:
        limit (int): Número máximo de registros
        infraction_type (str): Filtrar por tipo de infração
        days (int): Mostrar apenas dos últimos N dias
    """

    if not os.path.exists(DB_PATH):
        print(f"[ERRO] Banco de dados não encontrado: {DB_PATH}")
        return []

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Construir query
        query = """
            SELECT
                gamertag,
                xuid,
                infraction_type,
                severity,
                description,
                evidence,
                detected_at,
                auto_banned,
                ban_lifted
            FROM infractions
            WHERE auto_banned = 1
        """

        params = []

        # Filtros
        if infraction_type:
            query += " AND infraction_type = ?"
            params.append(infraction_type)

        if days:
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            query += " AND DATE(detected_at) >= ?"
            params.append(cutoff_date)

        query += " ORDER BY detected_at DESC LIMIT ?"
        params.append(limit)

        cur.execute(query, params)
        rows = cur.fetchall()

        results = []
        for row in rows:
            results.append({
                "gamertag": row["gamertag"],
                "xuid": row["xuid"],
                "infraction_type": row["infraction_type"],
                "severity": row["severity"],
                "description": row["description"],
                "evidence": row["evidence"],
                "detected_at": row["detected_at"],
                "auto_banned": row["auto_banned"],
                "ban_lifted": row["ban_lifted"]
            })

        conn.close()
        return results

    except Exception as e:
        print(f"[ERRO] Falha ao buscar Muro da Vergonha: {e}")
        import traceback
        traceback.print_exc()
        return []


def display_hall_of_shame(limit=20, infraction_type=None, days=7):
    """Exibe Muro da Vergonha formatado"""

    print("\n" + "=" * 80)
    print(" " * 25 + "MURO DA VERGONHA")
    print(" " * 20 + "Hall of Shame - BigodeTexas")
    print("=" * 80)

    # Filtros aplicados
    filters = []
    if infraction_type:
        filters.append(f"Tipo: {infraction_type}")
    if days:
        filters.append(f"Ultimos {days} dias")
    filters.append(f"Limite: {limit}")

    print(f"\nFiltros: {' | '.join(filters)}\n")

    # Buscar dados
    results = get_hall_of_shame(limit=limit, infraction_type=infraction_type, days=days)

    if not results:
        print("[INFO] Nenhum banimento registrado com os filtros especificados.\n")
        return

    print(f"Total de banimentos encontrados: {len(results)}\n")
    print("-" * 80)

    # Exibir cada banimento
    for i, ban in enumerate(results, 1):
        print(f"\n#{i} - {ban['gamertag']}")
        print(f"{'─' * 80}")

        # Informações básicas
        print(f"XUID:       {ban['xuid'] or 'N/A'}")
        print(f"Infracao:   {ban['infraction_type']}")
        print(f"Severidade: {ban['severity']}")
        print(f"Data:       {ban['detected_at']}")

        # Descrição
        print(f"\nMotivo:")
        print(f"  {ban['description']}")

        # Evidências
        if ban['evidence']:
            print(f"\nEvidencias:")
            evidence_lines = ban['evidence'].split('\n')
            for line in evidence_lines:
                print(f"  {line}")

        # Status
        status = "ATIVO" if not ban['ban_lifted'] else "REMOVIDO"
        print(f"\nStatus do Ban: {status}")

        print(f"{'─' * 80}")

    print()


def get_statistics():
    """Retorna estatísticas do Muro da Vergonha"""

    if not os.path.exists(DB_PATH):
        print(f"[ERRO] Banco de dados não encontrado: {DB_PATH}")
        return None

    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        # Total de banimentos
        cur.execute("SELECT COUNT(*) FROM infractions WHERE auto_banned = 1")
        total = cur.fetchone()[0]

        # Por tipo
        cur.execute("""
            SELECT infraction_type, COUNT(*) as count
            FROM infractions
            WHERE auto_banned = 1
            GROUP BY infraction_type
            ORDER BY count DESC
        """)
        by_type = cur.fetchall()

        # Por severidade
        cur.execute("""
            SELECT severity, COUNT(*) as count
            FROM infractions
            WHERE auto_banned = 1
            GROUP BY severity
            ORDER BY count DESC
        """)
        by_severity = cur.fetchall()

        # Últimas 24h
        cur.execute("""
            SELECT COUNT(*)
            FROM infractions
            WHERE auto_banned = 1
              AND datetime(detected_at) > datetime('now', '-24 hours')
        """)
        last_24h = cur.fetchone()[0]

        # Últimos 7 dias
        cur.execute("""
            SELECT COUNT(*)
            FROM infractions
            WHERE auto_banned = 1
              AND datetime(detected_at) > datetime('now', '-7 days')
        """)
        last_7d = cur.fetchone()[0]

        conn.close()

        return {
            "total": total,
            "by_type": by_type,
            "by_severity": by_severity,
            "last_24h": last_24h,
            "last_7d": last_7d
        }

    except Exception as e:
        print(f"[ERRO] Falha ao obter estatísticas: {e}")
        return None


def display_statistics():
    """Exibe estatísticas formatadas"""

    print("\n" + "=" * 80)
    print(" " * 25 + "ESTATISTICAS DO SISTEMA")
    print("=" * 80)

    stats = get_statistics()

    if not stats:
        print("\n[ERRO] Não foi possível obter estatísticas\n")
        return

    print(f"\nTotal de banimentos automaticos: {stats['total']}")
    print(f"Banimentos nas ultimas 24h: {stats['last_24h']}")
    print(f"Banimentos nos ultimos 7 dias: {stats['last_7d']}")

    # Por tipo
    print("\n" + "-" * 80)
    print("POR TIPO DE INFRACAO:")
    print("-" * 80)

    if stats['by_type']:
        for infraction_type, count in stats['by_type']:
            percentage = (count / stats['total'] * 100) if stats['total'] > 0 else 0
            bar = "#" * int(percentage / 2)
            print(f"{infraction_type:30} {count:5} ({percentage:5.1f}%) {bar}")
    else:
        print("  Nenhum dado disponivel")

    # Por severidade
    print("\n" + "-" * 80)
    print("POR SEVERIDADE:")
    print("-" * 80)

    if stats['by_severity']:
        for severity, count in stats['by_severity']:
            percentage = (count / stats['total'] * 100) if stats['total'] > 0 else 0
            bar = "#" * int(percentage / 2)
            print(f"{severity:30} {count:5} ({percentage:5.1f}%) {bar}")
    else:
        print("  Nenhum dado disponivel")

    print()


def main():
    """Menu principal"""

    import argparse

    parser = argparse.ArgumentParser(
        description="Hall of Shame - Muro da Vergonha | Sistema Anti-Cheat BigodeTexas"
    )

    parser.add_argument(
        "--stats",
        action="store_true",
        help="Exibir estatisticas em vez da lista"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Numero maximo de banimentos a exibir (padrao: 20)"
    )

    parser.add_argument(
        "--type",
        type=str,
        help="Filtrar por tipo de infracao (ex: fly_hack, lag_machine)"
    )

    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Mostrar apenas dos ultimos N dias (padrao: 7)"
    )

    args = parser.parse_args()

    if args.stats:
        display_statistics()
    else:
        display_hall_of_shame(
            limit=args.limit,
            infraction_type=args.type,
            days=args.days
        )


if __name__ == "__main__":
    main()
