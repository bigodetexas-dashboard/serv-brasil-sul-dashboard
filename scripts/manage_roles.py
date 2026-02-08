# -*- coding: utf-8 -*-
"""
Script de Gerenciamento de Roles (RBAC)
BigodeTexas v2.3
"""
import sys
import os
import sqlite3

# Adicionar raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database

# Cores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")


def print_ok(text):
    print(f"{Colors.GREEN}[OK]{Colors.RESET} {text}")


def print_error(text):
    print(f"{Colors.RED}[ERRO]{Colors.RESET} {text}")


def print_info(text):
    print(f"{Colors.CYAN}[INFO]{Colors.RESET} {text}")


def list_users():
    """Lista todos os usuários e suas roles"""
    print_header("LISTA DE USUARIOS E ROLES")

    conn = database.get_connection()
    if not conn:
        print_error("Erro ao conectar ao banco de dados")
        return

    try:
        cur = conn.cursor()

        # Buscar usuários com role
        cur.execute("""
            SELECT discord_id, gamertag, role, is_banned
            FROM users
            ORDER BY role, gamertag
        """)

        users = cur.fetchall()
        conn.close()

        if not users:
            print_info("Nenhum usuário cadastrado")
            return

        print(f"Total de usuários: {len(users)}\n")

        # Agrupar por role
        roles_count = {"admin": 0, "moderator": 0, "user": 0, "banned": 0}
        users_by_role = {"admin": [], "moderator": [], "user": [], "banned": []}

        for discord_id, gamertag, role, is_banned in users:
            if not role:
                role = "user"  # Default

            roles_count[role] = roles_count.get(role, 0) + 1
            users_by_role.setdefault(role, []).append((discord_id, gamertag, is_banned))

        # Exibir estatísticas
        print(f"{Colors.BOLD}Estatísticas:{Colors.RESET}")
        print(f"  🔴 Admins:      {roles_count.get('admin', 0)}")
        print(f"  🟡 Moderators:  {roles_count.get('moderator', 0)}")
        print(f"  🟢 Users:       {roles_count.get('user', 0)}")
        print(f"  ⚫ Banned:      {roles_count.get('banned', 0)}")
        print()

        # Exibir usuários por role
        for role in ["admin", "moderator", "user", "banned"]:
            if users_by_role.get(role):
                role_emoji = {
                    "admin": "🔴",
                    "moderator": "🟡",
                    "user": "🟢",
                    "banned": "⚫"
                }
                print(f"{role_emoji[role]} {Colors.BOLD}{role.upper()}:{Colors.RESET}")

                for discord_id, gamertag, is_banned in users_by_role[role]:
                    banned_indicator = f" {Colors.RED}[BANIDO]{Colors.RESET}" if is_banned else ""
                    print(f"  - {gamertag or 'N/A'} ({discord_id}){banned_indicator}")

                print()

    except Exception as e:
        print_error(f"Erro ao listar usuários: {e}")
        if conn:
            conn.close()


def set_role(discord_id, new_role):
    """Atribui uma role a um usuário"""
    valid_roles = ["admin", "moderator", "user", "banned"]

    if new_role not in valid_roles:
        print_error(f"Role inválida! Use uma das seguintes: {', '.join(valid_roles)}")
        return False

    conn = database.get_connection()
    if not conn:
        print_error("Erro ao conectar ao banco de dados")
        return False

    try:
        cur = conn.cursor()

        # Verificar se usuário existe
        cur.execute("SELECT gamertag FROM users WHERE discord_id = ?", (discord_id,))
        user = cur.fetchone()

        if not user:
            print_error(f"Usuário com Discord ID '{discord_id}' não encontrado")
            conn.close()
            return False

        gamertag = user[0]

        # Atualizar role
        cur.execute("""
            UPDATE users
            SET role = ?
            WHERE discord_id = ?
        """, (new_role, discord_id))

        # Se role for 'banned', marcar is_banned
        if new_role == "banned":
            cur.execute("""
                UPDATE users
                SET is_banned = 1
                WHERE discord_id = ?
            """, (discord_id,))

        conn.commit()
        conn.close()

        print_ok(f"Role de '{gamertag}' ({discord_id}) alterada para: {Colors.BOLD}{new_role.upper()}{Colors.RESET}")
        return True

    except Exception as e:
        print_error(f"Erro ao atribuir role: {e}")
        if conn:
            conn.close()
        return False


