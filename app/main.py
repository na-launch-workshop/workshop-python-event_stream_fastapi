from __future__ import annotations

from contextlib import asynccontextmanager

import sqlite3
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import load_config
from .consumer import events, start_consumer

DB_PATH = Path(__file__).parent.parent / "data" / "customers.db"


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
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT name, department, role, location FROM customers").fetchall()
            conn.close()
            return JSONResponse(
                content=[dict(r) for r in rows],
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
