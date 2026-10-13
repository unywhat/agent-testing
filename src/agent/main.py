from openai import OpenAI

client = OpenAI(
    base_url='http://127.0.0.1:1919/v1',
    api_key='unused'
)

response = client.chat.completions.create(
    model="Qwen3.6-35B-A3B-NVFP4",
    messages=[
        {
            "role": "user",
            "content": "Hello!"
        }
    ],
    stream=True
)

for chunk in response:
    try:
        print(f'\033[90m{getattr(chunk.choices[0].delta, 'reasoning_content')}', end="", flush=True)
    except AttributeError:
        content = chunk.choices[0].delta.content
        if content:
            print(f'\033[97m{content}', end="", flush=True)

print('\033[0m\n')