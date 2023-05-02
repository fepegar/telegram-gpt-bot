# Telegram bot for ChatGPT

## Set environment variables

- `TELEGRAM_BOT_TOKEN`: Telegram token from bot created using [@BotFather](https://t.me/botfather).
- `TELEGRAM_CLIENT_ID`: Telegram client ID from [@userinfobot](https://t.me/userinfobot)
- `OPENAI_API_KEY`: OpenAI API key from [OpenAI](https://beta.openai.com/).

## Installation

```shell
pip install .
```

## Launch the bot

```shell
telegpt
```

## Usage

- `/new`: Restart the bot so it forget the last conversation.
- Voice notes in any language will be translated to English before being passed to ChatGPT.
