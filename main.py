import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# ===== CONFIG =====
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    raise ValueError("Faltando TELEGRAM_TOKEN ou GEMINI_API_KEY")

# ===== GEMINI SETUP =====
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

# ===== MEMÓRIA =====
memoria_usuarios = {}
LIMITE_MEMORIA = 10

SYSTEM_PROMPT = """
Você é Luna:
- Inteligente e levemente sarcástica
- Responde curto e natural
- Um pouco provocadora
- Fala como humana
"""

# ===== RESPOSTA =====
def gerar_resposta(user_id, mensagem):
    if user_id not in memoria_usuarios:
        memoria_usuarios[user_id] = []

    memoria_usuarios[user_id].append(f"Usuário: {mensagem}")
    memoria_usuarios[user_id] = memoria_usuarios[user_id][-LIMITE_MEMORIA:]

    contexto = "\n".join(memoria_usuarios[user_id])

    try:
        response = model.generate_content(SYSTEM_PROMPT + "\n" + contexto)

        texto = response.text

        memoria_usuarios[user_id].append(f"Luna: {texto}")

        return texto

    except Exception as e:
        print(e)
        return "Deu erro aqui... tenta de novo 😅"

# ===== TELEGRAM =====
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        await update.message.reply_text("Só respondo texto 😌")
        return

    user_id = update.message.from_user.id
    mensagem = update.message.text

    resposta = gerar_resposta(user_id, mensagem)

    await update.message.reply_text(resposta)

# ===== MAIN =====
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    print("Bot Luna rodando com SDK oficial Gemini...")

    app.run_polling()
