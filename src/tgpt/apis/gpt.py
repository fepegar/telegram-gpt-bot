from dataclasses import asdict
from dataclasses import dataclass

import openai

from .exchange import usd_to_gbp


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


class GPT:
    _MODEL_NAME: str
    _PRICING_USD: float
    _DEFAULT_SYSTEM_MESSAGE = (
        "You are ChatGPT, a large language model trained by OpenAI."
        " Answer as concisely as possible."
    )

    def __init__(self) -> None:
        self.history: list[SystemMessage | UserMessage | AssistantMessage]
        self.history = [SystemMessage(self._DEFAULT_SYSTEM_MESSAGE)]

    @property
    def gbp_per_token(self) -> float:
        return usd_to_gbp(self._PRICING_USD)

    def cost_gbp(self, num_tokens: int) -> float:
        return num_tokens * self.gbp_per_token

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

    def __call__(self, message: str) -> tuple[str, float]:
        self.history.append(UserMessage(message))
        completion = self._call_api()
        reply = completion.choices[0].message.content
        self.history.append(AssistantMessage(reply))
        num_tokens = completion.usage.total_tokens
        cost_gbp = self.cost_gbp(num_tokens)
        return reply, cost_gbp


class ChatGPT(GPT):
    _MODEL_NAME = "gpt-3.5-turbo"
    _PRICING_USD = 0.002 / 1000  # $0.002 per 1000 tokens


class GPT4(GPT):
    _MODEL_NAME = "gpt-4"
    _PRICING_USD = 0.03 / 1000  # $0.03 per 1000 tokens
