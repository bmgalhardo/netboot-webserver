from datetime import datetime
from enum import IntEnum, StrEnum, auto

from pydantic import model_validator
from sqlmodel import Field, SQLModel

from app.core.exceptions import InvalidMAC
from app.core.utils import MACAddress


class ImageType(StrEnum):
    ALPINE = auto()
    TALOS = auto()


class BootStatus(IntEnum):
    BOOT_PENDING = 0
    BOOT_DISK = 1
    BOOT_NET = 2


class Device(SQLModel):
    mac_addr: str
    timestamp: datetime | None = None
    image: ImageType
    proxmox: bool = False
    boot: BootStatus = BootStatus.BOOT_PENDING

    @property
    def mac_obj(self) -> MACAddress:
        return MACAddress(self.mac_addr)

    @model_validator(mode="after")
    def validate_mac(self):
        try:
            _ = self.mac_obj
        except InvalidMAC:
            raise InvalidMAC(f"Invalid MAC address: {self.mac_addr}")
        return self


class DeviceCreate(Device):
    pass


class DeviceUpdate(SQLModel):
    image: ImageType | None = None
    timestamp: datetime | None = None
    proxmox: bool | None = None
    boot: BootStatus | None = None


class DeviceDB(Device, table=True):  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    mac_addr: str = Field(index=True, unique=True)
