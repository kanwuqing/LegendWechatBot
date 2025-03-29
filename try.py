from utils.decorators import run_sync
import asyncio, time, aiohttp
import openai

def w(i):
    print("hello", i)
    time.sleep(5)
    print("world", i)
async def main():
    # async with aiohttp.ClientSession() as session:
    #     async with session.get(f'https://api.zvv.quest/search?q=自信&n=1') as response:
    #         res = await response.json()
    # print(res)
    print(1)
    response = await client.chat.completions.create(
        model='deepseek/deepseek-chat-v3-0324:free',  # 使用的模型
        messages=[
            # {"role": "system", "content": "你是一个帮助用户回答问题的助手。"},
            {"role": "user", "content": '你好'}
        ],
    )
    print(response.choices[0].message.content)

asyncio.run(main())
while 1:
    pass