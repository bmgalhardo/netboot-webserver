from sqlmodel import Session, SQLModel, create_engine, select

from app.core.model import DeviceDB
from app.core.settings import settings


class Database:

    def __init__(self):
        self.engine = None

    def start(self) -> None:
        if self.engine is None:
            self.engine = create_engine(settings.database_path, echo=False)
            SQLModel.metadata.create_all(self.engine)

    def close(self) -> None:
        if self.engine:
            self.engine.dispose()

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
