import os
import asyncio
from google import genai
from dotenv import load_dotenv

# Carrega .env do diretÃ³rio pai (BigodeBot)
load_dotenv(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
)

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "models/gemini-flash-latest"


async def test_gemini():
    print(f"--- TESTANDO GEMINI API ---")
    print(f"API_KEY encontrada: {'Sim' if API_KEY else 'NÃ£o'}")

    if not API_KEY:
        print("Erro: GEMINI_API_KEY nÃ£o encontrada no .env")
        return

    try:
        print(
            f"Inicializando cliente com a chave: {API_KEY[:5]}...{API_KEY[-5:] if len(API_KEY) > 10 else ''}"
        )
        client = genai.Client(api_key=API_KEY)

        print("Listando modelos disponÃ­veis...")
        models = client.models.list()
        for m in models:
            print(f"- {m.name} (Supported: {m.supported_actions})")

        print(f"Enviando pergunta de teste para o modelo {MODEL_NAME}...")

        # Teste sÃ­ncrono primeiro para simplificar
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents="OlÃ¡, vocÃª estÃ¡ funcionando? Responda com 'SISTEMA OPERACIONAL'.",
        )

        if response and response.text:
            print(f"Resposta recebida: {response.text}")
        else:
            print("Aviso: Resposta vazia recebida do modelo.")

    except Exception as e:
        print(f"ERRO CRÃTICO NA CONEXÃƒO: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_gemini())
