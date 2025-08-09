import logging
from typing import Any

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.core.model import DeviceDB
from app.core.settings import settings

logger = logging.getLogger(__name__)

class Database:

    _db_path = settings.database_path

    def __init__(self):
        self.engine = None

    def start(self) -> None:
        if self.engine is None:
            self.engine = create_engine(self._db_path, **self.db_configs)
            logger.debug(f"Tables registered: {', '.join(SQLModel.metadata.tables.keys())}")
            SQLModel.metadata.create_all(self.engine)

    def close(self) -> None:
        if self.engine:
            self.engine.dispose()

    def is_in_memory(self) -> bool:
        return ":memory:" in self._db_path

    @property
    def db_configs(self) -> dict:
        configs: dict[str, Any] = {
            "echo": settings.logging.upper() is logging.DEBUG,
        }
        if self.is_in_memory():
            # For in-memory SQLite databases, we need to set these options
            # to allow multiple threads to access the same database.
            configs.update(
                {
                    "connect_args": {"check_same_thread": False},
                    "poolclass": StaticPool,
                }
            )
        return configs

    @property
    def session(self):
        return Session(self.engine)

    def get_session(self):
        with self.session as session:
            yield session

    @staticmethod
    def get_mac_addr(session: Session, mac_addr: str) -> None | DeviceDB:
        statement = select(DeviceDB).where(DeviceDB.mac_addr == mac_addr)
        device = session.exec(statement).first()
        return device

    @staticmethod
    def get_all_devices(session: Session) -> list[DeviceDB]:
        devices = session.exec(select(DeviceDB)).all()
        return list(devices)

    @staticmethod
    def save_device(session: Session, device: DeviceDB) -> None:
        session.add(device)


database = Database()
