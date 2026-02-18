from aiogram import Bot, Dispatcher
from aiogram.types import Message, BotCommand
from aiogram.filters.command import Command
from aiogram.fsm.storage.memory import MemoryStorage

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

import asyncio
import json
from sqlalchemy.orm import Session

from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from uvicorn import Config, Server

from app.db import crud
from app.db.database import get_db
from app.bot import handlers
from app.scheduler.jobs import check_task
from app.bot.middlewares import DBSessionMiddleware
from app.api.routers import user_router, task_router
from app.api.templates import templates

with open("app/config/config.json", "r", encoding="utf-8") as file:
    data = file.read()
    config = json.loads(data)

BOT_TOKEN = config["BOT_TOKEN_API"]

bot = Bot(BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
dp.update.middleware(DBSessionMiddleware())

app = FastAPI(title="Reminder API")
app.mount(
    "/static",
    StaticFiles(directory="app/api/static"),
    name="static"
)

app.include_router(user_router)
app.include_router(task_router)


async def set_my_commands(b: Bot):
    commands = [
        BotCommand(command="start", description="Запускает бота"),
        BotCommand(command="register", description="Регистрация"),
    ]

    await b.set_my_commands(commands)


@dp.message(Command("start"))
async def cmd_start(message: Message, db):
    user_id = message.from_user.id
    users = crud.get_users(db)
    for user in users:
        if user.tg_id == user_id:
            await message.answer("Бот для создания напоминаний о задачах и привычках.")
            return
    await message.answer("Вы еще не зарегистрированны")

@app.get("/")
def ping(requests: Request, db: Session = Depends(get_db)):
    records = crud.get_records(db)
    for record in records:
        record.time = record.time.strftime("%H:%M")
    return templates.TemplateResponse("index.html", {"request": requests, "records": records})

async def start_api():
    config = Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = Server(config)
    await server.serve()

async def start_scheduler():
    scheduler = AsyncIOScheduler(timezone="Asia/Vladivostok")

    scheduler.add_job(
        check_task,
        trigger=IntervalTrigger(seconds=5),
        kwargs={"bot": bot}
    )
    scheduler.start()

async def start_bot():
    dp.include_router(handlers.tasks.tasks_router)
    dp.include_router(handlers.user.user_router)

    await set_my_commands(bot)
    await dp.start_polling(bot)


async def main():
    print("http://localhost:8000/tasks/")
    await asyncio.gather(
        start_api(),
        start_scheduler(),
        start_bot()
    )



if __name__ == "__main__":
    asyncio.run(main())