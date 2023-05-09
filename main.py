import asyncio
from aiogram import Bot, Dispatcher, executor, types
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
# import json
import requests
from geopy.geocoders import Nominatim
import ephem
import datetime
from io import BytesIO
from apscheduler.schedulers.asyncio import AsyncIOScheduler

geolocator = Nominatim(user_agent='my_app')
storage = MemoryStorage()
bot = Bot('5319343788:AAHOrkt75PJKSuqE-mEyre4jxj8pAjNGKyY')
dp = Dispatcher(bot, storage)


scheduler = AsyncIOScheduler(timezone='Europe/Moscow')



def get_today(city):
    global geolocator
    url = f"https://api.tomorrow.io/v4/weather/forecast?location={city}&timesteps=1h&units=metric&apikey=nMbAeWz1TAhYA7NeY9Ti24gjUqtSNUY1"  # %D0%9C%D0%B8%D0%BD%D1%81%D0%BA
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    response = response.json()
    print(response)
    time1 = response["timelines"]["hourly"][4]["time"]
    t1 = str(int(response["timelines"]["hourly"][4]["values"]["temperature"]))
    ws1 = str(int(response["timelines"]["hourly"][4]["values"]["windSpeed"]))
    pr1 = str(int(response["timelines"]["hourly"][4]["values"]["pressureSurfaceLevel"] / 1.333))
    wc1 = str(int(response["timelines"]["hourly"][4]["values"]["weatherCode"]))
    time2 = response["timelines"]["hourly"][10]["time"]
    t2 = str(int(response["timelines"]["hourly"][10]["values"]["temperature"]))
    ws2 = str(int(response["timelines"]["hourly"][10]["values"]["windSpeed"]))
    pr2 = str(int(response["timelines"]["hourly"][10]["values"]["pressureSurfaceLevel"] / 1.333))
    wc2 = str(int(response["timelines"]["hourly"][10]["values"]["weatherCode"]))
    time3 = response["timelines"]["hourly"][18]["time"]
    t3 = str(int(response["timelines"]["hourly"][18]["values"]["temperature"]))
    ws3 = str(int(response["timelines"]["hourly"][18]["values"]["windSpeed"]))
    pr3 = str(int(response["timelines"]["hourly"][18]["values"]["pressureSurfaceLevel"] / 1.333))
    wc3 = str(int(response["timelines"]["hourly"][18]["values"]["weatherCode"]))

    location = geolocator.geocode(city, timeout=10)

    lat = location.latitude
    lon = location.longitude

    city_astr = ephem.Observer()
    city_astr.lon = lon
    city_astr.lat = lat

    city_astr.date = datetime.date.today()

    # Вычислите время восхода и заката солнца
    sunrise_time = city_astr.next_rising(ephem.Sun()).datetime().strftime('%H:%M:%S')
    sunset_time = city_astr.next_setting(ephem.Sun()).datetime().strftime('%H:%M:%S')

    return [city, [t1, ws1, pr1, wc1], [t2, ws2, pr2, wc2], [t3, ws3, pr3, wc3], [sunrise_time, sunset_time]]


