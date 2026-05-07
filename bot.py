import logging
import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN")

SMALL_TALK_LINK = "https://chatgpt.com/g/g-68a718abfcbc819189ee9688df7c0721-small-talk-na-angliiskom-uverenno-i-zhivo"

KEYWORDS = {
    "СМОЛ-ТОК": "link",
    "ПРОМТЫ": "prompty",
    "ГОВОРЮ": "frazy",
}


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().upper()

    if text == "СМОЛ-ТОК":
        await update.message.reply_text(
            f"🎙 Вот твой GPT-агент для смол-тока на английском — уверенно и живо:\n\n{SMALL_TALK_LINK}"
        )

    elif text == "ПРОМТЫ":
        await update.message.reply_document(
            document=open("files/prompty.pdf", "rb"),
            caption="🧠 50 промптов, чтобы стать своим в UK и других англоязычных странах. Практикуй и делись результатами! 🇬🇧"
        )

    elif text == "ГОВОРЮ":
        await update.message.reply_document(
            document=open("files/frazy.pdf", "rb"),
            caption="💬 120+ фраз для общения с носителями английского языка — естественно и уверенно! 🇬🇧"
        )


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
