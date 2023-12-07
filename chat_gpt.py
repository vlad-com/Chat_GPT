import os
import openai
from openai import AsyncOpenAI
import g4f
from config import OPENAI_API_KEY, MODEL

openai.api_key = OPENAI_API_KEY
client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def g4f_generate_text(messages, userid):
    return await g4f.ChatCompletion.create_async(
        provider=g4f.Provider.GeekGpt,
        model=MODEL,
        messages=messages,
    )


async def g4f_generate_text_chunks(messages, userid):
    return await g4f.ChatCompletion.create_async(
        provider=g4f.Provider.GeekGpt,
        model=MODEL,
        messages=messages,
        stream=True,
    )


async def generate_text(messages, userid):
    completion = await client.chat.completions.create(
        model=MODEL,
        messages=messages,
        user=str(userid),
        max_tokens=2500,
        temperature=0.7,
        frequency_penalty=0,
        presence_penalty=0,
    )
    return completion.choices[0].text


async def generate_text_chunks(messages, userid):
    return await client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=2500,
        temperature=0.7,
        frequency_penalty=0,
        presence_penalty=0,
        user=str(userid),
        stream=True,
    )


async def generate_image(prompt):
    response = await client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="512x512",
        quality="standard",
        n=1,
    )

    return response.data[0].url


async def whisper(path):
    size = os.path.getsize(path)
    if size < 25000000:
        audio_file = open(path, "rb")
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file, 
            response_format="text"
        )
        return transcript
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
