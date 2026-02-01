import asyncio
import os
from dotenv import load_dotenv

# Carrega .env do diretório certo
load_dotenv(dotenv_path="../.env")


async def test_texano():
    print("--- Testando Integração Texano AI (Nova biblioteca) ---")
    try:
        from ai_integration import ask_gemini

        pergunta = "Qual é o mapa do servidor e qual o estilo de jogo?"
        print(f"Pergunta: {pergunta}")

        resposta = await ask_gemini(pergunta)

        print("\nResposta da IA:")
        print(f"{resposta}")
        print("\n--- Teste Finalizado ---")

    except Exception as e:
        print(f"\n[ERRO NO TESTE]: {e}")


if __name__ == "__main__":
    asyncio.run(test_texano())
