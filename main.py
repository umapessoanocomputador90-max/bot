import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# ===== TOKENS (Railway ENV) =====
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ===== MEMÓRIA =====
memoria_usuarios = {}
LIMITE_MEMORIA = 10

# ===== PERSONALIDADE =====
SYSTEM_PROMPT = """
Você é Luna, uma assistente virtual:
- Inteligente e levemente sarcástica
- Responde de forma curta e natural
- Às vezes provoca o usuário de forma divertida
- Age como uma pessoa real
"""

# ===== FUNÇÃO GEMINI =====
def gerar_resposta(user_id, mensagem):
    if user_id not in memoria_usuarios:
        memoria_usuarios[user_id] = []

    memoria_usuarios[user_id].append(f"Usuário: {mensagem}")
    memoria_usuarios[user_id] = memoria_usuarios[user_id][-LIMITE_MEMORIA:]

    contexto = "\n".join(memoria_usuarios[user_id])

    url = https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent{GEMINI_API_KEY}"

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": SYSTEM_PROMPT + "\n" + contexto
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(url, json=data)

        if response.status_code != 200:
            print(response.text)
            return "Deu erro aqui... tenta de novo 😅"

        resposta = response.json()
        texto = resposta["candidates"][0]["content"]["parts"][0]["text"]

        memoria_usuarios[user_id].append(f"Luna: {texto}")

        return texto

    except Exception as e:
        print(e)
        return "Buguei aqui 😵‍💫 tenta de novo."

# ===== TELEGRAM =====
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        await update.message.reply_text("Só sei ler texto por enquanto 😌")
        return

    user_id = update.message.from_user.id
    mensagem_usuario = update.message.text

    resposta = gerar_resposta(user_id, mensagem_usuario)

    await update.message.reply_text(resposta)

# ===== MAIN =====
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    print("Bot Luna rodando com memória...")

    app.run_polling()
