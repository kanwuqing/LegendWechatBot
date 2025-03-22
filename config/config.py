import os
import asyncio
import yaml
from pathlib import Path
from loguru import logger
import shutil

class Config:
    def __init__(self):
        self.scriptDir = Path(__file__).resolve().parent.parent
        os.chdir(self.scriptDir)
        logger.info(f'当前工作目录：{self.scriptDir}')

        if not os.path.exists(self.scriptDir / 'config/config.yaml'):
            shutil.copyfile(self.scriptDir / 'config/config.example.yaml', self.scriptDir / 'config/config.yaml')

        with open('config/config.yaml', 'r', encoding='utf-8') as f:
            c = yaml.safe_load(f)
        logger.success('加载配置文件成功')

        self.configPath = self.scriptDir / 'config.yaml'
        self.pluginsPath = self.scriptDir / 'plugins'
        
        self.autoRestart = c.get('autoRestart', False)
        self.protection = c.get('protection', True)
        self.banWord = c.get('banWord', True)

        self.RobotConfig = c['LegendBot']
        self.DBConfig = c['DataBase']

        self.admin = self.RobotConfig.get('admin')

        logger.success('初始化配置成功')

config = Config()
# asyncio.run(config.initialize(), debug=True)