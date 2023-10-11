import os
import openai
from config import OPENAI_API_KEY, MODEL

openai.api_key = OPENAI_API_KEY


async def generate_text(messages, userid):
    completion = await openai.ChatCompletion.acreate(
        model=MODEL,
        messages=messages,
        max_tokens=2500,
        temperature=0.7,
        frequency_penalty=0,
        presence_penalty=0,
        user=userid
    )
    return completion.choices[0]['message']['content']


async def generate_text_chunks(messages, userid):
    return await openai.ChatCompletion.acreate(
        model=MODEL,
        messages=messages,
        max_tokens=2500,
        temperature=0.7,
        frequency_penalty=0,
        presence_penalty=0,
        user=userid,
        stream=True,
    )


async def generate_image(prompt):
    response = await openai.Image.acreate(
        prompt=prompt,
        n=1,
        size="512x512",
        response_format="url",
    )

    return response['data'][0]['url']


async def whisper(path):
    size = os.path.getsize(path)
    if size < 25000000:
        audio_file = open(path, "rb")
        transcript = await openai.Audio.atranscribe(
            model="whisper-1",
            file=audio_file,
        )
        return transcript["text"]
    else:
        raise Exception("Input file is to large(>25 Mb)")


# tg limit 4096 symbols
def message_to_tg_chunks(s):
    maxlength = 4090
    start = 0
    end = 0
    while start + maxlength < len(s) and end != -1:
        end = s.rfind(" ", start, start + maxlength + 1)
        yield s[start:end]
        start = end + 1
    yield s[start:]
