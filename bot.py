from typing import Text
from aiogram import Bot, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Text
from config import TOKEN
from dialogs import msg
from database import database as db
import logging

# код создания
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())
@dp.message_handler(commands="start")
async def start_message(message: types.Message):
    # Имя юзера из настроек Телеграма
    user_name = message.from_user.first_name
    logging.info(message.text)
    keyboard = types.ReplyKeyboardMarkup([
        [
            types.KeyboardButton(text="Сгенерировать ПЦР"),
            types.KeyboardButton(text="Пополнить баланс"), 

        ],
        [
            types.KeyboardButton(text="Помощь"),
            types.KeyboardButton(text="Предложить идею"),
    ]], resize_keyboard=True)
    await message.answer(
        msg.hello_message.format(name=user_name),
        reply_markup=keyboard
        )

@dp.message_handler(Text(equals="Пополнить баланс"))
async def top_up_balance(message: types.Message):
    await message.answer("Стоимость одного теста 7 USD")
    topup_keys = types.ReplyKeyboardMarkup([
        [
            types.KeyboardButton(text=1),
            types.KeyboardButton(text=2),
            types.KeyboardButton(text=5),
        ],
    ], one_time_keyboard=True)
    await message.answer(
        "Dыберите нужное колличество\n1 (7 USD)\n2 (13 USD)\n5 (30 USD) ",
        reply_markup=topup_keys
        )

    user_input_sum = message.text
    print(user_input_sum)
    if user_input_sum == '1':
        print(message.chat)

# @dp.message_handler(content_types=['text'])
# async def get_text_messages(msg: types.Message):
#     if msg.text.lower() == '1':
#         await msg.answer('Привет!')
#     else:
#         await msg.answer('Не понимаю, что это значит.')

@dp.message_handler(commands="Сгенерировать ПЦР")
async def get_user_info(message: types.Message):
    await message.answer('Введите фамилию имя прим: "Alexeev Alexey"', )
    print("Юзер ввел сообщение", message.text)
    await message.answer(message.text)

async def on_shutdown(dp):
    logging.warning('Shutting down..')
    # закрытие соединения с БД
    db._conn.close()
    logging.warning("DB Connection closed")