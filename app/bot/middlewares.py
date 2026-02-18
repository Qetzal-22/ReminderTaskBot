from aiogram import BaseMiddleware
from app.db.database import SessionLocal


class DBSessionMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        db = SessionLocal()
        bot = event.bot
        data["db"] = db
        data["bot"] = bot
        try:
            return await handler(event, data)
        finally:
            db.close()
