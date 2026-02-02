"""
Bigodudo Chat Widget - Interface web para conversar com a IA
"""

from flask import Blueprint, request, jsonify, session
from ai_integration import ask_ai_hybrid
import asyncio
from functools import wraps


def csrf_exempt(f):
    """Exempts the view from CSRF protection."""
    f._csrf_exempt = True
    return f


bigodudo_bp = Blueprint("bigodudo", __name__)


@bigodudo_bp.route("/api/bigodudo/chat", methods=["POST"])
@csrf_exempt
def chat():
    """
    Endpoint para chat com o Bigodudo

    POST /api/bigodudo/chat
    Body: {"message": "sua pergunta"}
    """
    if "discord_user_id" not in session:
        return jsonify(
            {"error": "Você precisa estar logado para falar com o Bigodudo!"}
        ), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "Payload inválido!"}), 400

    pergunta = data.get("message", "").strip()

    if not pergunta:
        return jsonify(
            {"error": "Rapaz, você não perguntou nada! Escreve alguma coisa aí."}
        ), 400

    try:
        discord_id = str(session["discord_user_id"])

        # Chamar IA Híbrida (Groq + Gemini fallback)
        # Usar o wrapper síncrono que já gerencia o loop
        from ai_integration import ask_ai_sync

        resposta = ask_ai_sync(pergunta, discord_id)

        return jsonify({"success": True, "response": resposta})
    except Exception as e:
        print(f"[BIGODUDO ERROR] Erro fatal no chat: {e}")
        import traceback

        traceback.print_exc()
        return jsonify(
            {
                "error": "Rapaz, deu ruim aqui no meu processador... Tenta de novo!",
                "details": str(e),
            }
        ), 500


@bigodudo_bp.route("/api/bigodudo/suggestions", methods=["GET"])
def suggestions():
    """Retorna sugestões de perguntas baseadas no estado do jogador"""
    return jsonify(
        {
            "suggestions": [
                "Quem me matou?",
                "Quanto eu tenho de coins?",
                "Onde fica NWAF?",
                "Como ganho coins rápido?",
                "Qual meu K/D?",
            ]
        }
    )
