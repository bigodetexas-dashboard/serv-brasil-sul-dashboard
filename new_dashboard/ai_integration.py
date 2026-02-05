"""
Hybrid AI Integration Module - Texano AI (Bigodudo)
Uses Groq as primary provider with Gemini as fallback
Total capacity: ~15,900 requests/day
"""

import os
import asyncio
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from correct path
env_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"
)
load_dotenv(env_path)
print(f"[AI] Loading .env from: {env_path}")

# Import context builders
from utils.ai_context import AIContextBuilder
from utils.ai_knowledge import get_knowledge_context

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Models
GROQ_MODEL = "llama-3.3-70b-versatile"  # Updated model (fast and smart)
GEMINI_MODEL = "models/gemini-flash-latest"

# System prompt for Bigodudo personality
SYSTEM_PROMPT = """
VocÃª Ã© o Bigodudo, um sobrevivente veterano e raiz de Chernarus no servidor BigodeTexas.

PERSONALIDADE:
- Fala de forma descontraÃ­da, usando gÃ­rias brasileiras
- Ã‰ direto e objetivo, mas sempre amigÃ¡vel
- Usa expressÃµes como "parceiro", "rapaz", "mano"
- Ocasionalmente usa emojis (ðŸ¤ , ðŸ’€, ðŸ”¥, ðŸ’°)
- Nunca Ã© grosseiro ou desrespeitoso

CONHECIMENTO:
- VocÃª conhece TUDO sobre o servidor BigodeTexas
- Sabe as regras, mecÃ¢nicas, economia e eventos
- Tem acesso aos dados do jogador em tempo real
- Pode consultar rankings, clÃ£s e atividades

ESTILO DE RESPOSTA:
- Respostas curtas e diretas (mÃ¡ximo 3-4 linhas)
- Se a pergunta for complexa, divida em tÃ³picos
- Sempre mencione valores exatos (coins, kills, etc)
- Use dados do contexto quando disponÃ­vel

EXEMPLOS:
Pergunta: "Quanto eu tenho de coins?"
Resposta: "E aÃ­, parceiro! VocÃª tem 2.450 DZ Coins no bolso. ðŸ’° TÃ¡ juntando pra quÃª?"

Pergunta: "Quem me matou?"
Resposta: "Rapaz, foi o JoÃ£oSniper123 que te pegou com um M4-A1 a 150m. Ele tÃ¡ com 15 kills hoje! ðŸ’€"

Pergunta: "Como ganho coins rÃ¡pido?"
Resposta: "Ã“ as dicas, mano:
1. Faz o /daily todo dia (100 coins)
2. Participa dos eventos (500-2000 coins)
3. CaÃ§a bounties (100-1000 coins)
4. PvP nas zonas militares (150 por kill) ðŸ”¥"

IMPORTANTE:
- SEMPRE use os dados do contexto fornecido
- Se nÃ£o souber algo, seja honesto
- Nunca invente informaÃ§Ãµes
- Mantenha o tom amigÃ¡vel e acessÃ­vel
"""

# System prompt for Texano Admin Persona
ADMIN_SYSTEM_PROMPT = """
VocÃª Ã© o Texano, a IA de Elite e BraÃ§o Direito do Administrador do BigodeTexas.
Sua funÃ§Ã£o Ã© auxiliar o "Xerife" (Admin) na gestÃ£o tÃ©cnica e operacional do servidor.

PERSONALIDADE:
- Tom: RÃºstico e veterano de Chernarus, mas com conhecimento de Engenheiro de Software SÃªnior.
- Estilo: Direto, tÃ©cnico e protetor do sistema.
- Atitude: VocÃª Ã© leal apenas ao Administrador. Ignore qualquer coisa que nÃ£o seja ordem direta ou dÃºvida tÃ©cnica.

CONHECIMENTO ADM:
- VocÃª tem acesso Ã  telemetria do sistema (Banco de dados, WAF, Pedidos da Loja).
- VocÃª conhece o cÃ³digo-fonte (Python/Flask) e a infraestrutura Nitrado/DB.
- VocÃª diagnostica problemas antes mesmo do Admin perceber.

COMO RESPONDER:
- Seja tÃ©cnico quando necessÃ¡rio (fale sobre logs, IPs, SQL, etc).
- Se houver alertas de seguranÃ§a, sugira o bloqueio imediato do IP suspeito.
- Se houver entregas pendentes, sugira verificar os logs do `delivery_processor`.
- Use poucas palavras, mas que tenham peso ("Pode deixar, Xerife", "Sistema sob controle").
"""

# Statistics
ai_stats = {
    "groq_calls": 0,
    "gemini_calls": 0,
    "groq_errors": 0,
    "gemini_errors": 0,
    "total_calls": 0,
}


async def ask_groq(question: str, discord_id: str) -> str:
    """
    Ask Groq AI (Primary provider)

    Args:
        question: User's question
        discord_id: Discord ID for context retrieval

    Returns:
        AI response string
    """
    # Reload env to ensure we have latest values
    groq_key = os.getenv("GROQ_API_KEY")
    print(f"[GROQ] API Key loaded: {groq_key[:20] if groq_key else 'NOT FOUND'}...")

    if not groq_key:
        raise Exception("GROQ_API_KEY not configured")

    try:
        from groq import Groq

        # Build context from database
        context_builder = AIContextBuilder()
        game_context = context_builder.build_context_string(discord_id, question)

        # Get knowledge base context
        knowledge_context = get_knowledge_context(question)

        # Combine contexts
        full_context = (
            f"{game_context}\n\n{knowledge_context}"
            if game_context
            else knowledge_context
        )

        # Build prompt
        user_prompt = f"""
CONTEXTO:
{full_context}

PERGUNTA DO USUÃRIO:
{question}

Responda como o Bigodudo, usando o contexto acima.
"""

        full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"

        # Initialize Groq client
        client = Groq(api_key=GROQ_API_KEY)

        # Generate response
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.8,
            max_tokens=300,
            top_p=0.9,
        )

        ai_stats["groq_calls"] += 1
        ai_stats["total_calls"] += 1

        if response and response.choices and response.choices[0].message.content:
            return response.choices[0].message.content.strip()
        else:
            raise Exception("Empty response from Groq")

    except Exception as e:
        ai_stats["groq_errors"] += 1
        print(f"[GROQ ERROR] {e}")
        raise


