from openai import OpenAI
from openai.types.responses import (
    EasyInputMessageParam,
    ResponseInputParam,
    ResponseTextDeltaEvent,
    ResponseReasoningSummaryTextDeltaEvent,
)

from colorama import Fore


class Agent:
    def __init__(self) -> None:
        self.client = OpenAI()
        self.messages: ResponseInputParam = []
        self.model = "gpt-5-nano"

    def append_prompt(self, prompt: str) -> None:
        message: EasyInputMessageParam = {
            "role": "user",
            "content": prompt,
        }
        self.messages.append(message)

    def send_and_stream_response(self):
        with self.client.responses.stream(
            input=self.messages, model=self.model
        ) as stream:
            for event in stream:
                if isinstance(event, ResponseTextDeltaEvent):
                    print(Fore.WHITE + event.delta, end="", flush=True)
                elif isinstance(event, ResponseReasoningSummaryTextDeltaEvent):
                    print(Fore.WHITE + event.delta, end="", flush=True)

        final_response = stream.get_final_response()
        for item in final_response:
            for content in item:
                self.messages.append({"role": "assistant", "content": str(content)})
        return final_response
