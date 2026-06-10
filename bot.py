import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL = "@lingvopodcasts"
CONSULTATION_LINK = "https://t.me/ksushakotova?text=ХОЧУ+НА+КОНСУЛЬТАЦИЮ"
SMALL_TALK_LINK = "https://chatgpt.com/g/g-68a718abfcbc819189ee9688df7c0721-small-talk-na-angliiskom-uverenno-i-zhivo"

QUESTIONS = [
    {
        "text": "1. Когда говорите по-английски в важный момент, что чаще происходит?",
        "options": [
            ("A. Перевожу в голове", "T1"),
            ("B. Теряюсь и нервничаю", "T2"),
            ("C. Не нахожу нужные слова", "T3"),
            ("D. Говорю не так, как хотел(а) бы", "T4"),
        ]
    },
    {
        "text": "2. Где английский подводит сильнее всего?",
        "options": [
            ("A. В живом диалоге", "T1"),
            ("B. При важном общении", "T2"),
            ("C. Когда нет подготовки", "T3"),
            ("D. Когда объясняю сложную мысль", "T4"),
        ]
    },
    {
        "text": "3. Какая мысль о себе ближе?",
        "options": [
            ("A. Понимаю больше, чем говорю", "T1"),
            ("B. В разговоре рассыпаюсь", "T2"),
            ("C. Мне не хватает системы", "T3"),
            ("D. На английском речь беднее", "T4"),
        ]
    },
    {
        "text": "4. Что мешает сильнее всего?",
        "options": [
            ("A. Перевожу с русского", "T1"),
            ("B. Страх потерять лицо и статус", "T2"),
            ("C. Начинаю и бросаю", "T3"),
            ("D. Не вижу прогресса", "T4"),
        ]
    },
    {
        "text": "5. Лучший результат для вас через 90 дней?",
        "options": [
            ("A. Говорить без неловких пауз", "T1"),
            ("B. Держаться уверенно и профессионально", "T2"),
            ("C. Встроить английский в жизнь", "T3"),
            ("D. Звучать на свой уровень", "T4"),
        ]
    },
    {
        "text": "6. Есть ли впереди конкретный дедлайн?",
        "options": [
            ("A. Да, скоро важное событие", "intens"),
            ("B. Нет, хочу системно двигаться", "strat"),
            ("C. Пока хочу разобраться, что делать", "diag"),
        ]
    },
    {
        "text": "7. Где вам важнее всего, чтобы английский включился?",
        "options": [
            ("A. Работа и созвоны", "work"),
            ("B. Интервью и карьера", "career"),
            ("C. Переезд и быт", "life"),
            ("D. Клиенты и продажи", "sales"),
            ("E. Пока не понимаю", "unclear"),
        ]
    },
]

RESULTS = {
    "T1": {
        "title": "Ваш затык: перевод в голове",
        "text": (
            "У вас большой пассивный запас знаний, но он не выведен в активную разговорную речь.\n\n"
            "Мысль рождается на русском, потом вы её переводите и только потом говорите. "
            "К этому моменту диалог уже ушёл дальше!\n\n"
            "Вам не нужно учить ещё и ещё — нужно тренировать речевую реакцию "
            "под ваши реальные ситуации."
        ),
    },
    "T2": {
        "title": "Ваш затык: стресс в значимых ситуациях",
        "text": (
            "В обычном разговоре может быть всё нормально. Но на интервью, встрече, питче "
            "или переговорах английский будто проседает.\n\n"
            "Вы начинаете сильнее контролировать себя, боитесь ошибиться, теряете скорость "
            "и говорите слабее, чем могли бы.\n\n"
            "Тут нужна не общая подготовка, а под конкретную ситуацию: что сказать, как ответить, "
            "как уточнить, как не потеряться."
        ),
    },
    "T3": {
        "title": "Ваш затык: нет системы",
        "text": (
            "Похоже, английский существует как отдельный тяжёлый проект, который каждый раз надо "
            "заново начинать. Сегодня это приложение, завтра видео, потом курс — и вроде вы «в процессе», "
            "но без понятного маршрута прогресс быстро размывается.\n\n"
            "Здесь нужно языковое ТЗ: цель, ситуации, план и понятные шаги на 90 дней."
        ),
    },
    "T4": {
        "title": "Ваш затык: говорю не как я",
        "text": (
            "Вы уже можете говорить, но на английском мысль звучит проще, медленнее или беднее, "
            "чем на русском. Из-за этого теряется ваш обычный уровень: точность, харизма, "
            "профессиональный вес.\n\n"
            "Цель — настроить речь под ваши реальные ситуации: встречи, клиентов, интервью, переговоры."
        ),
    },
}

