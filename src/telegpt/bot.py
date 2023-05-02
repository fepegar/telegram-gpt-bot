import datetime
import os
import tempfile
import time
from pathlib import Path

import openai
from pydub import AudioSegment
from telegram import Update
from telegram import Voice
from telegram.ext import ApplicationBuilder
from telegram.ext import CommandHandler
from telegram.ext import ContextTypes
from telegram.ext import MessageHandler
from telegram.ext import filters

from .apis import GPT4
from .apis import Whisper
from .utils import get_cache_dir
from .utils import get_logger

logger = get_logger(__name__)


class Bot:
    def __init__(self) -> None:
        logger.info("Initializing bot")
        self._transcriber = Whisper()
        self._chatbot_class = GPT4
        self._chatbot = self._chatbot_class()
        telegram_token = os.environ["TELEGRAM_BOT_TOKEN"]
        self._application = ApplicationBuilder().token(telegram_token).build()
        self._add_handlers()
        self._cache_dir = get_cache_dir()
        self._show_cost = False

    def _add_handlers(self) -> None:
        text_handler = MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self._text_callback,
        )
        self._application.add_handler(text_handler)

        voice_handler = MessageHandler(filters.VOICE, self._voice_callback)
        self._application.add_handler(voice_handler)

        new_session_handler = CommandHandler(
            "new",
            self._start_session,
        )
        self._application.add_handler(new_session_handler)

    async def _chat(self, text: str) -> tuple[str, float]:
        logger.info("Getting response from chatbot...")
        await self._send("[Getting response from chatbot...]")
        reply, cost = self._chatbot(text)
        logger.info(f'Reply received: "{reply}"')
        logger.info(f"Cost: £{100 * cost:.3}p")
        return reply, cost

    async def _send(self, message: str) -> None:
        assert self.update.effective_chat is not None
        await self.context.bot.send_message(
            chat_id=self.update.effective_chat.id,
            text=message,
        )

    def _set_update_context(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        self.update = update
        self.context = context

    async def _text_callback(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        self._set_update_context(update, context)
        if not await self._check_is_me():
            return
        assert update.message is not None
        text = update.message.text
        assert isinstance(text, str)
        logger.info(f'Text message received: "{text}"')
        reply, cost = await self._chat(text)
        assert update.effective_chat is not None
        if self._show_cost:
            await self._send(f"[Cost: £{100 * cost:.3}p]")
        await self._send(reply)

    async def _check_is_me(self) -> bool:
        my_client_id = int(os.environ["TELEGRAM_CLIENT_ID"])
        assert self.update.effective_chat is not None
        is_me = self.update.effective_chat.id == my_client_id
        if is_me:
            return True
        else:
            await self._send("Sorry, I'm not allowed to chat with you.")
            return False

    async def _start_session(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        self._set_update_context(update, context)
        if not await self._check_is_me():
            return
        message = f"Initializing chatbot session ({self._chatbot_class.__name__})"
        logger.info(message)
        _ = self._send(message)
        self._chatbot = self._chatbot_class()

    async def _get_mp3_from_voice(self, voice: Voice) -> Path:
        logger.info(f"Voice message received ({voice.duration} seconds)")
        voice_file = await voice.get_file()
        time_string = datetime.datetime.now().isoformat()
        filename = f"{time_string}_voice.mp3"
        mp3_path = self._cache_dir / filename
        with tempfile.NamedTemporaryFile(suffix=".oga") as f:
            oga_path = Path(f.name)
            await voice_file.download_to_drive(oga_path)
            oga_file: AudioSegment = AudioSegment.from_file(oga_path, format="ogg")
            oga_file.export(mp3_path, format="mp3")
        return mp3_path

    async def _voice_callback(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        max_num_attempts: int = 3,
        waiting_time: float = 1,
    ) -> None:
        self._set_update_context(update, context)
        if not await self._check_is_me():
            return

        assert update.message is not None
        assert isinstance(update.message.voice, Voice)
        voice = update.message.voice
        logger.info(f"Voice message received ({voice.duration} seconds)")
        mp3_path = await self._get_mp3_from_voice(voice)

        logger.info("Transcribing audio...")
        assert update.effective_chat is not None
        await self._send(f"[Transcribing {voice.duration} seconds of audio...]")
        attempts = 0
        while attempts < max_num_attempts:
            try:
                transcript = self._transcriber(mp3_path)
                logger.info(f'Transcript: "{transcript}"')
                await self._send(f'[Transcript: "{transcript}"]')
                reply, cost = await self._chat(transcript)
                if self._show_cost:
                    await self._send(f"[Cost: £{100 * cost:.3}p]")
                await self._send(reply)
                return
            except openai.error.APIConnectionError:
                await self._send("[Transcription error. Trying again...]")
                attempts += 1
                time.sleep(waiting_time)
        await self._send("[Transcription API not working. Try using text...]")

    def run(self) -> None:
        logger.info("The bot is ready")
        self._application.run_polling()
