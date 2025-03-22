from watchdog.events import FileSystemEventHandler, FileSystemEvent
import time
from pathlib import Path
from loguru import logger
import sys
import os
import subprocess

def restartProgram(observer=None):
    logger.info("正在重启程序...")
    # 清理资源
    if observer:
        observer.stop()
    try:
        import multiprocessing.resource_tracker
        multiprocessing.resource_tracker._resource_tracker.close()
    except Exception as e:
        logger.warning(f"清理资源时出错: {e}")
    # 重启程序
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    os.execv(sys.executable, [sys.executable] + sys.argv)

class ConfigChangeHandler(FileSystemEventHandler):
    def __init__(self, restartCallback = restartProgram):
        '''初始化配置文件变化处理器
        :param restartCallback: 重启回调函数, 默认为None, 即不执行任何操作
        '''
        self.restartCallback = restartCallback
        self.lastTriggered = 0
        self.cooldown = 2  # 冷却时间(秒)
        self.waiting = False  # 是否在等待文件改变

    def onModified(self, event: FileSystemEvent):
        if not event.is_directory:
            # 判断是否在冷却时间内
            currentTime = time.time()
            if currentTime - self.last_triggered < self.cooldown:
                return

            filePath = Path(event.src_path).resolve()
            if (filePath.name == "config.yaml" or
                    "plugins" in str(filePath) and filePath.suffix in ['.py', '.yaml']):
                logger.info(f"检测到文件变化: {filePath}")
                self.last_triggered = currentTime
                if self.waiting:
                    logger.info("检测到文件改变，正在重启...")
                    self.waiting = False
                self.restartCallback()