def todayforecast(fc):  # city, m_t, m_ws, m_p, m_wc, d_t, d_ws, d_p, d_wc, n_t, n_ws, n_p, n_wc

    city = fc[0]
    m_t, m_ws, m_p, m_wc = fc[1]
    d_t, d_ws, d_p, d_wc = fc[2]
    n_t, n_ws, n_p, n_wc = fc[3]

    def place_text(where, text, font_size, coords=(0, 0), color=(255, 255, 255, 255)):
        shadow_offset = 1
        shadow_color = (0, 0, 0, 128)

        font = ImageFont.truetype("arial.ttf", font_size)
        text_length = font.getlength(text)
        if coords[0] == 999:
            x = (bg_width - text_length) // 2
            y = coords[1]
        else:
            x, y = coords
        draw = ImageDraw.Draw(where)
        shadow_position = (x + shadow_offset, y + shadow_offset)
        draw.text(shadow_position, text, font=font, fill=shadow_color)
        text_position = (x, y)
        draw.text(text_position, text, font=font, fill=color)
        return int(x + text_length), int(y)

    def place_img(where, src, size=(100, 100), coords=(0, 0)):
        img = Image.open(src)
        img = img.resize(size)
        where.paste(img, coords, img)

    d_wc = int(d_wc)
    bg_img = "wbgs/d/"
    if d_wc == 1000 or d_wc == 1100:
        bg_img += "clear.jpg"
    elif d_wc == 2000 or d_wc == 2100:
        bg_img += "fog.jpg"
    elif d_wc == 1101:
        bg_img += "partly_cloudy.jpg"
    elif d_wc == 1102 or d_wc == 1001:
        bg_img += "cloudy.jpg"
    elif d_wc == 4000 or d_wc == 4200 or d_wc == 4001 or d_wc == 4201:
        bg_img += "rain.jpg"
    elif d_wc == 5001 or d_wc == 5100 or d_wc == 5000 or d_wc == 5101:
        bg_img += "snow.jpg"
    elif d_wc == 6000 or d_wc == 6200 or d_wc == 6001 or d_wc == 6201 or d_wc == 7102 or d_wc == 7000 or d_wc == 7101:
        bg_img += "hail.jpg"
    elif d_wc == 8000:
        bg_img += "storm.jpg"
    else:
        bg_img += "zzz.jpg"
    bg = Image.open(bg_img)

    bg_width, bg_height = bg.size

    logo = Image.open("wbgs/Бот - погоды - без фона.png")
    logo = logo.resize((115, 115))
    bg.paste(logo, (0, 0), logo)

    draw = ImageDraw.Draw(bg)
    place_text(bg, city.capitalize(), 28, (999, 30), (118, 206, 255, 255))
    place_text(bg, "Погода на завтра", 36, (999, 72))
    place_text(bg, "Утро", 21, (205, 127))
    place_text(bg, "День", 21, (324, 127))
    place_text(bg, "Ночь", 21, (444, 127))
    place_text(bg, "Температура", 21, (24, 263))
    place_text(bg, "Ветер", 21, (24, 316))
    place_text(bg, "Давление", 21, (24, 368))
    draw.line(((173, 253), (173, 253 + 144)), fill=(255, 255, 255), width=2)
    draw.line(((290, 253), (290, 253 + 144)), fill=(255, 255, 255), width=2)
    draw.line(((410, 253), (410, 253 + 144)), fill=(255, 255, 255), width=2)

    s = place_text(bg, m_t, 32, (193, 263))
    place_text(bg, "°С", 16, (s[0] + 4, s[1]), (190, 192, 194, 255))
    s = place_text(bg, d_t, 32, (310, 263))
    place_text(bg, "°С", 16, (s[0] + 4, s[1]), (190, 192, 194, 255))
    s = place_text(bg, n_t, 32, (430, 263))
    place_text(bg, "°С", 16, (s[0] + 4, s[1]), (190, 192, 194, 255))

    s = place_text(bg, m_ws, 22, (210, 319))
    place_text(bg, "м/с", 16, (s[0] + 4, s[1]), (190, 192, 194, 255))
    s = place_text(bg, d_ws, 22, (323, 319))
    place_text(bg, "м/с", 16, (s[0] + 4, s[1]), (190, 192, 194, 255))
    s = place_text(bg, n_ws, 22, (442, 319))
    place_text(bg, "м/с", 16, (s[0] + 4, s[1]), (190, 192, 194, 255))

    s = place_text(bg, m_p, 22, (193, 371))
    place_text(bg, "рт.ст.", 16, (s[0] + 4, s[1]), (190, 192, 194, 255))
    s = place_text(bg, d_p, 22, (310, 371))
    place_text(bg, "рт.ст.", 16, (s[0] + 4, s[1]), (190, 192, 194, 255))
    s = place_text(bg, n_p, 22, (430, 371))
    place_text(bg, "рт.ст.", 16, (s[0] + 4, s[1]), (190, 192, 194, 255))

    wc_m_img = f"wc_imgs/day/{m_wc}.png"
    wc_d_img = f"wc_imgs/day/{d_wc}.png"
    wc_n_img = f"wc_imgs/night/{n_wc}.png"

    place_img(bg, wc_m_img, (100, 100), (180, 155))
    place_img(bg, wc_d_img, (100, 100), (300, 155))
    place_img(bg, wc_n_img, (100, 100), (420, 155))

    # bg.save("ex.png")

    byte_io = BytesIO()
    # Сохраняем изображение в объект BytesIO
    bg.save(byte_io, format='PNG')
    # Сбрасываем указатель на начало объекта BytesIO
    byte_io.seek(0)
    # Создаем объект types.InputFile из объекта BytesIO
    input_file = types.InputFile(byte_io)
    return input_file


