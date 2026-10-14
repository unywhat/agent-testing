from openai import OpenAI
from platform import system
from subprocess import run
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit import HTML
import tomllib

operating_system = system()
status_icons = "✧◇◈∴⟡∵⚙✴✳✦"


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
    tools=[
      {
        "type": "function",
        "function": {
          "name": "get_weather",
          "description": "Get weather for a city",
          "parameters": {
            "type": "object",
            "properties": {
              "city": {"type": "string"}
            },
            "required": ["city"]
          }
        }
      }
    ],
    tool_choice="auto",
    stream=True
)

tool_calls = {}

for chunk in response:
    if chunk.choices[0].delta.tool_calls:
        tool_delta = chunk.choices[0].delta.tool_calls[0]
        tool_idx = tool_delta.index

        if tool_idx not in tool_calls:
            tool_calls[tool_idx] = {
                "id": "",
                "arguments": "",
                "name": ""
            }

        if tool_delta.id:
            tool_calls[tool_idx]["id"] += tool_delta.id
        if tool_delta.function.arguments:
            tool_calls[tool_idx]["arguments"] += tool_delta.function.arguments
        if tool_delta.function.name:
            tool_calls[tool_idx]["name"] += tool_delta.function.name
        continue
    try:
        if config['general']['show_reasoning']:
            print(f'\033[90m{getattr(chunk.choices[0].delta, 'reasoning_content')}', end="", flush=True)
        else:
            raise AttributeError
    except AttributeError:
        content = chunk.choices[0].delta.content
        if content:
            print(f'\033[97m{content}', end="", flush=True)

    for idx in tool_calls:
        tool_call = tool_calls[idx]
        print(tool_call)

print('\033[0m\n')