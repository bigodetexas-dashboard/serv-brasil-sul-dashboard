import os
import sys
import time
import random
import logging
import sqlite3
from datetime import datetime

# Configura o path para importar módulos do projeto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from repositories.player_repository import PlayerRepository
from repositories.clan_repository import ClanRepository
from repositories.item_repository import ItemRepository

# Configuração de Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("stress_test.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

DB_FILE = "bigode_unified.db"


def get_db():
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f"Erro de conexão DB: {e}")
        return None


class StressTest:
    def __init__(self):
        self.player_repo = PlayerRepository()
        self.clan_repo = ClanRepository()
        self.item_repo = ItemRepository()  # Assumindo que existe ou simularemos
        self.mock_users = []
        self.clans = []

    def setup_database(self):
        """Prepara o banco de dados limpando dados de teste anteriores"""
        logger.info("Preparando ambiente de teste (Limpando dados antigos)...")
        conn = get_db()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            # Limpa clãs de teste
            cursor.execute("DELETE FROM clans WHERE name LIKE 'Clan_Test_%'")
            # Limpa usuários de teste
            cursor.execute("DELETE FROM users WHERE discord_id LIKE 'test_user_%'")
            conn.commit()
            logger.info("Limpeza de dados de teste concluída.")
        except Exception as e:
            logger.error(f"Erro ao limpar banco de dados: {e}")
        finally:
            conn.close()

    def create_mock_users(self, count=20):
        """Simula a entrada de novos jogadores"""
        logger.info(f"Simulando registro de {count} jogadores...")
        start_time = time.time()

        for i in range(count):
            discord_id = f"test_user_{i}_{int(time.time())}"
            name = f"Survivor_{i}"
            gamertag = f"Gamer_{i}"

            # 1. Registrar Usuário e Gamertag (Implicitamente cria user)
            # O repositório cria o usuário se não existir ao definir a gamertag
            self.player_repo.set_gamertag(discord_id, gamertag)

            self.mock_users.append(
                {"id": discord_id, "name": name, "gamertag": gamertag}
            )
            time.sleep(0.05)  # Yield to avoid DB lock

        elapsed = time.time() - start_time
        logger.info(f"Criação de usuários concluída em {elapsed:.4f}s")

    def simulate_economy(self):
        """Simula fluxo intenso de economia"""
        logger.info(
            "Iniciando simulação de economia (Daily + Transferências + Compras)..."
        )
        start_time = time.time()

        for user in self.mock_users:
            uid = user["id"]

            # 1. Resgatar Daily
            # Simula a lógica do comando !daily
            bonus = random.randint(100, 5000)
            self.player_repo.update_balance(uid, bonus, "Stress Test Daily")
            logger.debug(f"User {uid} recebeu daily: {bonus}")

            # 2. Transferência para outro usuário aleatório
            if len(self.mock_users) > 1:
                target = random.choice(self.mock_users)
                if target["id"] != uid:
                    amount = random.randint(10, 100)
                    # Verifica saldo antes (lógica do bot)
                    saldo = self.player_repo.get_balance(uid)
                    if saldo >= amount:
                        self.player_repo.update_balance(uid, -amount, "Transfer Out")
                        self.player_repo.update_balance(
                            target["id"], amount, "Transfer In"
                        )
                        logger.debug(
                            f"Transferência: {uid} -> {target['id']} ({amount})"
                        )

            # 3. Compra de Item (Simulada)
            price = random.randint(50, 200)
            saldo = self.player_repo.get_balance(uid)
            if saldo >= price:
                self.player_repo.update_balance(uid, -price, "Shop Purchase")
                # Opcional: Adicionar ao inventário se houver método
                # self.item_repo.add_to_inventory(uid, "apple", 1) # Assumindo que ItemRepository tem isso ou PlayerRepository
                logger.debug(f"User {uid} comprou item valor {price}")

            time.sleep(0.05)  # Yield to avoid DB lock

        elapsed = time.time() - start_time
        logger.info(f"Simulação econômica concluída em {elapsed:.4f}s")

    def simulate_clans(self):
        """Simula criação e gestão de clãs"""
        logger.info("Simulando operações de clã (Criação + Convites + Join)...")
        start_time = time.time()

        # Vamos criar 4 clãs (aprox 5 membros cada)
        clan_leaders = self.mock_users[:4]
        other_users = self.mock_users[4:]

        for i, leader in enumerate(clan_leaders):
            clan_name = f"Clan_Test_{i}"
            leader_id = leader["id"]

            # 1. Criar Clã
            # Verifica se já tem clã
            existing = self.clan_repo.get_user_clan(leader_id)
            if not existing:
                clan_id = self.clan_repo.create_clan(clan_name, leader_id)
                if clan_id:
                    logger.debug(
                        f"Clã {clan_name} criado por {leader_id} (ID: {clan_id})"
                    )
                    self.clans.append(clan_name)
                else:
                    logger.error(f"Falha ao criar clã {clan_name}")

            time.sleep(0.05)  # Yield to avoid DB lock

        # 2. Adicionar membros
        # Distribuir users restantes nos clãs
        if self.clans:
            for user in other_users:
                target_clan_name = random.choice(self.clans)
                clan_data = self.clan_repo.get_clan_by_tag(
                    target_clan_name
                )  # Fix: get_clan_by_tag

                if clan_data:
                    # Simula fluxo correto: Invite -> Respond
                    # 1. Leader cria invite
                    leader_id = clan_data["leader_discord_id"]
                    if self.clan_repo.create_invite(clan_data["id"], user["id"]):
                        logger.debug(
                            f"Invite criado: {leader_id} -> {user['id']} (Clan: {target_clan_name})"
                        )

                        # 2. User aceita (recupera ID do invite)
                        invites = self.clan_repo.get_user_invites(user["id"])
                        if invites:
                            invite_id = invites[0]["id"]
                            if self.clan_repo.respond_invite(invite_id, accept=True):
                                logger.debug(
                                    f"User {user['id']} entrou no clã {target_clan_name}"
                                )
                            else:
                                logger.error(f"Falha ao aceitar invite {invite_id}")
                    else:
                        logger.error(f"Falha ao criar invite para {user['id']}")

                time.sleep(0.05)  # Yield to avoid DB lock

        elapsed = time.time() - start_time
        logger.info(f"Simulação de clãs concluída em {elapsed:.4f}s")

    def simulate_bases(self):
        """Simula registro de 7 bases"""
        logger.info("Simulando registro de 7 bases...")
        start_time = time.time()

        # Seleciona 7 usuários aleatórios
        builders = random.sample(self.mock_users, 7)

        for i, builder in enumerate(builders):
            # Coordenadas aleatórias no mapa (Chernarus: 0-15360)
            x = random.uniform(1000.0, 14000.0)
            z = random.uniform(1000.0, 14000.0)
            # Y geralmente não é validado estritamente no DB, mas simulamos algo realista
            y = 100.0

            name = f"Base Test {i}"
            radius = 50.0

            # Registra base usando PlayerRepository.add_base
            success, msg = self.player_repo.add_base(
                builder["id"], x, y, z, name, radius
            )

            if success:
                logger.debug(
                    f"Base registrada por {builder['id']} em ({x:.1f}, {z:.1f})"
                )
            else:
                logger.warning(f"Falha ao registrar base para {builder['id']}: {msg}")

            time.sleep(0.05)  # Yield to avoid DB lock

        elapsed = time.time() - start_time
        logger.info(f"Registro de bases concluído em {elapsed:.4f}s")

    def check_integrity(self):
        """Verifica integridade dos dados pós-teste"""
        logger.info("Verificando integridade e consistência dos dados...")

        # 1. Verificar saldos negativos
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT discord_id, balance FROM users WHERE balance < 0")
        negatives = cursor.fetchall()

        if negatives:
            logger.error(
                f"ALERTA DE SEGURANÇA: {len(negatives)} usuários com saldo negativo!"
            )
            for n in negatives:
                logger.error(f"User {n[0]}: {n[1]}")
        else:
            logger.info("Integridade de saldo: OK (Nenhum saldo negativo)")

        conn.close()

    def run(self):
        print("=== INICIANDO STRESS TEST ===")
        print(f"Horário: {datetime.now()}")

        conn = None
        try:
            # Estabelecer conexão compartilhada para o teste
            conn = get_db()
            if conn:
                logger.info(
                    "Ativando modo de conexão compartilhada (High Performance)..."
                )
                self.player_repo.set_shared_connection(conn)
                self.clan_repo.set_shared_connection(conn)
                self.item_repo.set_shared_connection(conn)

            self.setup_database()
            self.create_mock_users(20)
            self.simulate_economy()
            self.simulate_clans()
            self.simulate_bases()

            # Fechar conexão compartilhada antes de checks finais
            if conn:
                conn.close()
                conn = None
                logger.info("Conexão compartilhada encerrada.")

            self.check_integrity()

            print("\n=== TESTE CONCLUÍDO COM SUCESSO ===")
            print("Verifique stress_test.log para detalhes.")

        except Exception as e:
            logger.error(f"Erro fatal durante o teste: {e}", exc_info=True)
            print(f"\n[ERRO CRITICO]: {e}")
        finally:
            if conn:
                conn.close()


if __name__ == "__main__":
    # Garante que os prints apareçam imediatamente no console
    sys.stdout.reconfigure(line_buffering=True)
    try:
        test = StressTest()
        test.run()
        # Força o encerramento explícito do processo
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Erro fatal na execução principal: {e}", exc_info=True)
        print(f"ERRO FATAL: {e}")
        sys.exit(1)
