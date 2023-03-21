from dataclasses import asdict
from dataclasses import dataclass

import openai


@dataclass
class SystemMessage:
    content: str
    role: str = "system"


@dataclass
class UserMessage:
    content: str
    role: str = "user"


@dataclass
class AssistantMessage:
    content: str
    role: str = "assistant"


class ChatGPT:
    _MODEL_NAME = "gpt-3.5-turbo"
    _DEFAULT_SYSTEM_MESSAGE = (
        "You are ChatGPT, a large language model trained by OpenAI."
        " Answer as concisely as possible."
    )

    def __init__(self) -> None:
        self.history: list[SystemMessage | UserMessage | AssistantMessage]
        self.history = [SystemMessage(self._DEFAULT_SYSTEM_MESSAGE)]

    @property
    def _messages(self) -> list[dict[str, str]]:
        return [asdict(message) for message in self.history]

    def _call_api(self) -> openai.openai_object.OpenAIObject:
        completion = openai.ChatCompletion.create(  # type: ignore[no-untyped-call]
            model=self._MODEL_NAME,
            messages=self._messages,
        )
        assert isinstance(completion, openai.openai_object.OpenAIObject)
        return completion

    def __call__(self, message: str) -> tuple[str, int]:
        self.history.append(UserMessage(message))
        completion = self._call_api()
        reply = completion.choices[0].message.content
        num_tokens = completion.usage.total_tokens
        self.history.append(AssistantMessage(reply))
        return reply, num_tokens
