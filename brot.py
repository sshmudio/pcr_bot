import logging
from aiogram.types.base import InputFile

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
from config import TOKEN
from datetime import datetime, timedelta
from generator import PcrGenerator
bot = Bot(token=TOKEN)
yesterday = datetime.now() - timedelta(days=1)

storage = MemoryStorage()  # external storage is supported!
dp = Dispatcher(bot, storage=storage)

# user_info = []
# Defining available states
class Form(StatesGroup):
    name = State()
    dob = State()
    age = State()
    collected_date = State()
    gender = State()
    # date_of_completion = State()

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
    ]
    ], resize_keyboard=True, one_time_keyboard=True)
    await message.answer('Здравтсвуйте, выберите действие: ', reply_markup=keyboard)


@dp.message_handler(Text(equals='Сгенерировать ПЦР'))
async def start_generate(message: types.Message):
    """
    Точка входа в разговор
    """
    # Set state
    await Form.name.set()
    await message.reply("Введите свои фамилию и имя прим. Alexeev Alexey: ")


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Разрешить пользователю отменить любое действие
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    """
    Process user name
    """
    async with state.proxy() as data:
        data['name'] = message.text
    print(data['name'])
    await Form.next()

    await message.answer("Напишите свою дату рождения прим. 30.12.1990: ")

# dob
@dp.message_handler(state=Form.dob)
async def process_dob(message: types.Message, state: FSMContext):
    """ Process user name """
    async with state.proxy() as data:
        data['dob'] = message.text

    print(data['dob'])
    await Form.next()

    await message.answer("Сколько вам полных лет прим. 25: ")

@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.age)
async def process_age_invalid(message: types.Message):
    """
    If age is invalid
    """
    return await message.reply("Используйте только цифры")


@dp.message_handler(lambda message: message.text.isdigit(), state=Form.age)
async def process_age(message: types.Message, state: FSMContext):
    # Update state and data
    async with state.proxy() as data:
        data['age'] = message.text
    await Form.next()
    # await state.update_data(age=int(message.text))

    # Configure ReplyKeyboardMarkup
    await message.answer(f"Введите дату взятия анализа прим. {yesterday.strftime('%d.%m.%Y')}: ")
    
@dp.message_handler(state=Form.collected_date)
async def process_collected_date(message: types.Message, state: FSMContext):
    """ Process user collected_date """
    async with state.proxy() as data:
        data['collected_date'] = message.text

    await Form.next()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=True)
    markup.add("Male", "Female")

    await message.answer("Ваш пол?", reply_markup=markup)

@dp.message_handler(state=Form.gender)
async def process_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        date_object = datetime.strptime(data['collected_date'], '%d.%m.%Y') + timedelta(days=3)
        data['gender'] = message.text
        print(data['gender'])
        # Remove keyboard
        markup = types.ReplyKeyboardRemove()
        # And send message
        await bot.send_message(
            message.chat.id,
            md.text(
                md.text('Генерируем на имя, ', data['name']),
                md.text('с возрастом:', data['age']),
                md.text('будет указана дата теста:', data['collected_date']),
                md.text('и полом:', data['gender']),
                md.text(f"а также не забудьте что ваш тест будет действителен три дня до: {date_object.strftime('%d.%m.%Y')}"),
                sep='\n',
            ),
            reply_markup=markup,
            parse_mode=ParseMode.MARKDOWN,
        )
    # Finish conversation
    await state.finish()
    pcr = PcrGenerator(name=data['name'], dob=data['dob'], age=data['age'], gender=data['gender'], collected_date=data['collected_date'], date_of_completion=str(date_object.strftime("%d.%m.%Y")))
    name_doc = pcr.generate()
    print(name_doc)
    photo = open(name_doc, 'rb')
    print(photo)
    await bot.send_photo(message.chat.id, photo)

@dp.message_handler(lambda message: message.text not in ["Male", "Female"], state=Form.gender)
async def process_gender_invalid(message: types.Message):
    """
    In this example gender has to be one of: Male, Female, Other.
    """
    return await message.reply(".")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)