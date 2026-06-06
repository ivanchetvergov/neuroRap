import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from neurorap.artists import ARTIST_DEFAULT_TAGS, ARTIST_LIST
from neurorap.config import MODELS_DIR, TRAIN_CONFIG
from neurorap.generate.generator import Generator

load_dotenv()
logging.basicConfig(format="%(asctime)s %(name)s %(levelname)s %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

DEFAULT_ARTIST = "PHARAOH"
_ARTIST_SET = set(ARTIST_LIST)


def _make_generator() -> Generator:
    model_path = MODELS_DIR / "final"
    return Generator(model_path, TRAIN_CONFIG.base_model)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    artist = context.user_data.get("artist", DEFAULT_ARTIST)
    await update.message.reply_text(
        f"НейроРэп-бот\n"
        f"Текущий артист: {artist}\n\n"
        f"Команды:\n"
        f"/artist <имя> — сменить артиста\n"
        f"/artists — список доступных артистов\n"
        f"Просто отправь текст — получишь продолжение."
    )


async def cmd_artists(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("\n".join(ARTIST_LIST))


async def cmd_artist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Укажи артиста: /artist PHARAOH")
        return

    name = " ".join(context.args)
    if name not in _ARTIST_SET:
        await update.message.reply_text(f"Артист '{name}' не найден. /artists — полный список.")
        return

    context.user_data["artist"] = name
    await update.message.reply_text(f"Артист: {name}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    generator: Generator = context.bot_data["generator"]
    artist = context.user_data.get("artist", DEFAULT_ARTIST)
    seed = update.message.text.strip()

    await update.message.reply_text("Генерирую...")
    try:
        lines = generator.generate(artist=artist, seed=seed)
        result = "\n".join(line for line in lines if line.strip())
        await update.message.reply_text(f"[{artist}]\n\n{result}")
    except Exception as e:
        logger.error("Generation error: %s", e)
        await update.message.reply_text("Ошибка генерации, попробуй ещё раз.")


def run() -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    generator = _make_generator()

    app = Application.builder().token(token).build()
    app.bot_data["generator"] = generator

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("artists", cmd_artists))
    app.add_handler(CommandHandler("artist", cmd_artist))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot started")
    app.run_polling(allowed_updates=Update.ALL_TYPES)
