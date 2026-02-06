import os
from google import genai
import json
import asyncio
import random

# --- CONFIGURAÇÃO MULTI-KEY ---
# Pega todas as chaves separadas por vírgula
raw_keys = os.getenv("GEMINI_API_KEY", "")
API_KEYS = [k.strip() for k in raw_keys.split(",") if k.strip()]

clients = []
current_key_index = 0

if API_KEYS:
    print(f"[AI] Carregando {len(API_KEYS)} chaves de API...")
    for key in API_KEYS:
        try:
            # Inicializa um cliente para cada chave
            client = genai.Client(api_key=key)
            clients.append(client)
        except Exception as e:
            print(f"[AI] Falha ao carregar chave {key[:10]}...: {e}")

    if clients:
        pass_key_check = True
        print(f"[AI] Total de {len(clients)} clientes Google ativos com sucesso.")
    else:
        pass_key_check = False
        print("[AI] ERRO CRITICO: Nenhuma chave valida carregada.")
else:
    pass_key_check = False
    print("[AI] Nenhuma chave encontrada no .env")

# Modelo recomendado
MODEL_NAME = "models/gemini-flash-latest"


def get_next_client():
    """Retorna o próximo cliente da lista (Round Robin simples)."""
    global current_key_index
    if not clients:
        return None

    # Pega o atual
    client = clients[current_key_index]

    # Avança o índice para a próxima chamada
    current_key_index = (current_key_index + 1) % len(clients)

    return client


def switch_key_force():
    """Força a troca da chave atual (usado em caso de erro)."""
    global current_key_index
    if not clients:
        return
    prev = current_key_index
    current_key_index = (current_key_index + 1) % len(clients)
    print(f"🔄 [AI] Rotação Forçada: Key {prev} -> Key {current_key_index}")


# --- HELPER DE SEGURANÇA ---
def sanitize_input(text):
    if not text:
        return ""
    if len(text) > 1000:
        text = text[:1000] + "... (cortado)"
    return text.replace("```", "'''").replace("`", "'").strip()


# --- PROMPTS ---
SYSTEM_PROMPT = """
Você é o 'BigodeAI', assistente oficial do servidor DayZ Xbox 'BigodeTexas'.
Contexto do Servidor:
- Mapa: Chernarus (versão inverno/editada).
- Estilo: PvP com zonas seguras, Factions, Economia com DZ Coins.
- Regras principais: Sem glitch de base, sem off-limits, respeito no chat.
- Moeda: DZ Coins.
- Plataforma: Xbox.

Sua personalidade:
- Utilitário, direto, mas com um toque de humor 'sobrevivente'.
- Não invente regras que não existem. Se não souber, sugira abrir ticket.
- Use emojis moderadamente.
"""


async def ask_gemini(question, context_data=None):
    """
    Responde perguntas usando Rotação de Chaves Automática.
    """
    if not pass_key_check or not clients:
        return "🚫 **Erro de Configuração:** Nenhuma chave de API válida."

    # Tenta usar a chave atual
    client = get_next_client()

    # Se falhar, tentaremos com as outras chaves disponíveis (até o número total de chaves)
    attempts = len(clients)

    last_error = ""

    # Prepara o prompt uma vez
    if context_data and "[CONTEXTO TÉCNICO AVANÇADO]" in context_data:
        full_prompt = context_data
    else:
        safe_question = sanitize_input(question)
        safe_context = (
            sanitize_input(context_data) if context_data else "Nenhum dado extra."
        )
        full_prompt = (
            f"{SYSTEM_PROMPT}\n[CONTEXTO]\n{safe_context}\n[PERGUNTA]\n{safe_question}"
        )

    for i in range(attempts):
        try:
            response = await asyncio.to_thread(
                client.models.generate_content, model=MODEL_NAME, contents=full_prompt
            )

            if response and response.text:
                return response.text
            else:
                raise ValueError("Resposta vazia da IA")

        except Exception as e:
            error_msg = str(e)
            last_error = error_msg

            # Se for erro de COTA (429), troca a chave e tenta de novo
            if (
                "429" in error_msg
                or "quota" in error_msg.lower()
                or "resource_exhausted" in error_msg.lower()
            ):
                print(f"⚠️ [AI] Cota atingida na chave atual. Trocando...")
                switch_key_force()
                client = get_next_client()  # Pega a nova chave para o próximo loop
                continue  # Tenta de novo no loop

            # Se for outro erro, apenas loga e tenta o próximo por garantia
            print(f"⚠️ [AI] Erro na tentativa {i + 1}: {error_msg}")
            client = get_next_client()

    return f"⚠️ Falha em todas as chaves de IA. Último erro: {last_error[:100]}"


async def generate_event_idea():
    """Gera eventos (com suporte a rotação)."""
    if not pass_key_check:
        return None

    try:
        client = get_next_client()
        prompt = "Gere ideia de evento DayZ. JSON: {title, description, location, reward, difficulty}."

        response = await asyncio.to_thread(
            client.models.generate_content, model=MODEL_NAME, contents=prompt
        )
        # ... (Logica de JSON parsing simplificada aqui) ...
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception:
        return None


async def analyze_behavior(log_lines):
    """Analisa logs (com suporte a rotação)."""
    if not pass_key_check:
        return "Erro config AI."

    try:
        client = get_next_client()
        safe_logs = "\n".join([l[:100] for l in log_lines[:20]])
        prompt = f"Analise logs suspeitos DayZ:\n{safe_logs}"

        response = await asyncio.to_thread(
            client.models.generate_content, model=MODEL_NAME, contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Erro análise: {e}"
