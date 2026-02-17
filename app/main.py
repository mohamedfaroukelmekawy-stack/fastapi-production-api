from fastapi import FastAPI

from app.core.database import Base, engine
import app.models
from app.routes import (
    auth_router,
    items_router,
    llm_router,
    register_router,
    students_router,
)


app = FastAPI()


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(students_router)
app.include_router(items_router)
app.include_router(register_router)
app.include_router(auth_router)
app.include_router(llm_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
