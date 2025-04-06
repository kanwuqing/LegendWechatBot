import asyncio
from loguru import logger
from datetime import datetime, timedelta
from typing import Optional, List

from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, delete
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_scoped_session
from sqlalchemy.orm import declarative_base, sessionmaker
from config.config import config
from wcferry import WxMsg

from utils.singleton import Singleton

# 使用新的声明式基类
DeclarativeBase = declarative_base()


class Message(DeclarativeBase):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    msg_id = Column(Integer, index=True, comment='消息唯一ID(整型)')
    type = Column(Integer, comment='消息类型')
    timestamp = Column(DateTime, default=datetime.now, index=True, comment='消息时间戳')
    xml = Column(Text, comment='消息原始xml')
    content = Column(Text, comment='消息内容')
    extra = Column(Text, comment='消息额外信息')
    thumb = Column(Text, comment='消息缩略图')
    sender = Column(String(40), index=True, comment='消息发送人wxid')
    roomid = Column(String(40), default=None, index=True, comment='消息所在群聊wxid')
    is_at = Column(Boolean, default=False, comment='是否被at')


class MessageDB(metaclass=Singleton):
    _instance = None

    def __new__(cls):
        db_url = config.DBConfig["msgDB-url"]

        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.engine = create_async_engine(
                db_url,
                echo=False,
                future=True
            )
            cls._async_session_factory = async_scoped_session(
                sessionmaker(
                    cls._instance.engine,
                    class_=AsyncSession,
                    expire_on_commit=False
                ),
                scopefunc=asyncio.current_task
            )
            cls._instance._lock = asyncio.Lock()
        return cls._instance

    async def initialize(self):
        """异步初始化数据库"""
        async with self.engine.begin() as conn:
            # await conn.run_sync(DeclarativeBase.metadata.drop_all)
            await conn.run_sync(DeclarativeBase.metadata.create_all)

    async def save_message(self, msg: WxMsg, self_wxid) -> bool:
        """异步保存消息到数据库"""
        async with self._lock:
            async with self._async_session_factory() as session:
                try:
                    message = Message(
                        msg_id=msg.id,
                        type=msg.type,
                        xml=msg.xml,
                        content=msg.content,
                        extra=msg.extra,
                        sender=msg.sender,
                        roomid=msg.roomid,
                        thumb=msg.thumb,
                        is_at=msg.is_at(self_wxid),
                        timestamp=datetime.now()
                    )
                    session.add(message)
                    await session.commit()
                    return True
                except Exception as e:
                    logger.error(f"保存消息失败: {str(e)}")
                    await session.rollback()
                    return False

    async def get_messages(self,
                           msg_id: Optional[int] = None,
                           start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None,
                           sender: Optional[str] = None,
                           roomid: Optional[str] = None,
                           type: Optional[int] = None,
                           is_at: Optional[bool] = None,
                           limit: int = 100) -> List[Message]:
        """异步查询消息记录"""
        async with self._async_session_factory() as session:
            try:
                query = select(Message).order_by(Message.timestamp.desc()).limit(limit)
                if msg_id:
                    query = query.where(Message.msg_id == msg_id)
                if start_time:
                    query = query.where(Message.timestamp >= start_time)
                if end_time:
                    query = query.where(Message.timestamp <= end_time)
                if sender:
                    query = query.where(Message.sender == sender)
                if roomid:
                    query = query.where(Message.roomid == roomid)
                if type is not None:
                    query = query.where(Message.type == type)
                if is_at is not None:
                    query = query.where(Message.is_at == is_at)

                result = await session.execute(query)
                return result.scalars().all()
            except Exception as e:
                logger.error(f"查询消息失败: {str(e)}")
                return []

    async def close(self):
        """关闭数据库连接"""
        await self.engine.dispose()

    async def cleanup_messages(self):
        """每三天清理旧消息"""
        while True:
            async with self._async_session_factory() as session:
                try:
                    # 计算三天前的时间
                    three_days_ago = datetime.now() - timedelta(days=3)
                    # 删除三天前的消息
                    await session.execute(
                        delete(Message).where(Message.timestamp < three_days_ago)
                    )
                    await session.commit()
                except Exception as e:
                    logger.error(f"清理消息失败: {str(e)}")
                    await session.rollback()
            await asyncio.sleep(259200)  # 每三天（259200秒）执行一次

    async def __aenter__(self):
        # 启动清理消息的定时任务
        asyncio.create_task(self.cleanup_messages())
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()