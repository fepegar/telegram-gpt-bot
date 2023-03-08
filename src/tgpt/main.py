import logging
import os

from telegram import Update
from telegram import Voice
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes

from whisper import Whisper


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


def is_me(update: Update):
    my_client_id = int(os.environ["TELEGRAM_CLIENT_ID"])
    return update.effective_chat.id == my_client_id


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_me(update):
        text = "Sorry, I'm not allowed to chat with you."
    else:
        text = update.message.text
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def voice_handler(update: Update, context: ContextTypes):
    if not is_me(update):
        return
    voice: Voice = update.message.voice
    logging.info(f"Voice message received ({voice.duration} seconds)")
    whisper = Whisper()
    text = whisper.transcribe(voice)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    # voice_file = await voice.get_file()
    # await voice_file.download_to_drive('voice.oga')


if __name__ == "__main__":
    token = os.environ["TELEGRAM_BOT_TOKEN"]

    application = ApplicationBuilder().token(token).build()

    echo_handler = MessageHandler(filters.TEXT, echo)
    application.add_handler(echo_handler)

    voice_handler = MessageHandler(filters.VOICE, voice_handler)
    application.add_handler(voice_handler)

    application.run_polling()
