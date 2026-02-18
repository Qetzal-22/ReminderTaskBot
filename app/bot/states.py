from aiogram.fsm.state import State, StatesGroup

class StatesRegister(StatesGroup):
    login = State()

class StatesCreateTask(StatesGroup):
    title = State()
    time = State()
    repetition = State()
    day_week = State()

class StatesPostPone(StatesGroup):
    postpone_time = State()