from typing import Final

from openai.types.responses import ResponseInputParam, FunctionToolParam

system_prompt = """
You are a coding agent. You can run commands, or send the user a response.
Responding interrupts your execution loop, so only do so after having thoroughly explored
the problem and you either solved it or ran into a blocking problem.
To do so, you can use your command execution tool. When done, use the respond tool to respond to the user.
"""

conversation: ResponseInputParam = [{"role": "developer", "content": system_prompt}]

tools: Final[list[FunctionToolParam]] = [
    {
        "type": "function",
        "name": "exec",
        "description": "Execute a shell command",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command to execute"}
            },
            "required": ["command"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "respond",
        "description": "Stop the loop and respond to the user",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "message to give to the user",
                }
            },
            "required": ["message"],
            "additionalProperties": False,
        },
    },
]
