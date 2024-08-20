import cursor
import telebot
import schedule
import os
import time
import requests
from bs4 import BeautifulSoup as BS
import json
import sqlite3 as sl
from sqlite3 import Error
from telebot import types
import threading
from datetime import datetime

token = os.environ.get('TOKEN')

bot = telebot.TeleBot(token)


def is_valid_time(time_str):
    try:
        # Попробуем распарсить строку времени
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        # Если возникла ошибка, значит формат неправильный
        return False


# подключение БД
def create_connection(path):
    conn = None
    try:
        conn = sl.connect('reports.db', check_same_thread=False)
        print("Подключение к базе данных SQLite прошло успешно")
    except Error as e:
        print(f"Произошла ошибка '{e}'")
    return conn


connection = create_connection("reports.db")


# функция отправки запросов
def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Запрос выполнен успешно")
    except Error as e:
        print(f"Произошла ошибка '{e}'")


create_users_table = """
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  name TEXT NOT NULL,
  user_time TEXT NOT NULL,
  user_days TEXT NOT NULL,
  shirota FLOAT,
  dolgota FLOAT,
  znak TEXT,
  news INTEGER,
  horoscope INTEGER,
  weather INTEGER
  
);
"""
execute_query(connection, create_users_table)


# user_id, name, time, shirota, dolgota, znak, news, horoscope, weather

class User:
    def __init__(self,
                 user_id=None,
                 name=None,
                 user_time=None,
                 user_days=[],
                 shirota: str = None,
                 dolgota: str = None,
                 znak=None,
                 bnews: bool = None,
                 bhoro: bool = None,
                 bweat: bool = None
                 ):
        self.user_id = user_id
        self.name = name
        self.shirota = shirota
        self.dolgota = dolgota
        self.user_time = user_time
        self.user_days = user_days
        self.znak = znak
        self.bnews = bnews
        self.bhoro = bhoro
        self.bweat = bweat

    def planing(self):
        for day in self.user_days:
            if day == "понедельник":
                schedule.every().monday.at(self.user_time).do(sendin, self)
            elif day == "вторник":
                schedule.every().tuesday.at(self.user_time).do(sendin, self)
            elif day == "среда":
                schedule.every().wednesday.at(self.user_time).do(sendin, self)
            elif day == "четверг":
                schedule.every().thursday.at(self.user_time).do(sendin, self)
            elif day == "пятница":
                schedule.every().friday.at(self.user_time).do(sendin, self)
            elif day == "суббота":
                schedule.every().saturday.at(self.user_time).do(sendin, self)
            elif day == "воскресенье":
                schedule.every().sunday.at(self.user_time).do(sendin, self)


def sendin(s_user):
    bot.send_message(s_user.user_id, 'Доброе утро, ' + s_user.name)
    if s_user.bweat:
        weather(s_user)
    if s_user.bhoro:
        horoscope(s_user)
    if s_user.bnews:
        news(s_user.user_id)


# функция получения погоды
# во всех функциях используется временное решение с сообщением
# до подключения БД
def weather(user):
    url = "https://api.weather.yandex.ru/v2/forecast?lat=" + user.shirota + "&lon=" + user.dolgota + "&ru_RU"
    headers = {"X-Yandex-Weather-Key": "27eb5fc1-8eb9-4077-94b9-7d1d1c5dff07"}
    r = requests.get(url=url, headers=headers)
    data = json.loads(r.text)
    fact = data["fact"]
    con_trans = {
        "clear": "ясно",
        "partly-cloudy": "малооблачно",
        "cloudy": "облачно с прояснениями",
        "overcast": "пасмурно",
        "light-rain": "небольшой дождь",
        "rain": "дождь",
        "heavy-rain": "сильный дождь",
        "showers": "ливень",
        "wet-snow": "дождь со снегом",
        "light-snow": "небольшой снег",
        "snow": "снег",
        "snow-showers": "снегопад",
        "hail": "град",
        "thunderstorm": "гроза",
        "thunderstorm-with-rain": "дождь с грозой",
        "thunderstorm-with-hail": "гроза с градом"
    }
    bot.send_message(user.user_id,
                     text=f'Температура за окном {fact["temp"]}°, ощущается как {fact["feels_like"]}°. На улице сейчас {con_trans[fact["condition"]]}')


