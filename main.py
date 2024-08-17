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
  time TEXT NOT NULL,
  weather INTEGER,
  news INTEGER,
  horoscope INTEGER
);
"""
execute_query(connection, create_users_table)


class User:
    def __init__(self, user_id, name, time: str, bnews: bool, bhoro: bool, bweat: bool):
        self.user_id = user_id
        self.name = name
        self.time = time
        self.bnews = bnews
        self.bhoro = bhoro
        self.bweat = bweat
        schedule.every().day.at(time).do(sendin(self))


# функция получения погоды
# во всех функциях используется временное решение с сообщением
# до подключения БД
def weather(user):
    url = "https://api.weather.yandex.ru/v2/informers?lat=55.75222&lon=37.61556"
    headers = {"X-Yandex-API-Key": "27eb5fc1-8eb9-4077-94b9-7d1d1c5dff07"}
    r = requests.get(url=url, headers=headers)
    bot.send_message(user.user_id, r.text)


# функция получения гороскопа
def horoscope(user):
    pass


# функция получения новостей

def news():
    pass


# функция аутентификации нового пользователя

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет, чтобы начать пользоваться этим ботом тебе нужно зарегистрироваться, для этого отправь /reg')


def sendin(user):
    bot.send_message(user.user_id, 'Доброе утро!')
    if user.bweat:
        weather(user)
    if user.bhoro:
        horoscope(user)
    if user.bnews:
        news()


DATA = []


@bot.message_handler(commands=['reg'])
def registration(message):
    keyboard = types.InlineKeyboardMarkup()
    key_city = types.InlineKeyboardButton(text='Овен', callback_data='zodiac')
    keyboard.add(key_city)
    user_id1 = message.chat.id








    if User(user_id=user_id1, name='name',time='time') not in DATA:
        create_users = 'INSERT INTO users (user_id, time, weather, news, horoscope) values(?, ?, ?, ?, ?)'
        DATA.append(User(user_id=user_id1, name='name', time='time'))

        data = [
            (str(user_id1), "09:00", 0, 0, 0)
        ]

        with connection:
            connection.executemany(create_users, data)
        bot.send_message(message.from_user.id, 'Принято, спасибо!', parse_mode='Markdown')


@bot.message_handler(commands=['change'])
def change_user_timer():
    search_id = 10
    for user_id, User in enumerate(DATA, start=10):  # (0, User1), (1, User2), ....
        if User.user_id == search_id:
            DATA.pop(user_id)
            DATA.append(User(user_id=user_id, name=User.name, time='time'))


while True:
    # в бесконечном цикле постоянно опрашиваем бота — есть ли новые сообщения
    try:
        bot.polling(none_stop=True, interval=0)
    # если возникла ошибка — сообщаем про исключение и продолжаем работу
    except Exception as e:
        print(e)

"""





# lst = [1, 2, 3]
# lst.pop(1) # [1, 3]

"""
