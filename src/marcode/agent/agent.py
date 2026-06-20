import subprocess, json

from pydantic import BaseModel

from openai import OpenAI
from openai.types.responses import (
    EasyInputMessageParam,
    ParsedResponse,
    ResponseInputParam,
    ResponseTextDeltaEvent,
    ResponseReasoningSummaryTextDeltaEvent,
    ResponseFunctionToolCall,
)

from colorama import Fore
from marcode.agent.prompts import tools, system_prompt


class ExecArguments(BaseModel):
    command: str


class RespondArguments(BaseModel):
    message: str


class Agent:
    def __init__(self) -> None:
        self.client = OpenAI()
        self.messages: ResponseInputParam = [
            {"role": "system", "content": system_prompt}
        ]
        self.model = "gpt-5-nano"
        self.tools = tools

    def append_prompt(self, prompt: str) -> None:
        message: EasyInputMessageParam = {
            "role": "user",
            "content": prompt,
        }

        self.messages.append(message)

    def send_and_stream_response(self):
        with self.client.responses.stream(
            input=self.messages, model=self.model, tools=self.tools
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

    def handle_tool_calls(self, response: ParsedResponse):
        tool_outputs: ResponseInputParam = []
        for output_item in response.output:
            if isinstance(output_item, ResponseFunctionToolCall):
                try:
                    if output_item.name == "exec":
                        arguments = ExecArguments.model_validate_json(
                            output_item.arguments
                        )
                        print(f"EXECUTION: \n\n {arguments.command}")
                        result = subprocess.run(
                            arguments.command,
                            capture_output=True,
                            text=True,
                            shell=True,
                            check=False,
                        )
                        tool_output = json.dumps(
                            {
                                "returncode": result.returncode,
                                "stdout": result.stdout,
                                "stderr": result.stderr,
                            }
                        )
                    elif output_item.name == "respond":
                        arguments = RespondArguments.model_validate_json(
                            output_item.arguments
                        )
                        print(f"RESPONSE: \n\n {arguments.message}")
                        return
                    else:
                        tool_output = json.dumps(
                            {"error": f"Unknown tool: {output_item.name}"}
                        )

                except Exception as error:
                    tool_output = json.dumps({"error": str(error)})

                tool_outputs.append(
                    {
                        "type": "function_call_output",
                        "call_id": output_item.call_id,
                        "output": tool_output,
                    }
                )
        self.messages += tool_outputs
