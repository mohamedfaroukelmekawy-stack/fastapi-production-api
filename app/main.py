from fastapi import FastAPI

from app.core.database import engine, Base
import app.models   # 👈 مهم عشان يحمل كل الموديلات

from app.api import students_router, items_router, register_router, auth_router


app = FastAPI()


# ✅ Create tables automatically on startup
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Routers
app.include_router(students_router)
app.include_router(items_router)
app.include_router(register_router)
app.include_router(auth_router)


@app.get("/health")
async def health():
    return {"status": "ok"}

from app.api.llm import router as llm_router

app.include_router(llm_router)

