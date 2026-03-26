import logging
from pathlib import Path

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

from config import PROXY_URL, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_IDS
from create_task import create_task
from task_name import build_task_name


LOG_PATH = Path(__file__).with_name("telegram_bot.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def is_allowed_chat(chat_id: int) -> bool:
    return chat_id in TELEGRAM_CHAT_IDS


async def reply_no_access(update: Update) -> None:
    if update.message:
        chat_id = update.effective_chat.id if update.effective_chat else None
        logger.warning("Access denied for chat_id=%s", chat_id)
        await update.message.reply_text("У вас нет доступа к этому боту.")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat:
        return

    if not is_allowed_chat(update.effective_chat.id):
        await reply_no_access(update)
        return

    await update.message.reply_text(
        "Отправьте задачу одним сообщением:\n"
        "1) Первая строка будет именем задачи (до 40 символов).\n"
        "2) Со второй строки начнется definition."
    )


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat or not update.message:
        return

    chat_id = update.effective_chat.id
    if not is_allowed_chat(chat_id):
        await reply_no_access(update)
        return

    message_text = (update.message.text or "").strip()
    if not message_text:
        logger.info("Empty message from chat_id=%s", chat_id)
        await update.message.reply_text("Пустое сообщение. Отправьте текст задачи.")
        return

    task_name = build_task_name(message_text)
    lines = message_text.splitlines()
    definition = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""
    if not definition:
        logger.info("Definition is empty after title removal for chat_id=%s", chat_id)
        await update.message.reply_text(
            "После первой строки (имя задачи) должен быть текст definition."
        )
        return

    logger.info("Creating task '%s' for chat_id=%s", task_name, chat_id)
    result = create_task(task_name=task_name, definition=definition)

    if result.get("success"):
        logger.info("Task created successfully: '%s' for chat_id=%s", task_name, chat_id)
        await update.message.reply_text(f"Задача создана: {task_name}")
    else:
        error_text = result.get("error", "Unknown error")
        logger.error(
            "Failed to create task '%s' for chat_id=%s: %s",
            task_name,
            chat_id,
            error_text,
        )
        await update.message.reply_text(f"Не удалось создать задачу: {error_text}")


def main() -> None:
    logger.info("Starting telegram bot")
    app = (
        ApplicationBuilder()
        .token(TELEGRAM_BOT_TOKEN)
        .proxy(PROXY_URL)
        .get_updates_proxy(PROXY_URL)
        .build()
    )
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    app.run_polling()


if __name__ == "__main__":
    main()
