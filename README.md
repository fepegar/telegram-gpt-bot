# Telegram bot for ChatGPT

Send voice notes in any language (which will be translated to English) or text messages to ChatGPT.

## Set environment variables

- `TELEGRAM_BOT_TOKEN`: Telegram token from bot created using [@BotFather](https://t.me/botfather)
- `TELEGRAM_CLIENT_ID`: Telegram client ID from [@userinfobot](https://t.me/userinfobot)
- `OPENAI_API_KEY`: OpenAI API key from [OpenAI](https://beta.openai.com/)

## Installation

```shell
pip install telegpt
```

## Launch the bot

```shell
telegpt
```

## Usage

- Text `/new` to the bot to restart so it forget the last conversation.
- Voice notes in any language will be translated to English before being passed to ChatGPT.