# функция получения гороскопа
def horoscope(user):
    znaks = {
        "Овен": "aries",
        "Телец": "taurus",
        "Близнецы": "gemini",
        "Рак": "cancer",
        "Лев": "leo",
        "Дева": "virgo",
        "Весы": "libra",
        "Скорпион": "scorpio",
        "Стрелец": "sagittarius",
        "Козерог": "capricorn",
        "Водолей": "aquarius",
        "Рыбы": "pisces"
    }

    znak_h = znaks[user.znak]
    r = requests.get('https://horo.mail.ru/prediction/' + znak_h + "/today/")
    html = BS(r.text, 'html.parser')
    horoscope_res = html.find('div', class_='article__item article__item_alignment_left article__item_html').text
    bot.send_message(user.user_id, f'Ваш гороскоп на сегодня:\n {user.znak} - {horoscope_res}')


# функция получения новостей


def news(user):
    r = requests.get('https://ria.ru/economy/')
    html = BS(r.text, 'html.parser')
    names = []
    times = []
    links = []
    chk = 0
    for titles in html.find_all('a', class_='list-item__title color-font-hover-only'):
        if chk == 3:
            break
        else:
            names.append(titles.text)
        chk += 1
    chk = 0
    for infos in html.find_all('div', class_='list-item__date'):
        if chk == 3:
            break
        else:
            times.append(infos.text)
        chk += 1
    chk = 0
    for ssilka in html.find_all('a', class_='list-item__image'):
        if chk == 3:
            break
        else:
            links.append(ssilka['href'])
        chk += 1
    mas_news = [names, times, links]
    print(mas_news)

    text = (
        f"Главные новости за последнее время:\n -------------- \n {mas_news[0][0]} \n Время новости: {mas_news[1][0]}, Источник {mas_news[2][0]}\n"
        f"-------------- \n {mas_news[0][1]} \n Время новости: {mas_news[1][1]}, Источник {mas_news[2][1]}\n"
        f"-------------- \n {mas_news[0][2]} \n Время новости: {mas_news[1][2]}, Источник {mas_news[2][2]}\n")
    bot.send_message(user, text)


# функция аутентификации нового пользователя

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет, чтобы начать пользоваться этим ботом тебе нужно зарегистрироваться, '
                                      'для этого отправь /reg')


DATA = []

request_to_read_data = "SELECT * FROM users"

cursor = connection.cursor()

cursor.execute(request_to_read_data)

data = cursor.fetchall()

for i in range(len(data)):
    DATA.append(User(user_id=data[i][1],
                     name=data[i][2],
                     user_time=data[i][3],
                     user_days=json.loads(data[i][3]),
                     shirota=data[i][5],
                     dolgota=data[i][6],
                     znak=data[i][7],
                     bnews=data[i][8],
                     bhoro=data[i][9],
                     bweat=data[i][10])
                )

print(DATA)


@bot.message_handler(commands=['reg'])
def reg_first(message):
    user = User(user_id=message.chat.id)
    search_id = message.chat.id
    flag = 0
    for user_id, user in enumerate(DATA):
        if int(user.user_id) == int(search_id):
            flag = 1
            bot.send_message(message.chat.id, 'Вы уже зарегистрированы')
    if flag == 0:
        mesg = bot.send_message(message.chat.id, 'Укажите ваше имя')
        bot.register_next_step_handler(mesg, reg_name, user)


def reg_name(message, user):
    user.name = message.text
    bot.send_message(message.chat.id, 'Укажите город в котором вы живете')
    bot.register_next_step_handler(message, reg_city, user)


def reg_city(message, user):
    city = message.text.capitalize()
    f = open('goroda.txt')
    f = f.read()
    f = f.split('\n')
    print(f)
    flag = 0
    for i in range(len(f)):
        if city == str(f[i]).split('\t')[0]:
            user.shirota = str(f[i]).split('\t')[1]
            user.dolgota = str(f[i]).split('\t')[2]
            flag = 1
            break
    else:
        bot.send_message(message.chat.id, 'Город указан не верно, либо ваш город слишком маленький, попробуйте еще раз')
        bot.register_next_step_handler(message, reg_city, user)
    if flag == 1:
        bot.send_message(message.chat.id, 'Укажите ваш знак зодиака')
        bot.register_next_step_handler(message, reg_zodiak, user)


def reg_zodiak(message, user):
    zodiak = message.text.capitalize()
    zodiaks = ["Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева", "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей",
               "Рыбы"]
    if zodiak not in zodiaks:
        bot.send_message(message.chat.id, 'Знак зодиака указан не верно, повторите попытку')
        bot.register_next_step_handler(message, reg_zodiak, user)
    else:
        user.znak = zodiak
        bot.send_message(message.chat.id,
                         'Укажите время в которое вам хотелось бы получать сообщения строго в формате ЧЧ:ММ')
        bot.register_next_step_handler(message, reg_time, user)


