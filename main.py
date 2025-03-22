from cprint import cprint
from utils.logger import initLogger
import sys
from loguru import logger
from config.config import config
from watchdog.observers import Observer
from utils.changeHandler import ConfigChangeHandler
from robot import run
import traceback
import asyncio

Legend_Logo = """

██╗     ███████╗ ██████╗ ███████╗███╗   ██╗██████╗ 
██║     ██╔════╝██╔════╝ ██╔════╝████╗  ██║██╔══██╗
██║     █████╗  ██║  ███╗█████╗  ██╔██╗ ██║██║  ██║
██║     ██╔══╝  ██║   ██║██╔══╝  ██║╚██╗██║██║  ██║
███████╗███████╗╚██████╔╝███████╗██║ ╚████║██████╔╝
╚══════╝╚══════╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚═════╝ 
"""

Author = "Kanwuqing"

Version = "v1.0.0 | 春暖花开"
async def main():
    if config.autoRestart:
        # 设置监控
        observer = Observer()
        handler = ConfigChangeHandler()
        observer.schedule(handler, str(config.configPath.parent), recursive=False)
        observer.schedule(handler, str(config.pluginsPath), recursive=True)
        observer.start()

        logger.success('监控已启动')

        try:
            await run()
        except KeyboardInterrupt:
            logger.info('用户手动停止')
            observer.stop()
            observer.join()
        except Exception as e:
            logger.error(f"发生错误: {e}")
            logger.error(traceback.format_exc())
            logger.info('等待文件改变后重启...')
            handler.waiting = True

            while handler.waiting:
                await asyncio.sleep(1)
    
    else:
        # 不设置监控
        try:
            await run()
        except KeyboardInterrupt:
            logger.info("收到终止信号，正在关闭...")
        except Exception as e:
            logger.error(f"发生错误: {e}")
            logger.error(traceback.format_exc())
        

if __name__ == "__main__":    
    cprint.info(Legend_Logo)
    cprint.info(Author)
    cprint.info(Version)

    initLogger()
    
    asyncio.run(main())