import os

from dotenv import load_dotenv
from colorama import init, Fore

from marcode.agent.agent import Agent


def entrypoint():
    init(autoreset=True)
    load_dotenv()
    if not os.environ.get("OPENAI_API_KEY"):
        print(Fore.LIGHTBLACK_EX + "\nsorry, no API key was found!")
        return 1

    agent = Agent()
    print(Fore.CYAN + "welcome to marcode!\n")
    try:
        while True:
            prompt = input(Fore.CYAN + "> ")
            agent.append_prompt(prompt)
            agent.send_and_stream_response()
            print()
    except KeyboardInterrupt:
        print(Fore.LIGHTBLACK_EX + "\ngoodbye!")
        return 0
