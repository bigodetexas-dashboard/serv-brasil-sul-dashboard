"""
Bigodudo Chat Widget - Interface web para conversar com a IA
"""

from flask import Blueprint, request, jsonify, session
from ai_integration import ask_gemini
import asyncio

bigodudo_bp = Blueprint("bigodudo", __name__)


@bigodudo_bp.route("/api/bigodudo/chat", methods=["POST"])
def chat():
    """
    Endpoint para chat com o Bigodudo

    POST /api/bigodudo/chat
    Body: {"message": "sua pergunta"}
    """
    if "user_id" not in session:
        return jsonify({"error": "Você precisa estar logado para falar com o Bigodudo!"}), 401

    data = request.get_json()
    pergunta = data.get("message", "").strip()

    if not pergunta:
        return jsonify({"error": "Cadê a pergunta, parceiro?"}), 400

    if len(pergunta) > 500:
        return jsonify({"error": "Rapaz, essa pergunta tá muito grande! Seja mais direto."}), 400

    try:
        discord_id = str(session["user_id"])

        # Chamar IA (precisa ser async)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        resposta = loop.run_until_complete(ask_gemini(question=pergunta, discord_id=discord_id))
        loop.close()

        return jsonify({"success": True, "response": resposta, "bigodudo_name": "Bigodudo"})

    except Exception as e:
        print(f"[BIGODUDO] Erro no chat: {e}")
        return jsonify({"error": "Rapaz, deu ruim aqui... Tenta de novo!", "details": str(e)}), 500


@bigodudo_bp.route("/api/bigodudo/suggestions", methods=["GET"])
def suggestions():
    """Retorna sugestões de perguntas para o Bigodudo"""
    sugestoes = [
        "Quem me matou?",
        "Quanto eu tenho de coins?",
        "Onde fica NWAF?",
        "Como ganho coins rápido?",
        "Qual meu K/D?",
        "Quem tá no top 5?",
        "Qual meu clã?",
        "Minhas últimas compras",
        "Atividade do servidor",
        "Dicas para iniciantes",
    ]

    return jsonify({"suggestions": sugestoes})
