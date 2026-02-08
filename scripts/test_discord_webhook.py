# -*- coding: utf-8 -*-
"""
Script de Teste - Webhook Discord
Testa se o webhook está configurado corretamente e envia mensagem de teste.
"""
import os
import sys
import requests
from datetime import datetime
from dotenv import load_dotenv

# Adicionar raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar UTF-8 no Windows
if sys.platform == "win32":
    import codecs
    if hasattr(sys.stdout, 'detach'):
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

load_dotenv()


def test_webhook():
    """Testa webhook Discord com mensagem de exemplo"""

    webhook_url = os.getenv("NOTIFICATION_WEBHOOK_URL")

    print("=" * 60)
    print("TESTE DE WEBHOOK DISCORD - BigodeTexas")
    print("=" * 60)

    # Verificar se está configurado
    if not webhook_url or webhook_url == "seu_webhook_url_aqui":
        print("\n[X] WEBHOOK NAO CONFIGURADO!")
        print("\nCOMO CONFIGURAR:\n")
        print("1. Abra o Discord")
        print("2. Va ate o canal onde deseja receber notificacoes")
        print("3. Clique na engrenagem (Editar Canal)")
        print("4. Va em 'Integracoes' > 'Webhooks'")
        print("5. Clique em 'Criar Webhook' ou 'Novo Webhook'")
        print("6. De um nome (ex: 'BigodeTexas Anti-Cheat')")
        print("7. Copie a URL do Webhook")
        print("8. Edite o arquivo .env e cole a URL em:")
        print("   NOTIFICATION_WEBHOOK_URL=<sua_url_aqui>")
        print("\nExemplo de URL:")
        print("   https://discord.com/api/webhooks/123456789/abcdefghijklmnop")
        return False

    print(f"\n[OK] Webhook encontrado!")
    print(f"URL: {webhook_url[:50]}...")

    # Criar mensagem de teste
    embed = {
        "title": "TESTE DE WEBHOOK - Sistema Anti-Cheat",
        "description": "**Webhook configurado com sucesso!**\n\nO sistema está pronto para enviar notificações automáticas.",
        "color": 0x00FF00,  # Verde
        "fields": [
            {
                "name": "Sistema",
                "value": "BigodeTexas Auto-Ban",
                "inline": True
            },
            {
                "name": "Data",
                "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "inline": True
            },
            {
                "name": "Notificacoes Ativas",
                "value": "• Banimentos automaticos\n• Infracoes detectadas\n• Alt accounts\n• Invasoes de territorio",
                "inline": False
            }
        ],
        "footer": {
            "text": "Sistema Anti-Cheat BigodeTexas | Modo Autonomo"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

    payload = {
        "username": "Sistema Anti-Cheat",
        "avatar_url": "https://i.imgur.com/S71j4qO.png",
        "embeds": [embed]
    }

    try:
        print("\nEnviando mensagem de teste...")
        response = requests.post(webhook_url, json=payload, timeout=10)

        if response.status_code == 204:
            print("\n[OK] WEBHOOK FUNCIONANDO PERFEITAMENTE!")
            print("Mensagem de teste enviada ao Discord!")
            print("\nVerifique o canal do Discord para ver a mensagem.")
            return True
        else:
            print(f"\n[ERRO] Status {response.status_code}")
            print(f"Resposta: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("\n[ERRO] TIMEOUT: Webhook demorou muito para responder")
        print("Verifique sua conexao com a internet")
        return False

    except requests.exceptions.RequestException as e:
        print(f"\n[ERRO] CONEXAO: {e}")
        print("\nPossiveis causas:")
        print("• URL do webhook invalida")
        print("• Webhook foi deletado no Discord")
        print("• Problemas de conexao com a internet")
        return False


def send_test_ban_notification():
    """Envia notificação de ban de teste (exemplo visual)"""

    webhook_url = os.getenv("NOTIFICATION_WEBHOOK_URL")

    if not webhook_url or webhook_url == "seu_webhook_url_aqui":
        print("\n[AVISO] Configure o webhook primeiro!")
        return False

    print("\n" + "=" * 60)
    print("ENVIANDO NOTIFICACAO DE BAN DE TESTE")
    print("=" * 60)

    # Simular notificação de banimento
    embed = {
        "title": "BANIMENTO AUTOMATICO (TESTE)",
        "description": "**TestPlayer123** foi banido automaticamente do servidor!",
        "color": 0xFF0000,  # Vermelho
        "fields": [
            {
                "name": "Jogador",
                "value": "**TestPlayer123**",
                "inline": True
            },
            {
                "name": "XUID",
                "value": "1234567890123456",
                "inline": True
            },
            {
                "name": "Severidade",
                "value": "**CRITICA**",
                "inline": True
            },
            {
                "name": "Infracao",
                "value": "`fly_hack`",
                "inline": False
            },
            {
                "name": "Motivo",
                "value": "Fly Hack Detectado: Kill em altura ilegal (teste)",
                "inline": False
            },
            {
                "name": "Evidencia",
                "value": "```Coordenadas: X=5000, Y=500, Z=3000\nAltura: 500m (limite: 120m)```",
                "inline": False
            }
        ],
        "footer": {
            "text": "ID da Infracao: 999 | Sistema Anti-Cheat BigodeTexas (TESTE)"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

    payload = {
        "username": "Sistema Anti-Cheat",
        "avatar_url": "https://i.imgur.com/S71j4qO.png",
        "embeds": [embed]
    }

    try:
        response = requests.post(webhook_url, json=payload, timeout=10)

        if response.status_code == 204:
            print("\n[OK] Notificacao de TESTE enviada!")
            print("Verifique o Discord para ver como as notificacoes aparecerao.")
            return True
        else:
            print(f"\n[ERRO] Status {response.status_code}")
            return False

    except Exception as e:
        print(f"\n[ERRO] {e}")
        return False


if __name__ == "__main__":
    print("\n[TESTE] WEBHOOK DISCORD\n")

    # Teste básico
    success = test_webhook()

    # Se funcionou, perguntar se quer enviar exemplo de ban
    if success:
        print("\n" + "-" * 60)
        try:
            input("\nPressione ENTER para enviar um exemplo de notificacao de BAN...")
            send_test_ban_notification()
        except:
            pass

    print("\n" + "=" * 60)
    print("TESTE CONCLUIDO")
    print("=" * 60)
