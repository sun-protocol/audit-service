import logging
from contextlib import asynccontextmanager

from sqlalchemy import text

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import dashboard, repos, tasks
from app.services.scheduler import shutdown_scheduler, start_scheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def _run_migrations():
    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(repositories)"))
        columns = {row[1] for row in result}
        if "skill" not in columns:
            conn.execute(text("ALTER TABLE repositories ADD COLUMN skill VARCHAR(100)"))
            conn.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    _run_migrations()
    start_scheduler()
    yield
    shutdown_scheduler()


app = FastAPI(title="Audit Service", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(repos.router)
app.include_router(tasks.router)
app.include_router(dashboard.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
