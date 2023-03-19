import os
from pathlib import Path
from typing import Any

from pydub import AudioSegment
from telegram import Update
from telegram import Voice
from telegram.ext import ApplicationBuilder
from telegram.ext import CommandHandler
from telegram.ext import ContextTypes
from telegram.ext import MessageHandler
from telegram.ext import filters

from .apis import ChatGPT
from .apis import Whisper
from .utils import get_logger

logger = get_logger(__name__)


class Bot:
    def __init__(self) -> None:
        logger.info("Initializing bot")
        self.transcriber = Whisper()
        self.chat = ChatGPT()
        token = os.environ["TELEGRAM_BOT_TOKEN"]
        self.application = ApplicationBuilder().token(token).build()
        self.add_handlers()

    def add_handlers(self) -> None:
        text_handler = MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.text_callback,
        )
        self.application.add_handler(text_handler)

        voice_handler = MessageHandler(filters.VOICE, self.voice_callback)
        self.application.add_handler(voice_handler)

        new_session_handler = CommandHandler(  # type: ignore[var-annotated]
            "new",
            self.start_session,
        )
        self.application.add_handler(new_session_handler)

    @staticmethod
    def is_me(update: Update) -> bool:
        my_client_id = int(os.environ["TELEGRAM_CLIENT_ID"])
        assert update.effective_chat is not None
        return update.effective_chat.id == my_client_id

    def call_gpt(self, text: str) -> str:
        logger.info("Getting response from chatbot...")
        reply, _ = self.chat(text)
        logger.info(f'Reply received: "{reply}"')
        return reply

    async def text_callback(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        assert update.message is not None
        text = update.message.text
        assert isinstance(text, str)
        logger.info(f'Text message received: "{text}"')
        if not self.is_me(update):
            reply = "Sorry, I'm not allowed to chat with you."
        else:
            reply = self.call_gpt(text)
        assert update.effective_chat is not None
        await context.bot.send_message(chat_id=update.effective_chat.id, text=reply)

    async def voice_callback(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        if not self.is_me(update):
            return
        assert update.message is not None
        assert isinstance(update.message.voice, Voice)
        voice = update.message.voice
        logger.info(f"Voice message received ({voice.duration} seconds)")
        voice_file = await voice.get_file()
        mp3_path = Path("voice.mp3")
        oga_path = mp3_path.with_suffix(".oga")
        await voice_file.download_to_drive(oga_path)
        oga_file: AudioSegment = AudioSegment.from_file(oga_path, format="ogg")
        oga_file.export(mp3_path, format="mp3")
        logger.info("Transcribing audio...")
        transcript = self.transcriber(mp3_path)
        logger.info(f"Transcript: {transcript}")
        reply = self.call_gpt(transcript)
        assert update.effective_chat is not None
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=reply,
        )

    async def start_session(self, *args: Any) -> None:
        logger.info("Initializing new ChatGPT session")
        self.chat = ChatGPT()

    def run(self) -> None:
        logger.info("The bot is ready")
        self.application.run_polling()
