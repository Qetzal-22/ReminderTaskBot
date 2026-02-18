from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext


from sqlalchemy.orm import Session
from app.db import crud
from app.bot.keyboards import profile_kb
from app.bot.states import StatesRegister
from app.utils.verify import verify_user_in_db
from app.utils.informing import not_register

user_router = Router()

@user_router.message(Command("register"))
async def cmd_register(message: Message, db: Session, state: FSMContext):
    user_id = message.from_user.id
    if verify_user_in_db(user_id, db):
        await message.answer("Вы уже зарегистрированны!")
        return

    await message.answer("Введите логин: ")
    await state.set_state(StatesRegister.login)

@user_router.message(StatesRegister.login)
async def get_login(message: Message, state: FSMContext, db: Session):
    user_id = message.from_user.id
    crud.create_user(db, user_id, message.text)
    await message.answer("Вы успешно зарегистрировались!")
    await state.clear()
    await profile(message, db)

@user_router.message(F.text.lower().in_(["профиль", "назад в профиль"]))
async def profile(message: Message, db: Session):
    user_id = message.from_user.id
    if not verify_user_in_db(user_id, db):
        await not_register(message)
    rm = profile_kb()
    await message.answer("Ваш профиль: ", reply_markup=rm)




