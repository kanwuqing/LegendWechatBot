from loguru import logger
import os
from datetime import datetime
from cprint import cprint
import sys

def initLogger():
    '''初始化日志记录器'''

    # 移除默认的日志处理器
    logger.remove()
    log_dir = "logs"
    # 如果日志目录不存在，则创建
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 创建文件处理器
    date_str = datetime.now().strftime("%Y-%m-%d")
    # 定义日志文件路径
    all_log_path = os.path.join(log_dir, f"{date_str}_all.log")
    error_log_path = os.path.join(log_dir, f"{date_str}_error.log")

    # 添加日志文件处理器
    logger.add(all_log_path, level="INFO", format="{time:YYYY-MM-DD HH:mm:ss} | <level>{level: <8}</level> | <cyan>{module}</cyan>:<magenta>{line}</magenta> - <level>{message}</level>")
    logger.add(error_log_path, level="ERROR", format="{time:YYYY-MM-DD HH:mm:ss} | <level>{level: <8}</level> | <cyan>{module}</cyan>:<magenta>{line}</magenta> - <level>{message}</level>")
    # 添加自定义控制台输出处理器
    logger.add(sys.stdout, level="DEBUG", format="{time:YYYY-MM-DD HH:mm:ss} | <level>{level: <8}</level> | <cyan>{module}</cyan>:<magenta>{line}</magenta> - <level>{message}</level>")

    logger.success("日志记录器初始化完成")