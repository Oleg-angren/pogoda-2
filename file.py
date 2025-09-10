import logging
import asyncio
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
import requests
from datetime import datetime

# === Настройки ===
API_TOKEN = '8082307822:AAFWJBO01AZhgLXyKC2s-bO9NK08PvNT7h0'
WEATHER_API_KEY = 'df1b0cbe2a9f1f4a05b39a260d71816f'

# Логирование
logging.basicConfig(level=logging.INFO)

# Создаём роутер
router = Router()

# Словарь для перевода дней недели
WEEKDAYS = {
    "Monday": "понедельник",
    "Tuesday": "вторник",
    "Wednesday": "среда",
    "Thursday": "четверг",
    "Friday": "пятница",
    "Saturday": "суббота",
    "Sunday": "воскресенье"
}

# Эмодзи по времени суток
def get_time_emoji(hour: int) -> str:
    if 5 <= hour < 12:
        return "🌅, Доброе утро "
    elif 12 <= hour < 17:
        return "🌤️, Добрый день"
    elif 17 <= hour < 22:
        return "🌆, Добрый вечер"
    else:
        return "🌙, Доброй ночи"

# === Обработчики ===

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "🌤️ Привет! Я бот, который покажет погоду и точное время в любом городе.\n"
        "Напиши: /погода <город>\n"
        "Например: /погода Ангрен\n"
        "Бот от Олега"
    )


@router.message(Command("погода"))
async def cmd_weather(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("❗ Укажи город после команды. Пример: /погода Воронеж")
        return

    city = args[1].strip()
    url = (
        f"http://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={WEATHER_API_KEY}&lang=ru&units=metric"
    )

    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200:
            error_msg = data.get("message", "Город не найден")
            await message.answer(f"❌ Ошибка: {error_msg}")
            return
        

        # === Данные о погоде ===
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind_speed = data["wind"]["speed"]
        desc = data["weather"][0]["description"].capitalize()
        city_name = data["name"]
        country = data["sys"]["country"]

        # === Время в городе ===
        timezone_offset = data["timezone"]  # смещение от UTC в секундах
        current_time_utc = data["dt"]       # время сервера (Unix timestamp)
        city_timestamp = current_time_utc + timezone_offset
        city_dt = datetime.utcfromtimestamp(city_timestamp)

        city_time = city_dt.strftime("%d.%m.%Y %H:%M:%S")
        weekday_eng = city_dt.strftime("%A")
        weekday_ru = WEEKDAYS.get(weekday_eng, "Неизвестно")

        # Эмодзи по времени суток
        hour = city_dt.hour
        time_emoji = get_time_emoji(hour)

        # === Формируем ответ ===
        weather_text = (
            f"{time_emoji} <b>Погода и время в {city_name}, {country}</b>\n"
            f"🕒 <b>Местное время:</b> {city_time}\n"
            f"📅 <b>День недели:</b> {weekday_ru.capitalize()}\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"🌤️ <b>Состояние:</b> {desc}\n"
            f"🌡️ <b>Температура:</b> {temp}°C\n"
            f"🧍‍♂️ <b>Ощущается как:</b> {feels_like}°C\n"
            f"💧 <b>Влажность:</b> {humidity}%\n"
            f"🌬️ <b>Скорость ветра:</b> {wind_speed} м/с\n"
            f"🔽 <b>Давление:</b> {pressure * 0.750062:.1f} мм рт. ст. 🌡️"
        )

        await message.answer(weather_text, parse_mode="HTML")

    except Exception as e:
        await message.answer(f"⚠️ Произошла ошибка при получении данных: {e}")


# === Запуск бота ===
async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    print("🌍 Бот с погодой и временем запущен...")
    print("Ожидание команд от пользователей...")
    await dp.start_polling(bot)


# 🚀 Запуск
if __name__ == '__main__':
    asyncio.run(main())