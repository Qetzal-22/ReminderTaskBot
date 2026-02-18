from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session

from app.db import crud
from app.bot.keyboards import task_show_kb, task_management_kb, choose_repetition_kb, day_week_kb, profile_kb, \
    postpone_task_kb
from app.bot.states import StatesCreateTask, StatesPostPone
from app.utils.verify import verify_user_in_db, verify_time, verify_repetition
from app.utils.informing import not_register
from app.utils.datetime_utils import get_week_days

tasks_router = Router()


@tasks_router.message(F.text.lower() == "задачи")
async def management(message: Message, db: Session):
    user_id = message.from_user.id
    if not verify_user_in_db(user_id, db):
        await not_register(message)
    rm = task_management_kb()
    await message.answer("Управление задачами: ", reply_markup=rm)


# ==================================================================================================
# ======================================Просмотр задачи=============================================
# ==================================================================================================

@tasks_router.message(F.text.lower() == "просмотр задач")
async def show(message: Message, db: Session):
    tg_id = message.from_user.id
    if not verify_user_in_db(tg_id, db):
        await not_register(message)
    user_id = crud.get_user_id_by_tg_id(tg_id, db)
    records = crud.get_records_by_user_id(user_id, db)
    records = sorted(records, key=lambda x: x.next_reminder)
    count = 1
    text = "<b>  == Ваши задачи ==  </b>\n\n"

    for record in records:
        if record.category == "task":
            date_text = ".".join(str(record.next_reminder).split()[0].split("-")[::-1])
            time_text = str(record.next_reminder).split()[1][:-3]
            text += f"{count}) {record.title}\n   🕑{time_text}  -  📅{date_text}\n\n"
            count += 1

    rm = task_show_kb()
    await message.answer(text, reply_markup=rm, parse_mode="HTML")


# ==================================================================================================
# ==================================================================================================
# ==================================================================================================


# ==================================================================================================
# ======================================Добавление задачи===========================================
# ==================================================================================================

@tasks_router.message(F.text.lower() == "добавить задачу")
async def add(message: Message, state: FSMContext, db: Session):
    user_id = message.from_user.id
    if not verify_user_in_db(user_id, db):
        await not_register(message)
    await message.answer("Напишите названия задачи: ")
    await state.set_state(StatesCreateTask.title)


@tasks_router.message(StatesCreateTask.title)
async def get_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Напишите время для задачи: \n(Формат: 13:33)")
    await state.set_state(StatesCreateTask.time)


@tasks_router.message(StatesCreateTask.time)
async def get_time(message: Message, state: FSMContext):
    time = message.text
    if not verify_time(time):
        await message.answer("Вы ввели время в неправильном формате. Пример правильного формата: 21:55")
        await message.answer("Напишите время для задачи:")
        await state.set_state(StatesCreateTask.time)
        return
    await state.update_data(time=time)
    rm = choose_repetition_kb()
    await message.answer("Выберете интервал повторение задачи:", reply_markup=rm)


# ==============================Обработка выбора интервала между повторениями=======================

@tasks_router.callback_query(F.data.startswith("repetition_other"))
async def get_repetition_other(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Напиши раз во сколько часов надо повторять эту задачу: \n(Напиши число)")
    await state.set_state(StatesCreateTask.repetition)


@tasks_router.callback_query(F.data.startswith("repetition_day_week"))
async def get_repetition_day_week(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    bot = callback.bot
    await state.update_data(day_week="")
    rm = day_week_kb([])
    await bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text='Выберети дни недели в которые хотите получать напоминания и нажмите "Подтвердить"'
    )
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=rm
    )


@tasks_router.callback_query(F.data.startswith("repetition"))
async def get_selected_repetition(callback: CallbackQuery, state: FSMContext, db):
    await callback.answer()
    user_id = callback.from_user.id
    repetition = callback.data.split(":")[1]
    category = "task"
    repetition = int(repetition)
    await state.update_data(repetition=repetition)
    await state.update_data(day_week="")
    await state.update_data(next_reminder="")
    bot = callback.bot
    await create_record(user_id, category, state, db, bot)


@tasks_router.message(StatesCreateTask.repetition)
async def get_repetition(message: Message, state: FSMContext, db):
    repetition = message.text
    if not verify_repetition(repetition):
        await message.answer("Вы ввели данные в неправильном формате, нужно число (например: 3)")
        await message.answer("Попробуйте еще раз: ")
        await state.set_state(StatesCreateTask.repetition)
        return

    repetition = int(repetition)
    user_id = message.from_user.id
    category = "task"
    await state.update_data(repetition=repetition)
    await state.update_data(next_reminder="")
    await state.update_data(day_week="")
    bot = message.bot
    await create_record(user_id, category, state, db, bot)


# ==================================================================================================


# ===============================Обработка выбора дня недели========================================

