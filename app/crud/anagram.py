import os

import aioredis

from app.utils import is_anagram


REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')


async def anagram_check(str_1: str, str_2: str):
    redis = await aioredis.from_url('redis://redis', password=REDIS_PASSWORD)
    anagram = is_anagram(str_1, str_2)
    if anagram:
        await redis.incr('anagram_counter', 1)
    anagram_counter = await redis.get('anagram_counter')

    return {'str_1': str_1, 'str_2': str_2, 'is_anagram': anagram, 'anagram_counter': anagram_counter}