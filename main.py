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
    def __init__(self, user_id, name, user_time, shirota: str, dolgota: str, znak, bnews: bool, bhoro: bool,
                 bweat: bool):
        self.user_id = user_id
        self.name = name
        self.shirota = shirota
        self.dolgota = dolgota
        self.user_time = user_time
        self.znak = znak
        self.bnews = bnews
        self.bhoro = bhoro
        self.bweat = bweat

    def planing(self):
        schedule.every().day.at(self.user_time).do(sendin, self)


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
    print(user.shirota, type(user.shirota))
    url = "https://api.weather.yandex.ru/v2/forecast?lat=" + user.shirota + "&lon=" + user.dolgota + "&ru_RU"
    print(url)
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
        "Овен" : "aries",
        "Телец" : "taurus",
        "Близнецы" : "gemini",
        "Рак" : "cancer",
        "Лев" : "leo",
        "Дева" : "virgo",
        "Весы" : "libra",
        "Скорпион" : "scorpio",
        "Стрелец" : "sagittarius",
        "Козерог" : "capricorn",
        "Водолей" : "aquarius",
        "Рыбы" : "pisces"
    }

    znak_h=znaks[user.znak]
    r = requests.get('https://horo.mail.ru/prediction/'+znak_h+"/today/")
    html = BS(r.text, 'html.parser')
    horoscope_res = html.find('div', class_='article__item article__item_alignment_left article__item_html').text
    bot.send_message(user.user_id, f'Ваш гороскоп на сегодня:\n {user.znak} - {horoscope_res}')


# функция получения новостей


def news(user):
    r = requests.get('https://ria.ru/')
    html = BS(r.text, 'html.parser')
    title1 = html.find('div', class_='cell-main-photo__title').text
    link = html.find('a', class_='cell-main-photo__link')['href']
    news_time = html.find('div', class_='cell-info__date').text
    mas_news = [[title1, news_time, link]]
    chk = 0
    for titles in html.find_all('div', class_='cell-list__item m-no-image'):
        if chk == 2:
            break
        else:
            news_name=titles.span.text
            news_time = titles.div.text
            news_link = titles.a['href']
            mas_news.append([news_name, news_time, news_link])
        chk += 1
    print(mas_news)
    text = (
        f"Главные новости за последнее время:\n -------------- \n {mas_news[0][0]} \n Время новости: {mas_news[0][1]}, Источник {mas_news[0][2]}\n"
        f"-------------- \n {mas_news[1][0]} \n Время новости: {mas_news[1][1]}, Источник {mas_news[1][2]}\n"
        f"-------------- \n {mas_news[2][0]} \n Время новости: {mas_news[2][1]}, Источник {mas_news[2][2]}\n")
    bot.send_message(user, text)


# функция аутентификации нового пользователя

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет, чтобы начать пользоваться этим ботом тебе нужно зарегистрироваться, '
                                      'для этого отправь /reg')


DATA = []


@bot.message_handler(commands=['reg'])
def reg_first(message):
    mesg = bot.send_message(message.chat.id, 'Укажите ваше имя')
    bot.register_next_step_handler(mesg, reg_name)


def reg_name(message):
    global name
    name = message.text
    bot.send_message(message.chat.id, 'Укажите город в котором вы живете')
    bot.register_next_step_handler(message, reg_city)


def reg_city(message):
    city = message.text.capitalize()
    print(city, type(city))
    f = open('goroda.txt')
    f = f.read()
    f = f.split('\n')
    print(f)
    flag = 0
    global shir
    global dolg
    for i in range(len(f)):
        if city == str(f[i]).split('\t')[0]:
            shir = str(f[i]).split('\t')[1]
            dolg = str(f[i]).split('\t')[2]
            flag = 1
            break
    else:
        bot.send_message(message.chat.id, 'Город указан не верно, либо ваш город слишком маленький, попробуйте еще раз')
        bot.register_next_step_handler(message, reg_city)
    if flag == 1:
        bot.send_message(message.chat.id, 'Укажите ваш знак зодиака')
        bot.register_next_step_handler(message, reg_zodiak)


