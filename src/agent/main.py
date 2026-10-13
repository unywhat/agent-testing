from openai import OpenAI
from platform import system
from subprocess import run
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit import HTML
import tomllib

operating_system = system()


def get_config():
    with open('config.toml', 'rb') as cfg:
        return tomllib.load(cfg)


config = get_config()
print(config)


def clear_screen():
    if operating_system == "Windows":
        run(["cls"])
    elif operating_system in ["Linux", "Darwin"]:
        run(["clear"])


def setup_client():
    api_key = config['optional']['api_key']
    if not api_key:
        api_key = "unused"

    return OpenAI(
        base_url=config['general']['base_url'],
        api_key=api_key
    )


# clear_screen()
client = setup_client()

input_area = PromptSession(history=FileHistory('.promptHistory'))
user_input = input_area.prompt(HTML('<white><b>&gt; </b></white>'), multiline=True)

response = client.chat.completions.create(
    model=config['general']['model'],
    messages=[
        {
            "role": "user",
            "content": user_input
        }
    ],
    stream=True
)

for chunk in response:
    try:
        if config['general']['show_reasoning']:
            print(f'\033[90m{getattr(chunk.choices[0].delta, 'reasoning_content')}', end="", flush=True)
        else:
            raise AttributeError
    except AttributeError:
        content = chunk.choices[0].delta.content
        if content:
            print(f'\033[97m{content}', end="", flush=True)

print('\033[0m\n')