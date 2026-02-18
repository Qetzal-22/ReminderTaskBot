from app.db.database import SessionLocal
from app.db import crud
from app.utils.datetime_utils import get_week_days, calc_next_reminder_week, calc_next_reminder_interval
from app.bot.keyboards import postpone_task_kb
from datetime import datetime, date, timedelta
from aiogram import Bot


async def check_task(bot: Bot):
    now = datetime.now().replace(second=0, microsecond=0)
    db = SessionLocal()
    new_next_reminder = None
    try:
        records = crud.get_records_now(now, db)
        for record in records:
            # изменяем слудующею дату напоминания для дней недели или убираем разовое напоминание
            if record.repetition == -1:
                # изменяем следующую дату для задачи повторяющейся по дням недели
                if record.day_week != "":
                    new_next_reminder = calc_next_reminder_week(now, record)
                # удаляем разовую запись
                else:
                    crud.delete_record(record.id, db)
            # изменяем следующую дату для повторяющейся задачи
            else:
                new_next_reminder = calc_next_reminder_interval(now, record)

            if not new_next_reminder is None:
                crud.update_next_reminder_record(record.id, new_next_reminder, db)

            # отправляем смс если напоминание было пропущено или пришло вовремя
            if now-record.next_reminder <= timedelta(hours=3):
                tg_id = crud.get_tg_id_by_user_id(record.user_id, db)
                await bot.send_message(
                    chat_id=tg_id,
                    text=f"❗️ <b>Напоминание</b> ❗️ \n{record.title}",
                    reply_markup=postpone_task_kb(record.id),
                    parse_mode="HTML"
                )
        # обрабатываем записи которые просрочились больше положенного времени
        old_records = crud.get_records_old(now, db)
        for record in old_records:
            if record.repetition == -1:
                if record.day_week != "":
                    new_next_reminder = calc_next_reminder_week(now, record)
                else:
                    crud.delete_record(record.id, db)
            else:
                new_next_reminder = calc_next_reminder_interval(now, record)

            if not new_next_reminder is None:
                crud.update_next_reminder_record(record.id, new_next_reminder, db)

    finally:
        db.close()