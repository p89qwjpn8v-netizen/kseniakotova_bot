import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, filters, ContextTypes

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL = "@lingvopodcasts"
CONSULTATION_LINK = "https://t.me/lingvopodcasts"
SMALL_TALK_LINK = "https://chatgpt.com/g/g-68a718abfcbc819189ee9688df7c0721-small-talk-na-angliiskom-uverenno-i-zhivo"

QUESTIONS = [
    {
        "text": "1. Когда говорите по-английски в важный момент, что происходит чаще?",
        "options": [
            ("A. Знаю что сказать, но собираю фразу медленно", "T1"),
            ("B. В голове пусто, я напрягаюсь, в быту такого нет", "T2"),
            ("C. Практикую редко, нет места в графике", "T3"),
            ("D. Говорю, но с паузами, не как на русском", "T4"),
        ]
    },
    {
        "text": "2. Где английский подводит сильнее всего?",
        "options": [
            ("A. В быстром диалоге, не успеваю за темпом", "T1"),
            ("B. На интервью, питче, переговорах", "T2"),
            ("C. Везде понемногу, занятия нерегулярны", "T3"),
            ("D. Почти везде ок, но нет беглости", "T4"),
        ]
    },
    {
        "text": "3. Какая мысль о себе ближе?",
        "options": [
            ("A. Понимаю больше, чем говорю", "T1"),
            ("B. В ответственный момент рассыпаюсь", "T2"),
            ("C. Нет времени учить язык как проект", "T3"),
            ("D. На английском я — упрощённая версия себя", "T4"),
        ]
    },
    {
        "text": "4. Что мешает сильнее всего?",
        "options": [
            ("A. Постоянный перевод в голове, нет автоматизма", "T1"),
            ("B. Страх прозвучать слабее своей экспертизы", "T2"),
            ("C. Завал на работе и страх снова бросить", "T3"),
            ("D. Упёрся в потолок, дальше не двигается", "T4"),
        ]
    },
    {
        "text": "5. Лучший результат через 90 дней?",
        "options": [
            ("A. Говорить без задержки, не переводя в голове", "T1"),
            ("B. Уверенно держаться в интервью и переговорах", "T2"),
            ("C. Английский встроен в график без усилий", "T3"),
            ("D. Звучать бегло и естественно, как я сам(а)", "T4"),
        ]
    },
    {
        "text": "6. Есть ли впереди конкретное событие или дедлайн?",
        "options": [
            ("A. Да, интервью/ презентация или важная сделка", "intens"),
            ("B. Нет дедлайна, хочу системно", "strat"),
            ("C. Пока хочу понять, что вообще делать", "diag"),
        ]
    },
]

RESULTS = {
    "T1": (
        "💡 Ваш тип: «Думаю на русском — говорю с задержкой»\n\n"
        "У вас не ноль языка, у вас разрыв между пассивом и живой реакцией. "
        "Вы понимаете и читаете, но фраза собирается через русский, и пока вы её переводите, "
        "разговор уже ушёл вперёд. Дело не в количестве слов — слова и так есть, не хватает автоматизма. "
        "В лингвокоучинге мы не «доучиваем язык вообще», а точечно перестраиваем речевую опору "
        "под ваши ситуации. С чего начать именно в вашем случае, разберём на вводной консультации."
    ),
    "T2": (
        "💡 Ваш тип: «В быту ок, но на встрече обнуляюсь»\n\n"
        "Раз в быту вы говорите нормально — дело не в уровне. В интервью, питче или переговорах "
        "тело реагирует раньше головы, и вы звучите слабее, чем есть. А это уже про деньги и статус: "
        "за тем же столом можно звучать «на свой рейт» или втрое дешевле. "
        "Это тренируется заранее — под конкретное событие, а не «английским вообще». "
        "Если впереди важная встреча, на консультации разложим её на навыки и соберём план под неё."
    ),
    "T3": (
        "💡 Ваш тип: «Английский как вторая работа»\n\n"
        "Вы не ленитесь — у вас просто нет лишней жизни на проект «по два часа в день». "
        "Поэтому язык идёт рывками: взялись — бросили — снова взялись. "
        "Дело не в дисциплине, а в отсутствии системы, которая живёт рядом с работой, а не вместо неё. "
        "В лингвокоучинге мы отсекаем второстепенное и встраиваем английский в ваши уже существующие окна. "
        "Как это выглядит под ваш режим, разберём на вводной консультации."
    ),
    "T4": (
        "💡 Ваш тип: «Говорю, но звучу не как я»\n\n"
        "Вы уже неплохо говорите и именно поэтому застряли: базовые курсы вам ничего нового не дают, "
        "а гладкости и уверенности всё равно нет. Паузы, шероховатости, ощущение упрощённой версии себя. "
        "Это не «учить заново», это отполировать под ваши реальные ситуации, чтобы на английском "
        "вы звучали как вы. С этого и начинается лингвокоучинг — с диагностики того, что именно вас тормозит. "
        "Первый шаг — вводная консультация."
    ),
}