def reg_zodiak(message):
    global zodiak
    zodiak = message.text.capitalize()
    zodiaks = ["Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева", "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей",
               "Рыбы"]
    if zodiak not in zodiaks:
        bot.send_message(message.chat.id, 'Знак зодиака указан не верно, повторите попытку')
        bot.register_next_step_handler(message, reg_zodiak)
    else:
        bot.send_message(message.chat.id,
                         'Укажите время в которое вам хотелось бы получать сообщения строго в формате ЧЧ:ММ')
        bot.register_next_step_handler(message, reg_time)


def reg_time(message):
    global user_time
    user_time = message.text
    if is_valid_time(user_time):
        bot.send_message(message.chat.id, 'Укажите хотите ли вы получать новости (да/нет)')
        bot.register_next_step_handler(message, reg_news)
    else:
        bot.send_message(message.chat.id, 'Время указано не верно повторите попытку строго в формате ЧЧ:ММ')
        bot.register_next_step_handler(message, reg_time)


def reg_news(message):
    global need_news
    flag = 0
    if message.text.capitalize() == 'Да':
        need_news = True
        flag = 1
    elif message.text.capitalize() == 'Нет':
        need_news = False
        flag = 1
    else:
        bot.send_message(message.chat.id, 'Неправильный ввод, введите да или нет')
        bot.register_next_step_handler(message, reg_news)
    if flag == 1:
        bot.send_message(message.chat.id, 'Укажите хотите ли вы получать гороскоп (да/нет)')
        bot.register_next_step_handler(message, reg_horoscope)


def reg_horoscope(message):
    global need_horoscope
    flag = 0
    if message.text.capitalize() == 'Да':
        need_horoscope = True
        flag = 1
    elif message.text.capitalize() == 'Нет':
        need_horoscope = False
        flag = 1
    else:
        bot.send_message(message.chat.id, 'Неправильный ввод, введите да или нет')
        bot.register_next_step_handler(message, reg_horoscope)
    if flag == 1:
        bot.send_message(message.chat.id, 'Укажите хотите ли вы получать информацию о погоде (да/нет)')
        bot.register_next_step_handler(message, reg_weather)


def reg_weather(message):
    global need_weather
    global user_id1
    flag = 0
    if message.text.capitalize() == 'Да':
        need_weather = True
        flag = 1
    elif message.text.capitalize() == 'Нет':
        need_weather = False
        flag = 1
    else:
        bot.send_message(message.chat.id, 'Неправильный ввод, введите да или нет')
        bot.register_next_step_handler(message, reg_weather)
    if flag == 1:
        bot.send_message(message.chat.id, 'Спасибо, вы зарегистрированы!')
        user_id1 = message.chat.id
        final_reg()


def final_reg():
    if User(user_id=user_id1, name=name, user_time=user_time, shirota=shir, dolgota=dolg, znak=zodiak, bnews=need_news,
            bhoro=need_horoscope, bweat=need_weather) not in DATA:
        create_users = 'INSERT INTO users (user_id, name, user_time, shirota, dolgota, znak, news, horoscope, weather) values(?, ?, ?, ?, ?, ?, ?, ?, ?)'
        DATA.append(
            User(user_id=user_id1, name=name, user_time=user_time, shirota=shir, dolgota=dolg, znak=zodiak,
                 bnews=need_news,
                 bhoro=need_horoscope, bweat=need_weather))
        DATA[-1].planing()
        data = [
            (str(user_id1), name, user_time, shir, dolg, zodiak, int(need_news), int(need_horoscope), int(need_weather))
        ]

        with connection:
            connection.executemany(create_users, data)
    print(DATA)


@bot.message_handler(commands=['change'])
def change_user_timer():
    search_id = 10
    for user_id, User in enumerate(DATA, start=10):  # (0, User1), (1, User2), ....
        if User.user_id == search_id:
            DATA.pop(user_id)
            DATA.append(User(user_id=user_id, name=User.name, time='time'))


def schedule_checker():
    while True:
        schedule.run_pending()
        time.sleep(10)  # Задержка в 1 секунду, чтобы не перегружать CPU


# Запуск потока для проверки расписания
schedule_thread = threading.Thread(target=schedule_checker)
schedule_thread.start()

# Запуск бота в основном потоке
bot.polling(none_stop=True)
