import asyncio

from typing import Callable, Any, TypeVar

T = TypeVar("T")

async def with_retries(fn: Callable[[], Any], retries: int = 3, base_delay: float = 0.5):
    last_exc = None
    for i in range(retries):
        try:
            return await fn()
        except Exception as e:
            last_exc = e
            await asyncio.sleep(base_delay * (2 ** i))
    if last_exc:
        raise last_exc