def get_day(city):
    global geolocator
    url = f"https://api.tomorrow.io/v4/weather/forecast?location={city}&timesteps=1h&units=metric&apikey=nMbAeWz1TAhYA7NeY9Ti24gjUqtSNUY1"  # %D0%9C%D0%B8%D0%BD%D1%81%D0%BA
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    response = response.json()
    print(response)
    time1 = response["timelines"]["hourly"][11]["time"]
    t1 = str(int(response["timelines"]["hourly"][11]["values"]["temperature"]))
    ws1 = str(int(response["timelines"]["hourly"][11]["values"]["windSpeed"]))
    pr1 = str(int(response["timelines"]["hourly"][11]["values"]["pressureSurfaceLevel"] / 1.333))
    wc1 = str(int(response["timelines"]["hourly"][11]["values"]["weatherCode"]))
    time2 = response["timelines"]["hourly"][17]["time"]
    t2 = str(int(response["timelines"]["hourly"][17]["values"]["temperature"]))
    ws2 = str(int(response["timelines"]["hourly"][17]["values"]["windSpeed"]))
    pr2 = str(int(response["timelines"]["hourly"][17]["values"]["pressureSurfaceLevel"] / 1.333))
    wc2 = str(int(response["timelines"]["hourly"][17]["values"]["weatherCode"]))
    time3 = response["timelines"]["hourly"][25]["time"]
    t3 = str(int(response["timelines"]["hourly"][25]["values"]["temperature"]))
    ws3 = str(int(response["timelines"]["hourly"][25]["values"]["windSpeed"]))
    pr3 = str(int(response["timelines"]["hourly"][25]["values"]["pressureSurfaceLevel"] / 1.333))
    wc3 = str(int(response["timelines"]["hourly"][25]["values"]["weatherCode"]))

    location = geolocator.geocode(city, timeout=10)

    lat = location.latitude
    lon = location.longitude

    city_astr = ephem.Observer()
    city_astr.lon = lon
    city_astr.lat = lat

    city_astr.date = datetime.date.today()

    # Вычислите время восхода и заката солнца
    sunrise_time = city_astr.next_rising(ephem.Sun()).datetime().strftime('%H:%M:%S')
    sunset_time = city_astr.next_setting(ephem.Sun()).datetime().strftime('%H:%M:%S')

    return [city, [t1, ws1, pr1, wc1], [t2, ws2, pr2, wc2], [t3, ws3, pr3, wc3], [sunrise_time, sunset_time]]