def reg_time(message, user):
    user_time = message.text
    if is_valid_time(user_time):
        user.user_time = user_time
        bot.send_message(message.chat.id, 'Укажите дни недели через запятую (например: Понедельник, Среда, Пятница)')
        bot.register_next_step_handler(message, reg_days, user)
    else:
        bot.send_message(message.chat.id, 'Время указано неверно. Повторите попытку строго в формате ЧЧ:ММ')
        bot.register_next_step_handler(message, reg_time, user)


def reg_days(message, user):
    days = message.text.lower().replace(" ", "").split(',')
    valid_days = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
    user_days = [day for day in days if day in valid_days]

    if user_days:
        user.user_days = user_days
        bot.send_message(message.chat.id, 'Укажите хотите ли вы получать новости (да/нет)')
        bot.register_next_step_handler(message, reg_news, user)
    else:
        bot.send_message(message.chat.id, 'Некорректно указаны дни недели. Попробуйте еще раз.')
        bot.register_next_step_handler(message, reg_days, user)


def reg_news(message, user):
    flag = 0
    need_news = None
    if message.text.capitalize() == 'Да':
        need_news = True
        flag = 1
    elif message.text.capitalize() == 'Нет':
        need_news = False
        flag = 1
    else:
        bot.send_message(message.chat.id, 'Неправильный ввод, введите да или нет')
        bot.register_next_step_handler(message, reg_news, user)
    if flag == 1:
        user.bnews = need_news
        bot.send_message(message.chat.id, 'Укажите хотите ли вы получать гороскоп (да/нет)')
        bot.register_next_step_handler(message, reg_horoscope, user)


def reg_horoscope(message, user):
    flag = 0
    need_horoscope = None
    if message.text.capitalize() == 'Да':
        need_horoscope = True
        flag = 1
    elif message.text.capitalize() == 'Нет':
        need_horoscope = False
        flag = 1
    else:
        bot.send_message(message.chat.id, 'Неправильный ввод, введите да или нет')
        bot.register_next_step_handler(message, reg_horoscope, user)
    if flag == 1:
        user.bhoro = need_horoscope
        bot.send_message(message.chat.id, 'Укажите хотите ли вы получать информацию о погоде (да/нет)')
        bot.register_next_step_handler(message, reg_weather, user)


def reg_weather(message, user):
    flag = 0
    need_weather = None
    if message.text.capitalize() == 'Да':
        need_weather = True
        flag = 1
    elif message.text.capitalize() == 'Нет':
        need_weather = False
        flag = 1
    else:
        bot.send_message(message.chat.id, 'Неправильный ввод, введите да или нет')
        bot.register_next_step_handler(message, reg_weather, user)
    if flag == 1:
        user.bweat = need_weather
        bot.send_message(message.chat.id, 'Спасибо, вы зарегистрированы!')
        final_reg(user)


def final_reg(user):
    create_users = 'INSERT INTO users (user_id, name, user_time, user_days, shirota, dolgota, znak, news, horoscope, weather) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
    DATA.append(user)
    user.planing()
    user_id = user.user_id
    name = user.name
    shir = user.shirota
    dolg = user.dolgota
    user_time = user.user_time
    user_days = json.dumps(user.user_days)
    zodiak = user.znak
    need_news = user.bnews
    need_horoscope = user.bhoro
    need_weather = user.bweat
    data = [
        (str(user_id), name, user_time, user_days, shir, dolg, zodiak, int(need_news), int(need_horoscope), int(need_weather))
    ]
    with connection:
        connection.executemany(create_users, data)
    print(DATA)


@bot.message_handler(commands=['change'])
def change_user_timer(message):
    search_id = message.chat.id
    for user_id, user in enumerate(DATA):
        if int(user.user_id) == int(search_id):
            DATA.pop(user_id)
            print(DATA)
            user_id_to_delete = user.user_id
            request_to_delete_data = "DELETE FROM users WHERE user_id = ?"
            cursor.execute(request_to_delete_data, (user_id_to_delete,))
            mesg = bot.send_message(message.chat.id, 'Регистрация начата заново, укажите ваше имя')
            user = User(user_id=message.chat.id)
            bot.register_next_step_handler(mesg, reg_name, user)
            break
    else:
        bot.send_message(message.chat.id, 'Вы еще не зарегистрированы')


def schedule_checker():
    while True:
        schedule.run_pending()
        time.sleep(10)  # Задержка в 1 секунду, чтобы не перегружать CPU


# Запуск потока для проверки расписания
schedule_thread = threading.Thread(target=schedule_checker)
schedule_thread.start()

# Запуск бота в основном потоке
bot.polling(none_stop=True)