@tasks_router.callback_query(F.data.startswith("day_week"))
async def add_day_week(callback: CallbackQuery, state: FSMContext, bot: Bot):
    selected_day_week = callback.data.split(":")[1]
    data = await state.get_data()
    day_week = data["day_week"].split(",")
    if selected_day_week in day_week:
        day_week.remove(selected_day_week)
    else:
        day_week.append(selected_day_week)
    if "" in day_week: # отчищаем от мусора
        day_week.remove("")
    sort_day_week = sorted(list(map(int, day_week)))
    day_week = list(map(str, sort_day_week))
    day_week = ",".join(day_week)
    await state.update_data(day_week=day_week)

    rm = day_week_kb(day_week)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=rm
    )


@tasks_router.callback_query(F.data.startswith("ready_day_week"))
async def get_day_week(callback: CallbackQuery, state: FSMContext, db: Session):
    await callback.answer()
    await state.update_data(repetition=-1)
    await state.update_data(next_reminder="")

    user_id = callback.from_user.id
    source = "task"
    bot = callback.bot
    await create_record(user_id, source, state, db, bot)


# ==================================================================================================


async def create_record(tg_id, source, state: FSMContext, db: Session, bot: Bot, text_message="добавлена!"):
    user_id = crud.get_user_id_by_tg_id(tg_id, db)
    data = await state.get_data()
    title = data["title"]
    time_str = data["time"]
    repetition = data["repetition"]
    day_week = data["day_week"]
    next_reminder = data["next_reminder"]
    await state.clear()

    time = datetime.strptime(time_str, "%H:%M").time()

    if next_reminder == "":
        if repetition != -1:
            today = date.today()
            next_reminder = datetime.combine(today, time)
        else:
            if day_week != "":
                day_week = day_week.split(",")
                now_week = get_week_days()
                now = datetime.now()
                next_reminder = now - timedelta(days=1)
                for day in day_week:
                    if now_week[day] > now:
                        next_reminder = now_week[day].replace(hour=time.hour, minute=time.minute)
                if next_reminder <= now:
                    next_reminder = (now_week[day_week[0]] + timedelta(days=7)).replace(hour=time.hour,
                                                                                        minute=time.minute)

                while now > next_reminder:
                    if repetition == -1:
                        if day_week == "":
                            next_reminder += timedelta(days=1)
                            break
                    next_reminder += timedelta(hours=repetition)
            else:
                today = date.today()
                next_reminder = datetime.combine(today, time)
                if next_reminder < datetime.now():
                    next_reminder = next_reminder + timedelta(days=1)

    day_week = ",".join(day_week)
    crud.create_record(db, user_id, title, time, repetition, next_reminder, day_week, source)
    rm = profile_kb()
    await bot.send_message(
        chat_id=tg_id,
        text=f"Задача {title} {text_message}",
        reply_markup=rm
    )


# ==================================================================================================
# ==================================================================================================
# ==================================================================================================


# ==================================================================================================
# =================================обработка отложения задачи===========================================
# ==================================================================================================

@tasks_router.callback_query(F.data.startswith("postpone_other"))
async def get_postpone_other(callback: CallbackQuery, db, state: FSMContext):
    await callback.answer()
    record_id = callback.data.split(":")[1]
    record_id = int(record_id)
    await state.update_data(record_id=record_id)
    await callback.message.answer("Напишите на сколько минут хотите отложить задачу: ")
    await state.set_state(StatesPostPone.postpone_time)


@tasks_router.message(StatesPostPone.postpone_time)
async def get_postpone_time(message: Message, db: Session, state: FSMContext):
    postpone_time = message.text
    if not postpone_time.isdigit():
        await message.answer("Время на которое вы хотите отложить задачу должно быть написанно одним числом")
        await message.answer("Попробуйте снова: ")
        await state.set_state(StatesPostPone.postpone_time)
    postpone_time = int(postpone_time)
    data = await state.get_data()
    record_id = data["record_id"]
    record = crud.get_record_by_id(record_id, db)
    user_id = record.user_id
    category = record.category
    bot = message.bot
    new_next_reminder = datetime.now() + timedelta(minutes=postpone_time)
    str_time = ":".join(record.time.strftime("%H:%M").split(":")[:2])

    await state.update_data(title=record.title)
    await state.update_data(time=str_time)
    await state.update_data(repetition=-1)
    await state.update_data(day_week=record.day_week)
    await state.update_data(next_reminder=new_next_reminder)

    await create_record(user_id, category, state, db, bot, text_message="отложена!")


@tasks_router.callback_query(F.data.startswith("postpone"))
async def get_postpone(callback: CallbackQuery, db, state: FSMContext):
    await callback.answer()
    time_postpone = callback.data.split(":")[1]
    time_postpone = int(time_postpone)

    record_id = callback.data.split(":")[2]
    record_id = int(record_id)
    record = crud.get_record_by_id(record_id, db)
    user_id = record.user_id
    category = record.category
    bot = callback.bot
    new_next_reminder = datetime.now() + timedelta(minutes=time_postpone)
    str_time = ":".join(record.time.strftime("%H:%M").split(":")[:2])

    await state.update_data(title=record.title)
    await state.update_data(time=str_time)
    await state.update_data(repetition=-1)
    await state.update_data(day_week=record.day_week)
    await state.update_data(next_reminder=new_next_reminder)

    await create_record(user_id, category, state, db, bot, text_message="отложена!")

# ==================================================================================================
# ==================================================================================================
# ==================================================================================================
