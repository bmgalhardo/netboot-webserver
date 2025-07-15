from fastapi import APIRouter, Depends, Form, Query, status
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from app.core.db import database
from app.core.exceptions import InvalidMAC
from app.core.model import DeviceCreate, DeviceDB, ImageType
from app.core.settings import settings

router = APIRouter()
templates = Jinja2Templates(directory=settings.template_dir)


@router.get("/")
def index(
    request: Request, error: str | None = Query(default=None), session: Session = Depends(database.get_session)
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"devices": database.get_all_devices(session), "images": list(ImageType), "error": error},
    )


@router.post("/devices/create")
def create_device_ui(
    request: Request,
    mac_addr: str = Form(...),
    image: ImageType = Form(...),
    proxmox: bool = Form(default=False),
    session: Session = Depends(database.get_session),
):
    try:
        device_data = DeviceCreate(mac_addr=mac_addr, image=image, proxmox=proxmox)
    except InvalidMAC:
        return RedirectResponse(url="/?error=Mac+Address+invalid", status_code=status.HTTP_303_SEE_OTHER)

    existing = database.get_mac_addr(session=session, mac_addr=device_data.mac_addr)
    if existing:
        return RedirectResponse(url="/?error=Mac+Address+already+present", status_code=status.HTTP_303_SEE_OTHER)

    device_db = DeviceDB(**device_data.model_dump())
    database.save_device(session=session, device=device_db)
    session.commit()
    session.refresh(device_db)

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/devices/{mac_addr}/delete")
async def delete_device_ui(mac_addr: str, session: Session = Depends(database.get_session)):
    device = database.get_mac_addr(session=session, mac_addr=mac_addr)
    if not device:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    session.delete(device)
    session.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
