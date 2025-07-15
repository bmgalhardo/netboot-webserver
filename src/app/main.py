from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.db import database
from app.core.settings import settings
from app.router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.start()
    yield
    database.close()


app = FastAPI(lifespan=lifespan)

app.include_router(router)

app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8002, reload=True)  # nosec
