from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import load_config
from .consumer import events, start_consumer


@asynccontextmanager
async def lifespan(application: FastAPI):
    cfg = load_config()
    start_consumer(cfg.bootstrap_servers, cfg.topic, cfg.group_id)
    yield


def create_app() -> FastAPI:
    application = FastAPI(lifespan=lifespan)
    application.mount("/static", StaticFiles(directory="static"), name="static")

    @application.get("/", response_class=HTMLResponse)
    def dashboard():
        return HTMLResponse(open("static/index.html").read())

    @application.get("/api/events")
    def get_events():
        return JSONResponse(content=list(events))

    return application


app = create_app()

if __name__ == "__main__":
    from uvicorn import run

    cfg = load_config()
    run(app, host="0.0.0.0", port=cfg.port, reload=False)
