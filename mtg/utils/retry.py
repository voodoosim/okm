import asyncio
import random

async def exponential_backoff(attempt, base_delay=1, max_delay=30):
    """지수 백오프 지연 계산"""
    delay = min(base_delay * (2 ** attempt) + random.uniform(0, 0.1), max_delay)
    await asyncio.sleep(delay)
    return delay

async def retry_with_backoff(func, max_attempts=5, *args, **kwargs):
    """지수 백오프으로 함수 재시도"""
    for attempt in range(max_attempts):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt == max_attempts - 1:
                raise e
            await exponential_backoff(attempt)
    raise Exception("최대 재시도 횟수 초과")
