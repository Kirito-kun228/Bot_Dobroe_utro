import telebot
import schedule
import os
import time
import json

token = os.environ.get('TOKEN')

bot = telebot.TeleBot(token)


# функция получения погоды
def weather():
    pass


# функция получения гороскопа
def horoscope():
    pass


# функция получения новостей
def news():
    pass


def main():
    print('1')


schedule.every().day.at('09:00').do(main)

while True:
    schedule.run_pending()
    time.sleep(1)
