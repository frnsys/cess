import asyncio
from functools import wraps
from cess.agent import Agent


def async(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)
    return wrapper


class TestAgent(Agent):
    def multiply(self, num):
        return num * 2
