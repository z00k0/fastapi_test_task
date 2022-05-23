import os

import aioredis
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
app = FastAPI()


def is_anagram(str_1: str, str_2: str):
    return sorted(str_1) == sorted(str_2)


@app.post('/check/')
async def check(str_1: str, str_2: str):
    redis = aioredis.from_url("redis://localhost", password=REDIS_PASSWORD)
    anagram = is_anagram(str_1, str_2)
    if anagram:
        await redis.incr('anagram_counter', 1)
    anagram_counter = await redis.get('anagram_counter')

    return {'str_1': str_1, 'str_2': str_2, 'is_anagram': anagram, 'anagram_counter': anagram_counter}

