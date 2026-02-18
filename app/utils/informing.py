from aiogram.types import Message

async def not_register(message: Message):
    await message.answer("Вы не зарегистированны")
    await message.answer("Чтоб зарегистрироватся используйте команду:\n/register")