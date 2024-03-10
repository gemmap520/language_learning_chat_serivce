import os
from io import BytesIO
from tempfile import NamedTemporaryFile

import openai
import pygame

from dotenv import load_dotenv
from gtts import gTTS

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def gpt_query(user_query: str, skip_save: bool = False) -> str:
    "Returns a response to a user message."

    global messages

    messages.append({
        "role": "user",
        "content": user_query,
    })

    response = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
    assistant_message = response.choices[0].message.content

    if skip_save is False:
        messages.append({
            "role": "assistant",
            "content": assistant_message,
        })

    return assistant_message


def play_file(file_path: str) -> None:
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pass

    pygame.mixer.quit()


def say(message: str, lang: str) -> None:
    io = BytesIO()

    gTTS(message, lang=lang).write_to_fp(io)

    with NamedTemporaryFile() as f:
        f.write(io.getvalue())
        play_file(f.name)


def main():
    assistant_message = gpt_query(USER_PROMPT)
    print(f"[assistant] {assistant_message}")
    say(assistant_message, "en")

    while line := input("[user] ").strip():
        if line == "!recommend":
            recommended_message = gpt_query(RECOMMEND_PROMPT, skip_save=True)
            print("Recommended message: ", recommended_message)
        elif line == "!say":
            say(messages[-1]["content"], "en")
        else:
            response = gpt_query(line)
            print(f"[assistant] {response}")
            say(response, "en")


if __name__ == "__main__":
    main()