CTA_TEXT = (
    "\n\n—\n"
    "Это короткая диагностик показывает направление. "
    "Полную картину, а именно вашу точку А, точку Б и тот самый мостик, которого не хватает — "
    "собираем на вводной консультации (40 минут)."
)


async def is_subscribed(user_id, context):
    try:
        member = await context.bot.get_chat_member(CHANNEL, user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception:
        return False


def subscribe_keyboard(after_action):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📲 Подписаться на канал", url="https://t.me/lingvopodcasts")],
        [InlineKeyboardButton("✅ Я подписался(ась)", callback_data=f"check_{after_action}")]
    ])


def question_keyboard(q_index):
    q = QUESTIONS[q_index]
    buttons = []
    for i, (text, _) in enumerate(q["options"]):
        letter = chr(65 + i)
        buttons.append([InlineKeyboardButton(text, callback_data=f"q{q_index}_{letter}")])
    return InlineKeyboardMarkup(buttons)


async def send_content(message, context, keyword):
    if keyword == "СМОЛ-ТОК":
        await message.reply_text(f"🎙 Вот ваш GPT-агент для смол-тока на английском:\n\n{SMALL_TALK_LINK}")
    elif keyword == "ПРОМТЫ":
        await message.reply_document(
            document=open("files/prompty.pdf", "rb"),
            caption="🧠 50 промптов, чтобы стать своим в UK. Практикуйте и делитесь результатами! 🇬🇧"
        )
    elif keyword == "ГОВОРЮ":
        await message.reply_document(
            document=open("files/frazy.pdf", "rb"),
            caption="💬 120+ фраз для общения с носителями — естественно и уверенно! 🇬🇧"
        )


async def start_quiz(message, context):
    context.user_data["scores"] = {"T1": 0, "T2": 0, "T3": 0, "T4": 0}
    context.user_data["q6_label"] = None
    await message.reply_text(
        "Отлично! 6 коротких вопросов — отвечайте по первому ощущению, "
        "тут нет правильных и неправильных. Поехали 👇",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Начать", callback_data="quiz_start")]])
    )


async def show_result(message, context):
    scores = context.user_data.get("scores", {"T1": 0, "T2": 0, "T3": 0, "T4": 0})
    max_score = max(scores.values())
    dominant = "T2" if scores["T2"] == max_score else max(scores, key=lambda t: scores[t])
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("📅 Записаться на консультацию", url=CONSULTATION_LINK)]])
    await message.reply_text(RESULTS[dominant] + CTA_TEXT, reply_markup=keyboard)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().upper()
    user_id = update.message.from_user.id

    if text in ("СМОЛ-ТОК", "ПРОМТЫ", "ГОВОРЮ"):
        if await is_subscribed(user_id, context):
            await send_content(update.message, context, text)
        else:
            await update.message.reply_text(
                "Материал почти у вас! 🎁\n\n"
                "Подпишитесь на канал — там практика, разборы и лайфхаки для уверенного английского.\n\n"
                "После подписки нажмите кнопку ниже 👇",
                reply_markup=subscribe_keyboard(text)
            )
    elif text == "ТЕСТ":
        if await is_subscribed(user_id, context):
            await start_quiz(update.message, context)
        else:
            await update.message.reply_text(
                "Привет! За 2 минуты покажу, где именно застревает ваш английский — и что с этим делать.\n\n"
                "Тест откроется сразу после подписки на канал 👇",
                reply_markup=subscribe_keyboard("ТЕСТ")
            )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data.startswith("check_"):
        action = data.replace("check_", "")
        if await is_subscribed(user_id, context):
            if action == "ТЕСТ":
                await query.message.reply_text("✅ Отлично, вы подписаны! Начинаем тест.")
                await start_quiz(query.message, context)
            else:
                await query.message.reply_text("✅ Отлично, вы подписаны! Вот ваш материал:")
                await send_content(query.message, context, action)
        else:
            await query.answer("Подписка не найдена. Подпишитесь и нажмите кнопку снова 👇", show_alert=True)

    elif data == "quiz_start":
        await query.message.reply_text(QUESTIONS[0]["text"], reply_markup=question_keyboard(0))

    elif len(data) >= 3 and data[0] == "q" and "_" in data:
        parts = data.split("_")
        q_index = int(parts[0][1:])
        letter_index = ord(parts[1]) - 65

        if q_index < 5:
            _, type_code = QUESTIONS[q_index]["options"][letter_index]
            if "scores" not in context.user_data:
                context.user_data["scores"] = {"T1": 0, "T2": 0, "T3": 0, "T4": 0}
            context.user_data["scores"][type_code] += 1
            next_q = q_index + 1
            await query.message.reply_text(QUESTIONS[next_q]["text"], reply_markup=question_keyboard(next_q))
        else:
            _, label = QUESTIONS[q_index]["options"][letter_index]
            context.user_data["q6_label"] = label
            await show_result(query.message, context)


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback))
    logger.info("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
