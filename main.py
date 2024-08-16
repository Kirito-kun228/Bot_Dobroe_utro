import telebot
import schedule
import os
import time
import requests
import json
import sqlite3 as sl
from sqlite3 import Error

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


# функция получения погоды
# во всех функциях используется временное решение с сообщением
# до подключения БД
@bot.message_handler(commands=['get_weather', 'weather', 'pogoda'])
def weather(message):
    url = "https://api.weather.yandex.ru/v2/informers?lat=55.75222&lon=37.61556"
    headers = {"X-Yandex-API-Key": "27eb5fc1-8eb9-4077-94b9-7d1d1c5dff07"}
    r = requests.get(url=url, headers=headers)
    bot.send_message(message.chat.id, r.text)


# функция получения гороскопа
def horoscope():
    pass


# функция получения новостей
def news():
    pass


# функция аутентификации нового пользователя
@bot.message_handler(commands=['reg'])
def registration(message):
    user_id1 = message.chat.id
    create_users = 'INSERT INTO users (user_id, time, weather, news, horoscope) values(?, ?, ?, ?, ?)'
    data = [
        (str(user_id1), '9:00', 0, 0, 0)
    ]
    with connection:
        connection.executemany(create_users, data)
    bot.send_message(message.from_user.id, 'Принято, спасибо!', parse_mode='Markdown')

while True:
        # в бесконечном цикле постоянно опрашиваем бота — есть ли новые сообщения
        try:
            bot.polling(none_stop=True, interval=0)
        # если возникла ошибка — сообщаем про исключение и продолжаем работу
        except Exception as e:
            print(e)
