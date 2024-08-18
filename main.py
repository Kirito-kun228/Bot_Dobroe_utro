import telebot
import schedule
import os
import time
import requests
import json
import sqlite3 as sl
from sqlite3 import Error
from telebot import types

token = os.environ.get('TOKEN')

bot = telebot.TeleBot(token)


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
    def __init__(self, user_id, name, user_time, shirota, dolgota, znak, bnews: bool, bhoro: bool, bweat: bool):
        self.user_id = user_id
        self.name = name
        self.shirota = shirota
        self.dolgota = dolgota
        self.user_time = user_time
        self.znak = znak
        self.bnews = bnews
        self.bhoro = bhoro
        self.bweat = bweat





    def sendin(self):
        bot.send_message(self.user_id, 'Доброе утро, ' + self.name)
        if self.bweat:
            weather(self.user_id)
        if self.bhoro:
            horoscope(self.user_id)
        if self.bnews:
            news(self.user_id)


# функция получения погоды
# во всех функциях используется временное решение с сообщением
# до подключения БД
def weather(user):
    bot.send_message(user, 'Здесь будет погода')

    """url = "https://api.weather.yandex.ru/v2/informers?lat=55.75222&lon=37.61556"
    headers = {"X-Yandex-API-Key": "27eb5fc1-8eb9-4077-94b9-7d1d1c5dff07"}
    r = requests.get(url=url, headers=headers)
    bot.send_message(user.user_id, r.text)"""


# функция получения гороскопа
def horoscope(user):
    bot.send_message(user, 'Здесь будет гороскоп')


# функция получения новостей

def news(user):
    bot.send_message(user, 'Здесь будут новости')


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
    # сделать проверку времени
    bot.send_message(message.chat.id, 'Укажите хотите ли вы получать новости (да/нет)')
    bot.register_next_step_handler(message, reg_news)


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
            User(user_id=user_id1, name=name, user_time=user_time, shirota=shir, dolgota=dolg, znak=zodiak, bnews=need_news,
                 bhoro=need_horoscope, bweat=need_weather))
        data = [
            (str(user_id1), name, user_time, shir, dolg, zodiak, int(need_news), int(need_horoscope), int(need_weather))
        ]

        with connection:
            connection.executemany(create_users, data)
    print(DATA)

    schedule.every().day.at(DATA[-1].user_time).do(DATA[-1].sendin())



@bot.message_handler(commands=['change'])
def change_user_timer():
    search_id = 10
    for user_id, User in enumerate(DATA, start=10):  # (0, User1), (1, User2), ....
        if User.user_id == search_id:
            DATA.pop(user_id)
            DATA.append(User(user_id=user_id, name=User.name, time='time'))


while True:
    # в бесконечном цикле постоянно опрашиваем бота — есть ли новые сообщения
    schedule.run_pending()


    bot.polling(none_stop=True, interval=0)
# если возникла ошибка — сообщаем про исключение и продолжаем работу
