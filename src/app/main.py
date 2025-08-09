from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import app.models as _models  # noqa
from app.core.db import database
from app.core.settings import settings, setup_logger
from app.router import router

setup_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.start()
    yield
    database.close()


fastapi = FastAPI(lifespan=lifespan)
fastapi.include_router(router)
fastapi.mount("/static", StaticFiles(directory=settings.static_dir), name="static")

if __name__ == "__main__":
    uvicorn.run("app.main:fastapi", host="0.0.0.0", port=8002, reload=True)  # nosec
