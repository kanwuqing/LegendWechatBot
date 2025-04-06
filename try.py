import requests
import time
from queue import Queue
from threading import Thread, Event
from concurrent.futures import ThreadPoolExecutor

# 定义队列和线程池
message_queue = Queue()
stop_event = Event()  # 用于控制消息处理线程的运行状态
executor = ThreadPoolExecutor(max_workers=3)  # 限制并发线程数为 3

def generate_video(input_text: str):
    """调用视频生成 API"""
    try:
        print(f"开始处理: {input_text}")
        # 确保 API URL 和参数正确
        api_url = "https://open.bigmodel.cn/api/paas/v4/images/generations"
        payload = {
            "model": "cogview-3-flash",  # 确保模型名称正确
            "prompt": input_text,        # 确保输入内容符合要求
        }
        headers = {
            "Authorization": "Bearer 061a93ffc71a2074e76fcfca2b5dba24.uHnrTsPScPcmYhFT",
            "Content-Type": "application/json",
            "Connection": "close",  # 显式关闭连接
        }

        # 同步请求
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        print(f"状态码: {response.status_code}")
        print(f"响应头: {response.headers}")
        if response.status_code == 200:
            result = response.json()
            print(f"处理完成: {result}")
        else:
            error_message = response.text
            print(f"API 请求失败，状态码: {response.status_code}, 错误信息: {error_message}")
    except Exception as e:
        print(f"调用 API 时发生错误: {e}")

def message_listener():
    """模拟实时监听用户消息"""
    input_texts = [
        "一只可爱的小猫咪",
        "一只勇敢的小狗狗",
        "一片美丽的风景",
        "一只飞翔的鸟儿",
        "一片宁静的湖泊",
    ]
    for text in input_texts:
        print(f"收到新消息: {text}")
        message_queue.put(text)  # 将消息添加到队列
        time.sleep(1)  # 模拟消息间隔

    # 模拟新消息到来
    time.sleep(5)
    new_messages = [
        "一只奔跑的马儿",
        "一片广阔的草原",
    ]
    for text in new_messages:
        print(f"收到新消息: {text}")
        message_queue.put(text)

def process_queue():
    """持续处理队列中的消息"""
    while not stop_event.is_set():  # 当 stop_event 未被设置时持续运行
        try:
            input_text = message_queue.get(timeout=1)  # 等待消息，超时为 1 秒
            executor.submit(generate_video, input_text)  # 提交任务到线程池
            message_queue.task_done()  # 标记任务完成
        except Exception:
            pass  # 队列为空时继续循环

def main():
    """主函数"""
    # 创建并启动消息监听线程
    listener_thread = Thread(target=message_listener)
    listener_thread.start()

    # 创建并启动消息处理线程
    processor_thread = Thread(target=process_queue)
    processor_thread.start()

    # 等待消息监听线程完成
    listener_thread.join()

    # 停止消息处理线程
    stop_event.set()
    processor_thread.join()

    # 关闭线程池
    executor.shutdown(wait=True)

if __name__ == "__main__":
    main()