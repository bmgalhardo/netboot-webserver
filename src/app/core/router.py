import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlmodel import Session

from app.core.db import database
from app.core.ipxe import IPXE
from app.core.model import DeviceDB, ImageType
from app.core.utils import MACAddress

router = APIRouter()


@router.get("/entrypoint")
def ipxe_entrypoint() -> Response:
    ipxe = IPXE().add_chain("/entrypoint/${mac}")
    return Response(content=ipxe.to_file(), media_type="text/plain")


@router.get("/entrypoint/{mac_addr}")
def ipxe_mac_filtering(mac_addr: str, session: Session = Depends(database.get_session)) -> Response:
    mac = MACAddress(mac_addr)
    now = datetime.datetime.now()

    device = database.get_mac_addr(session=session, mac_addr=mac_addr)
    if device:
        ipxe = (
            IPXE()
            .add_msg(f"Booting {mac.as_colon()} with {device.image}")
            .add_chain(f"/{device.image}/boot?proxmox={device.proxmox}")
        )

        device.timestamp = now
    else:
        # default behaviour is to serve promox alpine
        device = DeviceDB(mac_addr=mac_addr, timestamp=now, proxmox=True, image=ImageType.ALPINE)
        ipxe = IPXE().add_msg(f"Booting {mac.as_colon()} with Alpine").add_chain("/alpine/boot?proxmox=true")

    database.save_device(session=session, device=device)
    session.commit()
    session.refresh(device)

    return Response(content=ipxe.to_file(), media_type="text/plain")