def forecast(fc):  # city, m_t, m_ws, m_p, m_wc, d_t, d_ws, d_p, d_wc, n_t, n_ws, n_p, n_wc

    city = fc[0]
    m_t, m_ws, m_p, m_wc = fc[1]
    d_t, d_ws, d_p, d_wc = fc[2]
    n_t, n_ws, n_p, n_wc = fc[3]

    def place_text(where, text, font_size, coords=(0, 0), color=(255, 255, 255, 255)):
        shadow_offset = 1
        shadow_color = (0, 0, 0, 128)

        font = ImageFont.truetype("arial.ttf", font_size)
        text_length = font.getlength(text)
        if coords[0] == 999:
            x = (bg_width - text_length) // 2
            y = coords[1]
        else:
            x, y = coords
        draw = ImageDraw.Draw(where)
        shadow_position = (x + shadow_offset, y + shadow_offset)
        draw.text(shadow_position, text, font=font, fill=shadow_color)
        text_position = (x, y)
        draw.text(text_position, text, font=font, fill=color)
        return int(x + text_length), int(y)

    def place_img(where, src, size=(100, 100), coords=(0, 0)):
        img = Image.open(src)
        img = img.resize(size)
        where.paste(img, coords, img)

    d_wc = int(d_wc)
    bg_img = "wbgs/d/"
    if d_wc == 1000 or d_wc == 1100:
        bg_img += "clear.jpg"
    elif d_wc == 2000 or d_wc == 2100:
        bg_img += "fog.jpg"
    elif d_wc == 1101:
        bg_img += "partly_cloudy.jpg"
    elif d_wc == 1102 or d_wc == 1001:
        bg_img += "cloudy.jpg"
    elif d_wc == 4000 or d_wc == 4200 or d_wc == 4001 or d_wc == 4201:
        bg_img += "rain.jpg"
    elif d_wc == 5001 or d_wc == 5100 or d_wc == 5000 or d_wc == 5101:
        bg_img += "snow.jpg"
    elif d_wc == 6000 or d_wc == 6200 or d_wc == 6001 or d_wc == 6201 or d_wc == 7102 or d_wc == 7000 or d_wc == 7101:
        bg_img += "hail.jpg"
    elif d_wc == 8000:
        bg_img += "storm.jpg"
    else:
        bg_img += "zzz.jpg"
    bg = Image.open(bg_img)

    bg_width, bg_height = bg.size

    logo = Image.open("wbgs/Бот - погоды - без фона.png")
    logo = logo.resize((115, 115))
    bg.paste(logo, (0, 0), logo)

    draw = ImageDraw.Draw(bg)
    place_text(bg, city.capitalize(), 28, (999, 30), (118, 206, 255, 255))
    place_text(bg, "Погода на завтра", 36, (999, 72))
    place_text(bg, "Утро", 21, (205, 127))
    place_text(bg, "День", 21, (324, 127))
    place_text(bg, "Ночь", 21, (444, 127))
    place_text(bg, "Температура", 21, (24, 263))
    place_text(bg, "Ветер", 21, (24, 316))
    place_text(bg, "Давление", 21, (24, 368))
    draw.line(((173, 253), (173, 253 + 144)), fill=(255, 255, 255), width=2)
    draw.line(((290, 253), (290, 253 + 144)), fill=(255, 255, 255), width=2)
    draw.line(((410, 253), (410, 253 + 144)), fill=(255, 255, 255), width=2)

    s = place_text(bg, m_t, 32, (193, 263))
    place_text(bg, "°С", 16, (s[0] + 4, s[1]), (190, 192, 194, 255))
    s = place_text(bg, d_t, 32, (310, 263))
    place_text(bg, "°С", 16, (s[0] + 4, s[1]), (190, 192, 194, 255))
    s = place_text(bg, n_t, 32, (430, 263))
    place_text(bg, "°С", 16, (s[0] + 4, s[1]), (190, 192, 194, 255))

    s = place_text(bg, m_ws, 22, (210, 319))
    place_text(bg, "м/с", 16, (s[0] + 4, s[1]), (190, 192, 194, 255))
    s = place_text(bg, d_ws, 22, (323, 319))
    place_text(bg, "м/с", 16, (s[0] + 4, s[1]), (190, 192, 194, 255))
    s = place_text(bg, n_ws, 22, (442, 319))
    place_text(bg, "м/с", 16, (s[0] + 4, s[1]), (190, 192, 194, 255))

    s = place_text(bg, m_p, 22, (193, 371))
    place_text(bg, "рт.ст.", 16, (s[0] + 4, s[1]), (190, 192, 194, 255))
    s = place_text(bg, d_p, 22, (310, 371))
    place_text(bg, "рт.ст.", 16, (s[0] + 4, s[1]), (190, 192, 194, 255))
    s = place_text(bg, n_p, 22, (430, 371))
    place_text(bg, "рт.ст.", 16, (s[0] + 4, s[1]), (190, 192, 194, 255))

    wc_m_img = f"wc_imgs/day/{m_wc}.png"
    wc_d_img = f"wc_imgs/day/{d_wc}.png"
    wc_n_img = f"wc_imgs/night/{n_wc}.png"

    place_img(bg, wc_m_img, (100, 100), (180, 155))
    place_img(bg, wc_d_img, (100, 100), (300, 155))
    place_img(bg, wc_n_img, (100, 100), (420, 155))

    # bg.save("ex.png")

    byte_io = BytesIO()
    # Сохраняем изображение в объект BytesIO
    bg.save(byte_io, format='PNG')
    # Сбрасываем указатель на начало объекта BytesIO
    byte_io.seek(0)
    # Создаем объект types.InputFile из объекта BytesIO
    input_file = types.InputFile(byte_io)
    return input_file


