import os
import sys
import asyncio
import discord
import sqlite3
from ftplib import FTP
from dotenv import load_dotenv

# Load env from parent dir
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

results = {"discord": False, "nitrado": False, "database": False}

print("diagnose_start")


async def check_discord():
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ [DISCORD] Token não encontrado no .env")
        return

    client = discord.Client(intents=discord.Intents.default())

    try:
        print(
            f"⏳ [DISCORD] Testando conexão com Token... (pode levar alguns segundos)"
        )
        await client.login(token)
        print(f"✅ [DISCORD] Conectado e autenticado! (Bot ID: {client.user.id})")
        results["discord"] = True
        await client.close()
    except Exception as e:
        print(f"❌ [DISCORD] Falha na conexão: {e}")


def check_nitrado():
    host = os.getenv("FTP_HOST")
    user = os.getenv("FTP_USER")
    passwd = os.getenv("FTP_PASS")
    port = int(os.getenv("FTP_PORT", 21))

    if not host or not user:
        print("❌ [NITRADO] Credenciais FTP incompletas.")
        return

    try:
        print(f"⏳ [NITRADO] Conectando ao FTP ({host})...")
        ftp = FTP()
        ftp.connect(host, port, timeout=10)
        ftp.login(user, passwd)
        print(f"✅ [NITRADO] Conexão FTP estabelecida com sucesso!")
        files = ftp.nlst()
        print(f"   📂 Arquivos na raiz: {len(files)}")
        ftp.quit()
        results["nitrado"] = True
    except Exception as e:
        print(f"❌ [NITRADO] Falha no FTP: {e}")


def check_database():
    db_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "bigode_unified.db"
    )
    try:
        if not os.path.exists(db_path):
            print(f"❌ [DATABASE] Arquivo não encontrado: {db_path}")
            return

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cur.fetchall()
        print(f"✅ [DATABASE] Conexão SQLite OK! ({len(tables)} tabelas encontradas)")
        conn.close()
        results["database"] = True
    except Exception as e:
        print(f"❌ [DATABASE] Erro ao abrir banco: {e}")


async def main():
    print("=" * 40)
    print("DIAGNOSTICO DE SISTEMA - BIGODETEXAS")
    print("=" * 40)

    check_database()
    print("-" * 40)
    check_nitrado()
    print("-" * 40)
    await check_discord()

    print("=" * 40)
    if all(results.values()):
        print("STATUS GLOBAL: TUDO ONLINE! SISTEMA OPERACIONAL.")
    else:
        print("STATUS GLOBAL: ALGUNS SISTEMAS ESTAO OFF.")


if __name__ == "__main__":
    asyncio.run(main())
