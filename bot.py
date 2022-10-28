import requests

from config import TOKEN, WEATHER_API_KEY
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton  # добавление инлайн-кнопки

bot = Bot(token=TOKEN)  # создание объекта бота и передача в его токена
dp = Dispatcher(bot)  # для управления ботом


# отказ (конец ветки)
@dp.message_handler(text=['Нет, сегодня я сплю дома весь день'])
async def net(message: types.Message):
    await message.answer('Уютного дня!', reply_markup=types.ReplyKeyboardRemove())


# согласие (другая ветка развития)
@dp.message_handler(text=['Привет'])  # message.handler == диспетчер сообщений
async def start(message: types.Message):
    kb = [
        [types.KeyboardButton(text='Давай'),
         types.KeyboardButton(text='Нет, сегодня я сплю дома весь день')
         ]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder='Выберите что-нибудь')  # то, что пишется в строке ввода подтекстом
    await message.answer('Привет! я расскажу тебе про погоду в любой точке мира', reply_markup=keyboard)


# 1. сообщение от бота после нажатия "Давай":
@dp.message_handler(text=['Давай'])
async def first_horad(message: types.Message):  # на message "Даавй" бот реагирует:
    await message.answer('Введите название города')  # и отправляет свою реакцию в виде строки в скобках


# ...сейчас пользователь вводит название своего города...


# 2. вывод данных о погоде в городе, введённом пользователем:
@dp.message_handler()
async def second_data(message: types.Message):
    try:
        # для этого нужен import requests
        r = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
        )
        # для этого ТОЖЕ нужен import requests
        data = r.json()

        global temp
        temp = data['main']['temp']
        press = data['main']['pressure']
        weath = data['weather'][0]['description']
        wind = data['wind']['speed']

        global first_answer
        first_answer = (f"температура: {temp}°\n"
                        f"давление: {press} гПа\n"
                        f"облачность: {weath}\n"
                        f"скорость ветра: {wind} м/с\n")

# 3. создание инлайн-кнопки:
        inline_button = InlineKeyboardButton('Хочу совет на день!',
                                            callback_data='button1')  # колбэк - что следует после НАЖАТИЯ кнопки
        inline_kb_1 = InlineKeyboardMarkup().add(inline_button)  # тело кнопки
        await message.answer(first_answer, reply_markup=inline_kb_1)

    except:
        await message.answer('Проверьте название города')


# 4. callback - реакция после нажатия кнопки (содержание совета):
@dp.callback_query_handler(lambda c: c.data == 'button1')
async def process_callback_button1(callback_query: types.CallbackQuery):
    if temp >= 25:
        await bot.send_message(
            callback_query.from_user.id, 'сегодня изжаришься, стоит взять водичку и головной убор')
    elif 10 <= temp <= 25:
        await bot.send_message(
            callback_query.from_user.id, 'сегодня комфортная температура, самое время наслаждаться пением птиц!)')
    elif -25 <= temp <= 10:
        await bot.send_message(
            callback_query.from_user.id, 'сегодня холодно, не забудь шапку и перчатки')
    elif temp <= -25:
        await bot.send_message(
            callback_query.from_user.id, 'в такую погоду лучше вообще не выходить на улицу, '
                                         'а выпить горячего какао дома')

    await bot.answer_callback_query(callback_query.id)


if __name__ == '__main__':
    executor.start_polling(dp)
