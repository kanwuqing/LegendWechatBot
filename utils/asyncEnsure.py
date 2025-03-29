import asyncio
import time
import threading

class LegendSemaphore(asyncio.Semaphore):
    def __init__(self, value, interval):
        super().__init__(value)
        self._interval = interval
        self._max_requests = value
        self._request_times = []

    async def acquire(self):
        await super().acquire()
        now = time.monotonic()
        
        # 清理过期的请求时间
        self._request_times = [t for t in self._request_times if now - t < self._interval]
        
        if len(self._request_times) >= self._max_requests:
            sleep_time = self._interval - (now - self._request_times[0])
            await asyncio.sleep(sleep_time)
            self._request_times = self._request_times[1:]
        
        self._request_times.append(time.monotonic())

    def release(self):
        super().release()

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.release()

sem = {
    'processAI': LegendSemaphore(5, 6),
    'GLM-4-Flash': asyncio.Semaphore(200),
    'GLM-4V-Flash': asyncio.Semaphore(10),
    'CogView-3-Flash': asyncio.Semaphore(5),
    'CogVideoX-Flash': asyncio.Semaphore(3),
}

# 示例异步函数，演示如何使用 LegendSemaphore
async def main():
    async with sem['processMsg']:
        print("Acquired semaphore")
        await asyncio.sleep(1)
        print("Releasing semaphore")

async def m():
    t = []
    for _ in range(20):
        t.append(asyncio.create_task(main()))
    await asyncio.gather(*t)

if __name__ == "__main__":
    # for _ in range(10):
    #     t.append(asyncio.create_task(main()))
    # asyncio.gather(*t).run_until_complete()
    asyncio.run(m())