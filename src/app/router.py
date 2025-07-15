from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.alpine.router import router as alpine_router
from app.core.router import router as general_router
from app.crud.router import router as crud_router
from app.front.router import router as front_router
from app.talos.router import router as talos_router

router = APIRouter()
router.include_router(alpine_router, tags=["alpine"], prefix="/api/alpine")
router.include_router(crud_router, tags=["crud"], prefix="/api")
router.include_router(general_router, tags=["general"], prefix="/api")
router.include_router(front_router, tags=["front"])
router.include_router(talos_router, tags=["talos"], prefix="/api/talos")


@router.get("/health", tags=["health"])
def health_check():
    return JSONResponse(content={"status": "ok"})