def ban_user(discord_id, reason="Violação de regras"):
    """Bane um usuário"""
    conn = database.get_connection()
    if not conn:
        print_error("Erro ao conectar ao banco de dados")
        return False

    try:
        cur = conn.cursor()

        # Verificar se usuário existe
        cur.execute("SELECT gamertag FROM users WHERE discord_id = ?", (discord_id,))
        user = cur.fetchone()

        if not user:
            print_error(f"Usuário com Discord ID '{discord_id}' não encontrado")
            conn.close()
            return False

        gamertag = user[0]

        # Banir usuário
        cur.execute("""
            UPDATE users
            SET is_banned = 1, role = 'banned', ban_reason = ?
            WHERE discord_id = ?
        """, (reason, discord_id))

        conn.commit()
        conn.close()

        print_ok(f"Usuário '{gamertag}' ({discord_id}) foi {Colors.RED}BANIDO{Colors.RESET}")
        print_info(f"Razão: {reason}")
        return True

    except Exception as e:
        print_error(f"Erro ao banir usuário: {e}")
        if conn:
            conn.close()
        return False


def unban_user(discord_id):
    """Remove o ban de um usuário"""
    conn = database.get_connection()
    if not conn:
        print_error("Erro ao conectar ao banco de dados")
        return False

    try:
        cur = conn.cursor()

        # Verificar se usuário existe
        cur.execute("SELECT gamertag FROM users WHERE discord_id = ?", (discord_id,))
        user = cur.fetchone()

        if not user:
            print_error(f"Usuário com Discord ID '{discord_id}' não encontrado")
            conn.close()
            return False

        gamertag = user[0]

        # Desbanir usuário
        cur.execute("""
            UPDATE users
            SET is_banned = 0, role = 'user', ban_reason = NULL
            WHERE discord_id = ?
        """, (discord_id,))

        conn.commit()
        conn.close()

        print_ok(f"Usuário '{gamertag}' ({discord_id}) foi {Colors.GREEN}DESBANIDO{Colors.RESET}")
        return True

    except Exception as e:
        print_error(f"Erro ao desbanir usuário: {e}")
        if conn:
            conn.close()
        return False


def show_help():
    """Exibe ajuda do script"""
    print_header("GERENCIAMENTO DE ROLES - BIGODETEXAS")

    print(f"{Colors.BOLD}Uso:{Colors.RESET}")
    print(f"  python manage_roles.py [comando] [argumentos]\n")

    print(f"{Colors.BOLD}Comandos disponíveis:{Colors.RESET}\n")

    print(f"  {Colors.CYAN}list{Colors.RESET}")
    print(f"    Lista todos os usuários e suas roles\n")

    print(f"  {Colors.CYAN}set <discord_id> <role>{Colors.RESET}")
    print(f"    Atribui uma role a um usuário")
    print(f"    Roles válidas: admin, moderator, user, banned")
    print(f"    Exemplo: python manage_roles.py set 123456789 admin\n")

    print(f"  {Colors.CYAN}ban <discord_id> [razão]{Colors.RESET}")
    print(f"    Bane um usuário")
    print(f"    Exemplo: python manage_roles.py ban 123456789 \"Uso de cheats\"\n")

    print(f"  {Colors.CYAN}unban <discord_id>{Colors.RESET}")
    print(f"    Remove o ban de um usuário")
    print(f"    Exemplo: python manage_roles.py unban 123456789\n")

    print(f"  {Colors.CYAN}help{Colors.RESET}")
    print(f"    Exibe esta mensagem de ajuda\n")


def main():
    """Função principal"""
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    if command == "list":
        list_users()

    elif command == "set":
        if len(sys.argv) < 4:
            print_error("Uso: python manage_roles.py set <discord_id> <role>")
            return

        discord_id = sys.argv[2]
        role = sys.argv[3].lower()
        set_role(discord_id, role)

    elif command == "ban":
        if len(sys.argv) < 3:
            print_error("Uso: python manage_roles.py ban <discord_id> [razão]")
            return

        discord_id = sys.argv[2]
        reason = sys.argv[3] if len(sys.argv) > 3 else "Violação de regras"
        ban_user(discord_id, reason)

    elif command == "unban":
        if len(sys.argv) < 3:
            print_error("Uso: python manage_roles.py unban <discord_id>")
            return

        discord_id = sys.argv[2]
        unban_user(discord_id)

    elif command == "help":
        show_help()

    else:
        print_error(f"Comando desconhecido: {command}")
        print_info("Use 'python manage_roles.py help' para ver comandos disponíveis")


if __name__ == "__main__":
    main()
