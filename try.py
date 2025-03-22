from utils.decorators import run_sync
import asyncio, time

def w(i):
    print("hello", i)
    time.sleep(5)
    print("world", i)
async def main(i):
    await run_sync(w)(str(i))

async def main2():
    for i in range(10):
        asyncio.create_task(main(i))
asyncio.run(main2())
while 1:
    pass