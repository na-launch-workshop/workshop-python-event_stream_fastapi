from __future__ import annotations

import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import load_config
from .consumer import events, start_consumer

DB_PATH = Path(__file__).parent.parent / "data" / "appliances.db"
PRICE_URL = "http://localhost:5000/price"

NO_CACHE = {"Cache-Control": "no-store"}


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
        return JSONResponse(content=list(events), headers=NO_CACHE)

    @application.get("/api/appliances")
    def get_appliances():
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT name, daily_kwh FROM appliances ORDER BY daily_kwh DESC").fetchall()
            conn.close()
            return JSONResponse(content=[dict(r) for r in rows], headers=NO_CACHE)
        except Exception:
            return JSONResponse(content=[], headers=NO_CACHE)

    @application.get("/api/price")
    def get_price():
        try:
            resp = httpx.get(PRICE_URL, timeout=2.0)
            return JSONResponse(content=resp.json(), headers=NO_CACHE)
        except Exception:
            return JSONResponse(content=None, headers=NO_CACHE)

    return application


app = create_app()

if __name__ == "__main__":
    from uvicorn import run
    cfg = load_config()
    run(app, host="0.0.0.0", port=cfg.port, reload=False)