def get_3days(city):
    global geolocator
    url = f"https://api.tomorrow.io/v4/weather/forecast?location={city}&timesteps=1d&units=metric&apikey=nMbAeWz1TAhYA7NeY9Ti24gjUqtSNUY1"  # %D0%9C%D0%B8%D0%BD%D1%81%D0%BA
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    response = response.json()
    # print(response)

    week = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    d = datetime.datetime.weekday(datetime.datetime.now())
    dow1 = week[d + 1]
    dow2 = week[d + 2]
    dow3 = week[d + 3]

    t1 = str(int(response["timelines"]["daily"][1]["values"]["temperatureAvg"]))
    t2 = str(int(response["timelines"]["daily"][2]["values"]["temperatureAvg"]))
    t3 = str(int(response["timelines"]["daily"][3]["values"]["temperatureAvg"]))
    wc1 = str(int(response["timelines"]["daily"][1]["values"]["weatherCodeMin"]))
    wc2 = str(int(response["timelines"]["daily"][2]["values"]["weatherCodeMin"]))
    wc3 = str(int(response["timelines"]["daily"][3]["values"]["weatherCodeMin"]))

    return [city, [dow1, t1, wc1], [dow2, t2, wc2], [dow3, t3, wc3]]


def forecast3(fc):  # city, m_t, m_ws, m_p, m_wc, d_t, d_ws, d_p, d_wc, n_t, n_ws, n_p, n_wc

    city = fc[0]
    d1_dow, d1_t, d1_wc = fc[1]
    d2_dow, d2_t, d2_wc = fc[2]
    d3_dow, d3_t, d3_wc = fc[3]

    def place_text(where, text, font_size, coords=(0, 0), color=(255, 255, 255, 255)):
        shadow_offset = 1
        shadow_color = (0, 0, 0, 128)

        font = ImageFont.truetype("arial.ttf", font_size)
        text_length = font.getlength(text)
        if coords[0] == 999:
            x = (bg_width - text_length) // 2
            y = coords[1]
        else:
            x, y = coords
        draw = ImageDraw.Draw(where)
        shadow_position = (x + shadow_offset, y + shadow_offset)
        draw.text(shadow_position, text, font=font, fill=shadow_color)
        text_position = (x, y)
        draw.text(text_position, text, font=font, fill=color)
        return int(x + text_length), int(y)

    def place_img(where, src, size=(100, 100), coords=(0, 0)):
        img = Image.open(src)
        img = img.resize(size)
        where.paste(img, coords, img)

    d_wc = int(d2_wc)
    bg_img = "wbgs/d/"
    if d_wc == 1000 or d_wc == 1100:
        bg_img += "clear.jpg"
    elif d_wc == 2000 or d_wc == 2100:
        bg_img += "fog.jpg"
    elif d_wc == 1101:
        bg_img += "partly_cloudy.jpg"
    elif d_wc == 1102 or d_wc == 1001:
        bg_img += "cloudy.jpg"
    elif d_wc == 4000 or d_wc == 4200 or d_wc == 4001 or d_wc == 4201:
        bg_img += "rain.jpg"
    elif d_wc == 5001 or d_wc == 5100 or d_wc == 5000 or d_wc == 5101:
        bg_img += "snow.jpg"
    elif d_wc == 6000 or d_wc == 6200 or d_wc == 6001 or d_wc == 6201 or d_wc == 7102 or d_wc == 7000 or d_wc == 7101:
        bg_img += "hail.jpg"
    elif d_wc == 8000:
        bg_img += "storm.jpg"
    else:
        bg_img += "zzz.jpg"
    bg = Image.open(bg_img)

    bg_width, bg_height = bg.size

    logo = Image.open("wbgs/Бот - погоды - без фона.png")
    logo = logo.resize((115, 115))
    bg.paste(logo, (0, 0), logo)

    draw = ImageDraw.Draw(bg)
    place_text(bg, city.capitalize(), 28, (999, 30), (118, 206, 255, 255))
    place_text(bg, "Прогноз на 3 дня", 36, (999, 72))
    place_text(bg, d1_dow, 38, (40, 174))
    place_text(bg, d2_dow, 38, (40, 297))
    place_text(bg, d3_dow, 38, (40, 428))
    draw.line(((40, 265), (40 + 460, 265)), fill=(255, 255, 255), width=2)
    draw.line(((40, 395), (40 + 460, 395)), fill=(255, 255, 255), width=2)

    s = place_text(bg, d1_t, 42, (371, 174))
    place_text(bg, "°С", 22, (s[0] + 4, s[1]), (190, 192, 194, 255))
    s = place_text(bg, d2_t, 42, (371, 304))
    place_text(bg, "°С", 22, (s[0] + 4, s[1]), (190, 192, 194, 255))
    s = place_text(bg, d3_t, 42, (371, 434))
    place_text(bg, "°С", 22, (s[0] + 4, s[1]), (190, 192, 194, 255))

    wc_d1_img = f"wc_imgs/day/{d1_wc}.png"
    wc_d2_img = f"wc_imgs/day/{d2_wc}.png"
    wc_d3_img = f"wc_imgs/night/{d3_wc}.png"

    place_img(bg, wc_d1_img, (140, 140), (178, 130))
    place_img(bg, wc_d2_img, (140, 140), (178, 260))
    place_img(bg, wc_d3_img, (140, 140), (178, 390))

    # bg.save("ex.png")

    byte_io = BytesIO()
    # Сохраняем изображение в объект BytesIO
    bg.save(byte_io, format='PNG')
    # Сбрасываем указатель на начало объекта BytesIO
    byte_io.seek(0)
    # Создаем объект types.InputFile из объекта BytesIO
    input_file = types.InputFile(byte_io)
    return input_file



