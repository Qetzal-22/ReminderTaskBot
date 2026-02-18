from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

def profile_kb():
    builder = ReplyKeyboardBuilder()
    builder.button(text="Задачи")
    rm = builder.as_markup(resize_keyboard=True)
    return rm

def task_management_kb():
    builder = ReplyKeyboardBuilder()
    builder.button(text="Просмотр задач")
    builder.button(text="Добавить задачу")
    builder.button(text="Назад в профиль")
    builder.adjust(2)
    rm = builder.as_markup(resize_keyboard=True)
    return rm

def task_show_kb():
    builder = ReplyKeyboardBuilder()
    builder.button(text="Добавить задачу")
    builder.button(text="Назад в профиль")
    rm = builder.as_markup(resize_keyboard=True)
    return rm

def choose_repetition_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="Не повторять", callback_data="repetition:-1")
    builder.button(text="Ежедневно", callback_data="repetition:24")
    builder.button(text="Еженедельно", callback_data=f"repetition:{24*7}")
    builder.button(text="Выбрать дни недели", callback_data=f"repetition_day_week")
    builder.button(text="Другое", callback_data="repetition_other")
    builder.adjust(1)
    rm = builder.as_markup(resize_keyboard=True)
    return rm

def postpone_task_kb(record_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="Отложить на 15мин", callback_data=f"postpone:15:{record_id}")
    builder.button(text="Отложить на час", callback_data=f"postpone:60:{record_id}")
    builder.button(text="Другое", callback_data=f"postpone_other:{record_id}")
    builder.adjust(1)
    rm = builder.as_markup(resize_keyboard=True)
    return rm

def day_week_kb(select_days):
    week_days = {
        "ПН": "0",
        "ВТ": "1",
        "СР": "2",
        "ЧТ": "3",
        "ПТ": "4",
        "СБ": "5",
        "ВС": "6"
    }
    builder = InlineKeyboardBuilder()
    for name, num in week_days.items():
        text = name
        if num in select_days:
            text += "✅"
        builder.button(text=text, callback_data=f"day_week:{num}")
    builder.button(text="Подтверить", callback_data="ready_day_week")
    builder.adjust(2)
    rm = builder.as_markup(resize_keyboard=True)
    return rm