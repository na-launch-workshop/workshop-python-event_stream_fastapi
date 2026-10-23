from __future__ import annotations

from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import load_config
from .consumer import events, start_consumer

DATASETTE_URL = "http://localhost:8001/customers/customers.json?_shape=array&_ttl=0"


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

    @application.get("/api/customers")
    def get_customers():
        try:
            response = httpx.get(DATASETTE_URL, timeout=2.0)
            return JSONResponse(
                content=response.json(),
                headers={"Cache-Control": "no-store"},
            )
        except Exception:
            return JSONResponse(content=[], headers={"Cache-Control": "no-store"})

    return application


app = create_app()

if __name__ == "__main__":
    from uvicorn import run

    cfg = load_config()
    run(app, host="0.0.0.0", port=cfg.port, reload=False)
