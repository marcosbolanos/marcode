import json
import os, random
from collections.abc import Iterator
from types import TracebackType
from typing import Any, Self, cast

from openai.resources.responses import Responses
from openai.types.responses import (
    ParsedResponse,
    ParsedResponseFunctionToolCall,
    ResponseTextDeltaEvent,
)

from marcode.agent.agent import Agent


os.environ["OPENAI_API_KEY"] = "foo bar"

class MockStream:
    def __init__(self):
        self.final_response: list[list[str]] = [['']]
    
    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        return False

    def __iter__(self) -> Iterator[ResponseTextDeltaEvent]:
        # yield 10 chunks
        for i in range(10):
            # generate a random string
            delta = random.choices("azertyuiopqsdfghjklmwxcvbn:,;", k=3)
            yield ResponseTextDeltaEvent(
                content_index=0,
                delta=delta[0],
                item_id=str(i),
                logprobs=[],
                output_index=0,
                sequence_number=0,
                type="response.output_text.delta",
            )
            self.final_response[0][0] += delta[0]

    def get_final_response(self) -> list[list[str]]:
        return self.final_response


def mock_responses_stream(*args, **kwargs: Any) -> MockStream:
    return MockStream()


# we stream the agent response and then check it's also present in latest message
def test_content_is_added_to_messages(monkeypatch):
    # mock stream means fast testing without connection
    monkeypatch.setattr(Responses, "stream", mock_responses_stream)
    agent = Agent()

    agent.append_prompt("foobar")
    final_response = agent.send_and_stream_response()

    for item in final_response:
        for content in item:
            assert content in agent.messages[-1]["content"] # type:ignore
    return


_tool_output_exec_item = ParsedResponseFunctionToolCall(
        name="exec",
        arguments=json.dumps({"command": "echo 'hello world'"}),
        call_id="foobar",
        type='function_call'
    )

_mock_exec_final_response = ParsedResponse(
        id="response-42",
        created_at=42,
        model="gpt-5-nano",
        object='response',
        parallel_tool_calls=False,
        tools=[],
        tool_choice='auto',
        output=[
            _tool_output_exec_item
        ]
    )
# we test that the tool calling function will handle command execution
# we also test that outputs are added back to messages
def test_exec_tool_handler():
    agent = Agent()
    
    agent.handle_tool_calls(_mock_exec_final_response)

    tool_output = cast(dict[str, Any], agent.messages[-1])
    assert tool_output["type"] == "function_call_output"
    assert tool_output["call_id"] == "foobar"
    output = json.loads(tool_output["output"])
    assert output["returncode"] == 0
    assert output["stdout"] == "hello world\n"