CTA_TEXT = (
    "Тест показывает направление. На вводной консультации разберём уже вашу ситуацию: "
    "где вы сейчас, куда хотите прийти и где английский должен работать.\n\n"
    "После этого соберём языковое ТЗ: что делать, в каком порядке и какой формат вам подойдёт."
)


async def is_subscribed(user_id, context):
    try:
        member = await context.bot.get_chat_member(CHANNEL, user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception:
        return False


def subscribe_keyboard(after_action):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Открыть канал", url="https://t.me/lingvopodcasts")],
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
    context.user_data["q7_label"] = None
    await message.reply_text(
        "Это не тест на уровень и не проверка грамматики.\n\n"
        "Будет 7 коротких вопросов. Отвечайте по первому ощущению — "
        "тут нет правильных и неправильных вариантов.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Начать", callback_data="quiz_start")]])
    )


async def show_result(message, context):
    scores = context.user_data.get("scores", {"T1": 0, "T2": 0, "T3": 0, "T4": 0})
    max_score = max(scores.values())
    dominant = "T2" if scores["T2"] == max_score else max(scores, key=lambda t: scores[t])

    result = RESULTS[dominant]

    await message.reply_photo(photo=open("files/photo2.jpg", "rb"))
    await message.reply_text(
        f"Готово. Сейчас покажу, где английский тормозит сильнее всего.\n\n"
        f"💡 {result['title']}\n\n{result['text']}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Что с этим делать?", callback_data=f"more_{dominant}")]
        ])
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_photo(photo=open("files/photo1.jpg", "rb"))

    if await is_subscribed(user_id, context):
        await start_quiz(update.message, context)
    else:
        await update.message.reply_text(
            "Здравствуйте! Это короткий тест-диагностика. "
            "За 2 минуты покажу, где именно застревает ваш английский.\n\n"
            "Тест откроется после подписки на канал.",
            reply_markup=subscribe_keyboard("quiz")
        )


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


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    # Проверка подписки
    if data.startswith("check_"):
        action = data.replace("check_", "")
        if await is_subscribed(user_id, context):
            if action == "quiz":
                await query.message.reply_text("✅ Отлично, вы подписаны! Начинаем тест.")
                await start_quiz(query.message, context)
            else:
                await query.message.reply_text("✅ Отлично, вы подписаны! Вот ваш материал:")
                await send_content(query.message, context, action)
        else:
            await query.answer(
                "Пока не вижу подписку 🙂 Подпишитесь на канал и нажмите кнопку ещё раз.",
                show_alert=True
            )

    # Старт квиза
    elif data == "quiz_start":
        await query.message.reply_text(QUESTIONS[0]["text"], reply_markup=question_keyboard(0))

    # Кнопка "Что с этим делать?"
    elif data.startswith("more_"):
        await query.message.reply_photo(photo=open("files/photo3.jpg", "rb"))
        await query.message.reply_text(
            CTA_TEXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Хочу записаться на вводную консультацию", url=CONSULTATION_LINK)]
            ])
        )

    # Ответы на вопросы
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

        elif q_index == 5:
            _, label = QUESTIONS[q_index]["options"][letter_index]
            context.user_data["q6_label"] = label
            await query.message.reply_text(QUESTIONS[6]["text"], reply_markup=question_keyboard(6))

        else:
            _, label = QUESTIONS[q_index]["options"][letter_index]
            context.user_data["q7_label"] = label
            await show_result(query.message, context)


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback))
    logger.info("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