async def on_chat_member_joined(message: types.ChatMemberUpdated):
    chat_title = message.chat.title
    print(f"The bot was added to the chat {chat_title}")

async def send_forecast(bot: Bot, city):
    r = requests.get(f"http://127.0.0.1:8000/getChatId/?city={city.lower()}").json()
    chat_id = r["data"]


    h=datetime.datetime.now().hour
    m=datetime.datetime.now().minute
    t=str(h)+':'+str(m)
    if h <= 10:
        tfrc = get_today(city)
        await bot.send_photo(chat_id=chat_id, photo=todayforecast(tfrc))
    elif h <= 18:
        tfrc = get_3days(city)
        await bot.send_photo(chat_id=chat_id, photo=forecast3(tfrc))
    elif h <= 24:
        tfrc = get_day(city)
        await bot.send_photo(chat_id=chat_id, photo=forecast(tfrc))



@dp.message_handler(commands=['update'])
async def update(message: types.Message):
    r = requests.get("http://127.0.0.1:8000/getSchedule").json()
    if scheduler.get_jobs():
        for j in scheduler.get_jobs():
            j.remove()
        for i in r["data"]:
            scheduler.add_job(send_forecast, trigger='cron', hour=i[1][0], minute=i[1][1], start_date=datetime.datetime.now(), kwargs={'bot': bot, 'city':i[0]})
    else:
        for i in r["data"]:
            scheduler.add_job(send_forecast, trigger='cron', hour=i[1][0], minute=i[1][1], start_date=datetime.datetime.now(), kwargs={'bot': bot, 'city':i[0]})
    
        scheduler.start()
    await message.answer("Расписание успешно обновлено")

    


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if message.chat.type in [types.ChatType.GROUP, types.ChatType.SUPERGROUP]:
        await message.reply("Здравствуй!\nЧтобы указать город для группы отправь комманду /add <название города>")
    else:
        await message.answer("Здравствуй!\nЭто бот с погодой по расписанию!\nЧтобы начать им пользоваться, добавьте его в группу")



@dp.message_handler(commands=['add'])
async def create(message: types.Message):
    city = message.text.split(' ')[1]
    r = requests.get(f"http://127.0.0.1:8000/askForApproval/?name={message.chat.title}&chat_id={message.chat.id}&city={city}").json()
    if int(r["data"]) == 200:
        await message.answer("Привет! Запрос на одобрение в группу отправлен. Войдите в панель администратора для дальнейшей настройки")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