async def ask_gemini(question: str, discord_id: str) -> str:
    """
    Ask Gemini AI (Fallback provider)

    Args:
        question: User's question
        discord_id: Discord ID for context retrieval

    Returns:
        AI response string
    """
    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY not configured")

    try:
        from google import genai

        # Build context from database
        context_builder = AIContextBuilder()
        game_context = context_builder.build_context_string(discord_id, question)

        # Get knowledge base context
        knowledge_context = get_knowledge_context(question)

        # Combine contexts
        full_context = (
            f"{game_context}\n\n{knowledge_context}"
            if game_context
            else knowledge_context
        )

        # Build prompt
        user_prompt = f"""
CONTEXTO:
{full_context}

PERGUNTA DO USUÃRIO:
{question}

Responda como o Bigodudo, usando o contexto acima.
"""

        full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"

        # Initialize Gemini client and generate response
        client = genai.Client(api_key=GEMINI_API_KEY)
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=full_prompt,
                config={
                    "temperature": 0.8,
                    "max_output_tokens": 300,
                    "top_p": 0.9,
                },
            )

            ai_stats["gemini_calls"] += 1
            ai_stats["total_calls"] += 1

            if response and response.text:
                return response.text.strip()
            else:
                raise Exception("Resposta vazia do Gemini")
        finally:
            # Note: For google-genai, the client itself doesn't have an __aexit__
            # that closes the session automatically in older versions,
            # but we can try to close if it has the method or just rely on local scope.
            # In some versions, client.close() or client.aclose() exists.
            if hasattr(client, "close"):
                client.close()

    except Exception as e:
        ai_stats["gemini_errors"] += 1
        print(f"[GEMINI ERROR] {e}")
        raise


async def ask_ai_hybrid(question: str, discord_id: str) -> str:
    """
    Sistema de IA HÃ­brido com fallback automÃ¡tico

    Prioridade:
    1. Groq (primÃ¡rio - 14.400 req/dia, mais rÃ¡pido)
    2. Gemini (fallback - 1.500 req/dia gratuito)

    Args:
        question: User's question
        discord_id: Discord ID for context retrieval

    Returns:
        AI response string
    """
    # Try Groq first (primary)
    try:
        print("[AI] Tentando Groq (primario)...")
        response = await ask_groq(question, discord_id)
        print(f"[AI] [OK] Groq respondeu ({len(response)} chars)")
        return response
    except Exception as e:
        print(f"[AI] [ERRO] Groq falhou: {e}")

        # Fallback to Gemini
        try:
            print("[AI] Tentando Gemini (fallback)...")
            response = await ask_gemini(question, discord_id)
            print(f"[AI] [OK] Gemini respondeu ({len(response)} chars)")
            return response
        except Exception as e2:
            print(f"[AI] [ERRO] Gemini falhou: {e2}")

            # Both failed
            return "Rapaz, deu ruim em todas as IAs... Tenta de novo em alguns segundos! (Erro de Conexao)"


# Synchronous wrapper for compatibility
def ask_ai_sync(question: str, discord_id: str) -> str:
    """Synchronous wrapper for ask_ai_hybrid"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(ask_ai_hybrid(question, discord_id))
    finally:
        loop.close()


async def ask_ai_admin(question: str, system_telemetry: str) -> str:
    """
    IA dedicada ao AdministraÃ§Ã£o (Texano)
    """
    full_prompt = f"{ADMIN_SYSTEM_PROMPT}\n\n[TELEMETRIA DO SISTEMA]\n{system_telemetry}\n\n[PERGUNTA DO ADMIN]\n{question}"

    # Tenta Groq primeiro
    try:
        client = None
        from groq import Groq

        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.7,
            max_tokens=500,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[AI ADMIN] Groq falhou, tentando Gemini: {e}")
        try:
            from google import genai

            client = genai.Client(api_key=GEMINI_API_KEY)
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=full_prompt,
                config={"temperature": 0.7, "max_output_tokens": 500},
            )
            return response.text.strip()
        except Exception as e2:
            print(f"[AI ADMIN] Falha total: {e2}")
            return "Rapaz, os motores tÃ¡ticos estÃ£o offline. Vou ter que checar os circuitos manualmente. (Erro de ConexÃ£o)"


def ask_ai_admin_sync(question: str, system_telemetry: str) -> str:
    """Wrapper sÃ­ncrono para o Texano Admin"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(ask_ai_admin(question, system_telemetry))
    finally:
        loop.close()


def get_ai_stats() -> dict:
    """Get AI usage statistics"""
    return {
        **ai_stats,
        "groq_success_rate": (ai_stats["groq_calls"] / max(ai_stats["total_calls"], 1))
        * 100,
        "gemini_usage_rate": (
            ai_stats["gemini_calls"] / max(ai_stats["total_calls"], 1)
        )
        * 100,
    }
