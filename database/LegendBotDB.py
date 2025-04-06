import datetime
import tomllib
from concurrent.futures import ThreadPoolExecutor
from typing import Union

from loguru import logger
from sqlalchemy import Column, String, Integer, DateTime, create_engine, JSON, Boolean, Text
from sqlalchemy import update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from config.config import config
from utils.singleton import Singleton

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    wxid = Column(String(20), primary_key=True, nullable=False, unique=True, index=True, autoincrement=False, comment='wxid')
    points = Column(Integer, nullable=False, default=0, comment='points')
    running = Column(Integer, nullable=False, default=False, comment='running')
    blacked = Column(Integer, nullable=False, default=-2, comment='black')
    lastSign = Column(DateTime, default=None, comment='lastSign')
    maxSign = Column(Integer, nullable=False, default=0, comment='maxSign')
    fortune = Column(Text, default=None, comment='fortune')


class Chatroom(Base):
    __tablename__ = 'chatroom'

    chatroom_id = Column(String(20), primary_key=True, nullable=False, unique=True, index=True, autoincrement=False, comment='chatroom_id')
    members = Column(JSON, nullable=False, default=list, comment='members')
    whitelist = Column(Boolean, nullable=False, default=False, comment='whitelist')


class LegendBotDB(metaclass=Singleton):
    def __init__(self, flag=False):
        self.database_url = config.DBConfig["LegendBotDB-url"]
        self.engine = create_engine(self.database_url)
        self.DBSession = sessionmaker(bind=self.engine)

        if flag:
            self.reset_all_running_stat()

        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="database")

    def recreate(self):
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

    def _execute_in_queue(self, method, *args, **kwargs):
        """在队列中执行数据库操作"""
        future = self.executor.submit(method, *args, **kwargs)
        try:
            return future.result(timeout=20)  # 20秒超时
        except Exception as e:
            logger.error(f"数据库操作失败: {method.__name__} - {str(e)}")
            raise

    # USER

    def get_black(self, wxid: str) -> int:
        return self._execute_in_queue(self._get_black, wxid)

    def _get_black(self, wxid: str) -> int:
        session = self.DBSession()
        try:
            user = session.query(User).filter_by(wxid=wxid).first()
            return user.blacked if user else False
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"获取用户 {wxid} 黑名单状态失败: {e}")
            return False
        finally:
            session.close()

    def add_black(self, wxid: str, n: int) -> bool:
        return self._execute_in_queue(self._add_black, wxid, n)

    def _add_black(self, wxid: str, n: int) -> bool:
        session = self.DBSession()
        try:
            result = session.execute(
                update(User)
                .where(User.wxid == wxid)
                .values(blacked=User.blacked + n)
            )
            if result.rowcount == 0:
                session.add(User(wxid=wxid, blacked=n))
            logger.info(f"用户 {wxid} 黑名单状态更新成功")
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"更新用户 {wxid} 黑名单状态失败: {e}")
            return False
        finally:
            session.close()

    def get_running(self, wxid: str) -> bool:
        return self._execute_in_queue(self._get_running, wxid)

    def _get_running(self, wxid: str) -> bool:
        session = self.DBSession()
        try:
            user = session.query(User).filter_by(wxid=wxid).first()
            return user.running if user else False
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"获取用户 {wxid} 运行状态失败: {e}")
            return False
        finally:
            session.close()

    def set_running(self, wxid: str, running: bool) -> bool:
        return self._execute_in_queue(self._set_running, wxid, running)

    def _set_running(self, wxid: str, running: bool) -> bool:
        session = self.DBSession()
        try:
            result = session.execute(
                update(User)
                .where(User.wxid == wxid)
                .values(running=running)
            )
            if result.rowcount == 0:
                session.add(User(wxid=wxid, running=running))
            logger.info(f"用户 {wxid} 运行状态更新成功")
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"更新用户 {wxid} 运行状态失败: {e}")
            return False
        finally:
            session.close()

    def add_points(self, wxid: str, num: int) -> bool:
        return self._execute_in_queue(self._add_points, wxid, num)

    def _add_points(self, wxid: str, num: int) -> bool:
        session = self.DBSession()
        try:
            result = session.execute(
                update(User)
                .where(User.wxid == wxid)
                .values(points=User.points + num)
            )
            if result.rowcount == 0:
                session.add(User(wxid=wxid, points=num))
            logger.info(f"用户 {wxid} 积分增加 {num} 分")
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"用户 {wxid} 积分增加失败: {e}")
            return False
        finally:
            session.close()

    def set_points(self, wxid: str, num: int) -> bool:
        return self._execute_in_queue(self._set_points, wxid, num)

    def _set_points(self, wxid: str, num: int) -> bool:
        session = self.DBSession()
        try:
            result = session.execute(
                update(User)
                .where(User.wxid == wxid)
                .values(points=num)
            )
            if result.rowcount == 0:
                session.add(User(wxid=wxid, points=num))
            logger.info(f"用户 {wxid} 积分设置为 {num} 分")
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"用户 {wxid} 积分设置失败: {e}")
            return False
        finally:
            session.close()

    def get_points(self, wxid: str) -> int:
        return self._execute_in_queue(self._get_points, wxid)

    def _get_points(self, wxid: str) -> int:
        session = self.DBSession()
        try:
            user = session.query(User).filter_by(wxid=wxid).first()
            return user.points if user else 0
        finally:
            session.close()

    def get_signin_stat(self, wxid: str) -> datetime.datetime:
        return self._execute_in_queue(self._get_signin_stat, wxid)

    def _get_signin_stat(self, wxid: str) -> datetime.datetime:
        session = self.DBSession()
        try:
            user = session.query(User).filter_by(wxid=wxid).first()
            return [user.lastSign, user.maxSign, user.fortune] if user else [None, None, None]
        finally:
            session.close()

    def set_signin_stat(self, wxid: str, fortune: str) -> bool:
        return self._execute_in_queue(self._set_signin_stat, wxid, fortune)

    def _set_signin_stat(self, wxid: str, fortune: str) -> bool:
        session = self.DBSession()
        try:
            user = session.query(User).filter_by(wxid=wxid).first()
            if user:
                last_sign = user.lastSign
                max_sign = user.maxSign
                points = user.points

                new_max_sign = max_sign + 1 if last_sign and datetime.datetime.today().date() == (last_sign + datetime.timedelta(days=1)).date() else max_sign
                new_points = points + config.RobotConfig['signPoint'] + min(10, new_max_sign)

                session.execute(
                    update(User)
                    .where(User.wxid == wxid)
                    .values(
                        fortune=fortune,
                        maxSign=new_max_sign,
                        lastSign=datetime.datetime.today(),
                        points=new_points
                    )
                )
            else:
                session.add(User(wxid=wxid, fortune=fortune, maxSign=1, lastSign=datetime.datetime.today(), points=11))

            logger.info(f"用户 {wxid} 签到状态更新成功")
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"用户 {wxid} 签到状态更新失败: {e}")
            return False
        finally:
            session.close()

    def reset_all_running_stat(self) -> bool:
        session = self.DBSession()
        try:
            session.query(User).update({User.running: False})
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"重置所有用户运行状态失败: {e}")

    def get_leaderboard(self, count: int) -> list:
        session = self.DBSession()
        try:
            users = session.query(User).order_by(User.points.desc()).limit(count).all()
            return [(user.wxid, user.points) for user in users]
        finally:
            session.close()

    def safe_trade_points(self, trader_wxid: str, target_wxid: str, num: int) -> bool:
        return self._execute_in_queue(self._safe_trade_points, trader_wxid, target_wxid, num)

    def _safe_trade_points(self, trader_wxid: str, target_wxid: str, num: int) -> bool:
        session = self.DBSession()
        try:
            trader = session.query(User).filter_by(wxid=trader_wxid).with_for_update().first()
            target = session.query(User).filter_by(wxid=target_wxid).with_for_update().first()

            if not trader:
                trader = User(wxid=trader_wxid)
                session.add(trader)
            if not target:
                target = User(wxid=target_wxid)
                session.add(target)
                session.flush()

            if trader.points >= num:
                trader.points -= num
                target.points += num
                session.commit()
                logger.info(f"用户 {trader_wxid} 转账 {num} 积分给用户 {target_wxid}")
                return True
            logger.info(f"转账失败: 用户 {trader_wxid} 积分不足")
            session.rollback()
            return False
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"转账失败: {e}")
            return False
        finally:
            session.close()

    def get_user_list(self) -> list:
        session = self.DBSession()
        try:
            users = session.query(User).all()
            return [user.wxid for user in users]
        finally:
            session.close()

    # CHATROOM

    def get_chatroom_list(self) -> list:
        return self._execute_in_queue(self._get_chatroom_list)

    def _get_chatroom_list(self):
        session = self.DBSession()
        try:
            chatrooms = session.query(Chatroom).filter_by(whitelist=True).all()
            return [chatroom.chatroom_id for chatroom in chatrooms]
        finally:
            session.close()

    def get_chatroom_members(self, chatroom_id: str) -> set:
        session = self.DBSession()
        try:
            chatroom = session.query(Chatroom).filter_by(chatroom_id=chatroom_id).first()
            return set(chatroom.members) if chatroom else set()
        finally:
            session.close()

    def get_chatroom_whitelist(self, chatroom_id: str) -> bool:
        return self._execute_in_queue(self._get_chatroom_whitelist, chatroom_id)

    def _get_chatroom_whitelist(self, chatroom_id: str) -> bool:
        session = self.DBSession()
        try:
            chatroom = session.query(Chatroom).filter_by(chatroom_id=chatroom_id).first()
            return chatroom.whitelist if chatroom else False
        finally:
            session.close()

    def set_chatroom_whitelist(self, chatroom_id: str, whitelist: bool) -> bool:
        session = self.DBSession()
        try:
            chatroom = session.query(Chatroom).filter_by(chatroom_id=chatroom_id).first()
            if not chatroom:
                chatroom = Chatroom(chatroom_id=chatroom_id, whitelist=whitelist)
                session.add(chatroom)
            chatroom.whitelist = whitelist
            logger.info(f"群组 {chatroom_id} 白名单状态更新成功")
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"群组 {chatroom_id} 白名单状态更新失败: {e}")
            return False
        finally:
            session.close()

    def __del__(self):
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)
        if hasattr(self, 'engine'):
            self.engine.dispose()