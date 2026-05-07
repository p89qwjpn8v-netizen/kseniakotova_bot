# Инструкция по запуску бота kseniakotova_bot

## Структура файлов
```
kseniakotova_bot/
├── bot.py              ← основной код бота
├── requirements.txt    ← зависимости
├── railway.toml        ← конфиг Railway
└── files/
    ├── prompty.pdf     ← 50 промптов (код ПРОМТЫ)
    └── frazy.pdf       ← 120+ фраз (код ГОВОРЮ)
```

## Шаги деплоя на Railway

### 1. Создай репозиторий на GitHub
- Зайди на github.com → New repository
- Название: kseniakotova_bot
- Загрузи все файлы (включая папку files/ с PDF)

### 2. Зарегистрируйся на Railway
- railway.app → Login with GitHub

### 3. Создай проект
- New Project → Deploy from GitHub repo
- Выбери kseniakotova_bot

### 4. Добавь токен бота
- В проекте → Variables → New Variable
- Имя: BOT_TOKEN
- Значение: вставь токен от @BotFather

### 5. Готово!
Railway автоматически установит зависимости и запустит бота.

## Кодовые слова
| Слово | Что выдаёт |
|-------|-----------|
| СМОЛ-ТОК | Ссылка на GPT-агента |
| ПРОМТЫ | PDF — 50 промптов |
| ГОВОРЮ | PDF — 120+ фраз |

## Добавить новый лид-магнит
В файле bot.py найди функцию handle_message и добавь новый elif:

```python
elif text == "НОВОЕ_СЛОВО":
    await update.message.reply_document(
        document=open("files/noviy_fail.pdf", "rb"),
        caption="Описание магнита"
    )
```
Не забудь положить PDF в папку files/.
