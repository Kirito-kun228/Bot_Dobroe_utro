import telebot
import schedule
import os
import time
import requests
import json

token = os.environ.get('TOKEN')

bot = telebot.TeleBot(token)


# функция получения погоды
# во всех функциях используется временное решение с сообщением
# до подключения БД
@bot.message_handler(commands=['get_weather', 'weather', 'pogoda'])
def weather(message):
    url = "https://api.weather.yandex.ru/v2/informers?lat=55.75222&lon=37.61556"
    headers = {"X-Yandex-API-Key": "weather token"}
    r = requests.get(url=url, headers=headers)
    bot.send_message(message.chat.id, r.text)



# функция получения гороскопа
def horoscope():
    pass


# функция получения новостей
def news():
    pass


# функция аутентификации нового пользователя
@bot.message_handler(commands=['start'])
def registration(message):
    pass


def main():
    print('1')


schedule.every().day.at('09:00').do(main)

while True:
    schedule.run_pending()
    time.sleep(1)
