from asyncio import Lock
from collections import defaultdict


class Counter:

    def __init__(self):
        self._lock = Lock()
        self._value = 0

    @property
    def value(self):
        return self._value

    async def increment(self):
        async with self._lock:
            self._value += 1

    async def decrement(self):
        async with self._lock:
            self._value -= 1


viewers = defaultdict(Counter)
