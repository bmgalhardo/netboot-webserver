from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.core.db import database
from app.core.model import BootStatus, DeviceCreate, DeviceDB, DeviceUpdate

router = APIRouter()


@router.post("/devices/", status_code=status.HTTP_201_CREATED)
def create_device(device: DeviceCreate, session: Session = Depends(database.get_session)) -> DeviceDB:
    existing = database.get_mac_addr(session=session, mac_addr=device.mac_addr)
    if existing:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Device with this MAC address already exists")

    device_db = DeviceDB(**device.model_dump())

    database.save_device(session=session, device=device_db)
    session.commit()
    session.refresh(device_db)

    return device_db


@router.get("/devices/")
def list_devices(session: Session = Depends(database.get_session)) -> list[DeviceDB]:
    devices = database.get_all_devices(session)
    return devices


@router.get("/devices/{mac_addr}")
def get_device(mac_addr: str, session: Session = Depends(database.get_session)) -> DeviceDB:
    device = database.get_mac_addr(session=session, mac_addr=mac_addr)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return device


@router.patch("/devices/{mac_addr}")
async def update_device(
    mac_addr: str, updated: DeviceUpdate, session: Session = Depends(database.get_session)
) -> DeviceDB:
    device = database.get_mac_addr(session=session, mac_addr=mac_addr)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    update_data = updated.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(device, key, value)

    session.commit()
    session.refresh(device)

    return device


@router.post("/devices/{mac_addr}/toggle")
def toggle_boot(mac_addr: str, session: Session = Depends(database.get_session)) -> RedirectResponse:
    device = database.get_mac_addr(session=session, mac_addr=mac_addr)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    if device.boot == BootStatus.BOOT_PENDING:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't change failed boot status")

    if device.boot == BootStatus.BOOT_DISK:
        device.boot = BootStatus.BOOT_NET
    else:
        device.boot = BootStatus.BOOT_DISK

    session.commit()
    session.refresh(device)

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.delete("/devices/{mac_addr}")
def delete_device(mac_addr: str, session: Session = Depends(database.get_session)) -> dict:
    device = database.get_mac_addr(session=session, mac_addr=mac_addr)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    session.delete(device)
    session.commit()
    return {"detail": "Device deleted"}
