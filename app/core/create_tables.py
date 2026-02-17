# one-time script — save as create_tables.py and run it
import asyncio
from app.core.database import engine, Base
from app.models.student import Student   # ← import so it's registered
from app.models.item import Item          # ← import so it's registered
from app.models.register import User      # ← import user model so it's registered
from app.models.chat_history import ChatHistory  # ← import chat history model so it's registered

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_db())
