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


async def generate_image(prompt):
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="512x512",
        response_format="url",
    )

    return response['data'][0]['url']
