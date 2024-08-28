import telebot
import schedule
import os
import time
import sqlite3 as sl
import re
from sqlite3 import Error
import threading

token = os.environ.get('TOKEN')

bot = telebot.TeleBot(token)


# Функция проверки формата времени

def is_valid_time(time_str):
    # Регулярное выражение для проверки формата времени HH:MM
    time_pattern = re.compile(r'^([01]\d|2[0-3]):([0-5]\d)$')

    if time_pattern.match(time_str):
        return True
    else:
        return False


# подключение к БД
def create_connection(path):
    conn = None
    try:
        conn = sl.connect('reports.db', check_same_thread=False)
        print("Подключение к базе данных SQLite прошло успешно")
    except Error as e:
        print(f"Произошла ошибка '{e}'")
    return conn


connection = create_connection("reports.db")


# функция отправки запросов к БД
def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Запрос выполнен успешно")
    except Error as e:
        print(f"Произошла ошибка '{e}'")


# Создание таблицы пользователей в БД, если она не существует
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


# Класс пользователя
class User:
    def __init__(self, user_id=None, name=None, user_time=None, user_days=[], shirota=None, dolgota=None, znak=None,
                 bnews=None, bhoro=None, bweat=None):
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
                schedule.every().monday.at(self.user_time).tag(self.user_id).do(sendin, self)
            elif day == "вторник":
                schedule.every().tuesday.at(self.user_time).tag(self.user_id).do(sendin, self)
            elif day == "среда":
                schedule.every().wednesday.at(self.user_time).tag(self.user_id).do(sendin, self)
            elif day == "четверг":
                schedule.every().thursday.at(self.user_time).tag(self.user_id).do(sendin, self)
            elif day == "пятница":
                schedule.every().friday.at(self.user_time).tag(self.user_id).do(sendin, self)
            elif day == "суббота":
                schedule.every().saturday.at(self.user_time).tag(self.user_id).do(sendin, self)
            elif day == "воскресенье":
                schedule.every().sunday.at(self.user_time).tag(self.user_id).do(sendin, self)

    def remove_plan(self):
        schedule.clear(self.user_id)


# Функция отправки сообщения пользователю



# функция аутентификации нового пользователя
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет, чтобы начать пользоваться этим ботом тебе нужно зарегистрироваться, '
                                      'для этого отправь /reg, если вы хотите изменить свои данные используйте /edit')


# Глобальный список пользователей
DATA = []

request_to_read_data = "SELECT * FROM users"
cursor = connection.cursor()
cursor.execute(request_to_read_data)
data = cursor.fetchall()

for i in range(len(data)):
    DATA.append(User(user_id=data[i][1],
                     name=data[i][2],
                     user_time=data[i][3],
                     user_days=data[i][4].split(","),
                     shirota=data[i][5],
                     dolgota=data[i][6],
                     znak=data[i][7],
                     bnews=bool(data[i][8]),
                     bhoro=bool(data[i][9]),
                     bweat=bool(data[i][10])
                     ))
    DATA[-1].planing()

@bot.message_handler(commands=['weather'])
def mes_weather(message):
    for user in DATA:
        if message.chat.id == user.user_id:
            weather(user)
            break


@bot.message_handler(commands=['horoscope'])
def mes_horo(message):
    for user in DATA:
        if message.chat.id == user.user_id:
            horoscope(user)
            break


@bot.message_handler(commands=['news'])
def mes_news(message):
    for user in DATA:
        if message.chat.id == user.user_id:
            news(user)
            break


@bot.message_handler(commands=['reg'])
def reg_first(message):
    # Создаем нового пользователя с уникальным user_id
    new_user = User(user_id=message.chat.id)
    search_id = message.chat.id
    flag = 0

    # Проверка, зарегистрирован ли пользователь
    for existing_user in DATA:
        if int(existing_user.user_id) == int(search_id):
            flag = 1
            bot.send_message(message.chat.id, 'Вы уже зарегистрированы')
            break

    if flag == 0:
        # Передача объекта new_user через все функции регистрации
        mesg = bot.send_message(message.chat.id, 'Укажите ваше имя')
        bot.register_next_step_handler(mesg, reg_name, new_user)


def reg_name(message, user):
    user.name = message.text
    bot.send_message(message.chat.id, 'Укажите город, в котором вы живете')
    bot.register_next_step_handler(message, reg_city, user)


def reg_city(message, user):
    city = message.text.capitalize()
    with open('goroda.txt') as f:
        cities = f.read().splitlines()

    flag = 0
    for city_info in cities:
        if city == city_info.split('\t')[0]:
            user.shirota = city_info.split('\t')[1]
            user.dolgota = city_info.split('\t')[2]
            flag = 1
            break

    if flag == 0:
        bot.send_message(message.chat.id, 'Город указан неверно, либо ваш город слишком маленький, попробуйте еще раз')
        bot.register_next_step_handler(message, reg_city, user)
    else:
        bot.send_message(message.chat.id, 'Укажите ваш знак зодиака')
        bot.register_next_step_handler(message, reg_zodiak, user)


def reg_zodiak(message, user):
    zodiak = message.text.capitalize()
    zodiaks = ["Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева", "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей",
               "Рыбы"]

    if zodiak not in zodiaks:
        bot.send_message(message.chat.id, 'Знак зодиака указан неверно, повторите попытку')
        bot.register_next_step_handler(message, reg_zodiak, user)
    else:
        user.znak = zodiak
        bot.send_message(message.chat.id,
                         'Укажите время, в которое вам хотелось бы получать сообщения (строго в формате ЧЧ:ММ)')
        bot.register_next_step_handler(message, reg_time, user)


def reg_time(message, user):
    user_time = message.text
    if is_valid_time(user_time):
        user.user_time = user_time
        bot.send_message(message.chat.id,
                         'Укажите дни недели, в которые вам хотелось бы получать сообщения, через запятую (например: Понедельник, Среда, Пятница)')
        bot.register_next_step_handler(message, reg_days, user)
    else:
        bot.send_message(message.chat.id, 'Время указано неверно. Повторите попытку (строго в формате ЧЧ:ММ)')
        bot.register_next_step_handler(message, reg_time, user)


def reg_days(message, user):
    days = message.text.lower().replace(" ", "").split(',')
    valid_days = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
    user_days = [day for day in days if day in valid_days]

    if user_days:
        user.user_days = user_days
        bot.send_message(message.chat.id, 'Укажите, хотите ли вы получать новости (да/нет)')
        bot.register_next_step_handler(message, reg_news, user)
    else:
        bot.send_message(message.chat.id, 'Некорректно указаны дни недели. Попробуйте еще раз.')
        bot.register_next_step_handler(message, reg_days, user)


def reg_news(message, user):
    if message.text.capitalize() == 'Да':
        user.bnews = True
    elif message.text.capitalize() == 'Нет':
        user.bnews = False
    else:
        bot.send_message(message.chat.id, 'Неправильный ввод, введите да или нет')
        bot.register_next_step_handler(message, reg_news, user)
        return

    bot.send_message(message.chat.id, 'Укажите, хотите ли вы получать гороскоп (да/нет)')
    bot.register_next_step_handler(message, reg_horoscope, user)


def reg_horoscope(message, user):
    if message.text.capitalize() == 'Да':
        user.bhoro = True
    elif message.text.capitalize() == 'Нет':
        user.bhoro = False
    else:
        bot.send_message(message.chat.id, 'Неправильный ввод, введите да или нет')
        bot.register_next_step_handler(message, reg_horoscope, user)
        return

    bot.send_message(message.chat.id, 'Укажите, хотите ли вы получать информацию о погоде (да/нет)')
    bot.register_next_step_handler(message, reg_weather, user)


def reg_weather(message, user):
    if message.text.capitalize() == 'Да':
        user.bweat = True
    elif message.text.capitalize() == 'Нет':
        user.bweat = False
    else:
        bot.send_message(message.chat.id, 'Неправильный ввод, введите да или нет')
        bot.register_next_step_handler(message, reg_weather, user)
        return

    bot.send_message(message.chat.id, 'Спасибо, вы зарегистрированы!')
    final_reg(user)


def final_reg(user):
    create_users = 'INSERT INTO users (user_id, name, user_time, user_days, shirota, dolgota, znak, news, horoscope, weather) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'

    data = [
        (str(user.user_id), user.name, user.user_time, ",".join(user.user_days), user.shirota, user.dolgota, user.znak,
         int(user.bnews), int(user.bhoro), int(user.bweat))
    ]

    with connection:
        connection.executemany(create_users, data)

    # Добавляем пользователя в список
    DATA.append(user)

    # Настраиваем планирование задач для пользователя
    user.planing()

    print(DATA)


@bot.message_handler(commands=['edit'])
def edit_user(message):
    search_id = message.chat.id
    current_user = None

    # Поиск пользователя в глобальном списке DATA
    for user in DATA:
        if int(user.user_id) == int(search_id):
            current_user = user
            break

    if current_user is None:
        bot.send_message(message.chat.id, 'Вы не зарегистрированы. Сначала используйте /reg для регистрации.')
    else:
        # Начало процесса редактирования
        bot.send_message(message.chat.id,
                         'Что вы хотите изменить? (имя, город, знак зодиака, время, дни, новости, гороскоп, погода)')
        bot.register_next_step_handler(message, process_edit_choice, current_user)


def process_edit_choice(message, user):
    choice = message.text.lower()

    if choice == 'имя':
        msg = bot.send_message(message.chat.id, 'Введите новое имя:')
        bot.register_next_step_handler(msg, edit_name, user)
    elif choice == 'город':
        msg = bot.send_message(message.chat.id, 'Введите новый город:')
        bot.register_next_step_handler(msg, edit_city, user)
    elif choice == 'знак зодиака':
        msg = bot.send_message(message.chat.id, 'Введите новый знак зодиака:')
        bot.register_next_step_handler(msg, edit_zodiak, user)
    elif choice == 'время':
        msg = bot.send_message(message.chat.id, 'Введите новое время (формат ЧЧ:ММ):')
        bot.register_next_step_handler(msg, edit_time, user)
    elif choice == 'дни':
        msg = bot.send_message(message.chat.id,
                               'Введите новые дни недели через запятую (например: Понедельник, Среда, Пятница):')
        bot.register_next_step_handler(msg, edit_days, user)
    elif choice == 'новости':
        msg = bot.send_message(message.chat.id, 'Хотите ли вы получать новости? (да/нет):')
        bot.register_next_step_handler(msg, edit_news, user)
    elif choice == 'гороскоп':
        msg = bot.send_message(message.chat.id, 'Хотите ли вы получать гороскоп? (да/нет):')
        bot.register_next_step_handler(msg, edit_horoscope, user)
    elif choice == 'погода':
        msg = bot.send_message(message.chat.id, 'Хотите ли вы получать погоду? (да/нет):')
        bot.register_next_step_handler(msg, edit_weather, user)
    else:
        bot.send_message(message.chat.id, 'Некорректный выбор. Попробуйте еще раз.')
        bot.register_next_step_handler(message, process_edit_choice, user)


def update_user_in_db(user, column, value):
    update_query = f"UPDATE users SET {column} = ? WHERE user_id = ?"
    with connection:
        connection.execute(update_query, (value, user.user_id))


def edit_name(message, user):
    user.name = message.text
    user.remove_plan()
    user.planing()
    update_user_in_db(user, 'name', user.name)
    bot.send_message(message.chat.id, f'Имя обновлено на {user.name}.')


def edit_city(message, user):
    city = message.text.capitalize()
    with open('goroda.txt') as f:
        cities = f.read().splitlines()

    flag = 0
    for city_info in cities:
        if city == city_info.split('\t')[0]:
            user.shirota = city_info.split('\t')[1]
            user.dolgota = city_info.split('\t')[2]
            flag = 1
            break

    if flag == 0:
        bot.send_message(message.chat.id, 'Город указан неверно или слишком мал. Попробуйте еще раз.')
        bot.register_next_step_handler(message, edit_city, user)
    else:
        update_user_in_db(user, 'shirota', user.shirota)
        update_user_in_db(user, 'dolgota', user.dolgota)
        user.remove_plan()
        user.planing()
        bot.send_message(message.chat.id, f'Город обновлен на {city}.')


def edit_zodiak(message, user):
    zodiak = message.text.capitalize()
    zodiaks = ["Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева", "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей",
               "Рыбы"]

    if zodiak not in zodiaks:
        bot.send_message(message.chat.id, 'Знак зодиака указан неверно. Попробуйте еще раз.')
        bot.register_next_step_handler(message, edit_zodiak, user)
    else:
        user.znak = zodiak
        update_user_in_db(user, 'znak', user.znak)
        user.remove_plan()
        user.planing()
        bot.send_message(message.chat.id, f'Знак зодиака обновлен на {user.znak}.')


def edit_time(message, user):
    user_time = message.text
    if is_valid_time(user_time):
        user.user_time = user_time
        update_user_in_db(user, 'user_time', user.user_time)
        bot.send_message(message.chat.id, f'Время уведомлений обновлено на {user.user_time}.')
        user.remove_plan()
        user.planing()
    else:
        bot.send_message(message.chat.id, 'Некорректный формат времени. Повторите попытку (формат ЧЧ:ММ).')
        bot.register_next_step_handler(message, edit_time, user)


def edit_days(message, user):
    days = message.text.lower().replace(" ", "").split(',')
    valid_days = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
    user_days = [day for day in days if day in valid_days]

    if user_days:
        user.user_days = user_days
        update_user_in_db(user, 'user_days', ",".join(user.user_days))
        user.remove_plan()
        user.planing()
        bot.send_message(message.chat.id, f'Дни недели обновлены на {", ".join(user.user_days)}.')
    else:
        bot.send_message(message.chat.id, 'Некорректно указаны дни недели. Попробуйте еще раз.')
        bot.register_next_step_handler(message, edit_days, user)


def edit_news(message, user):
    if message.text.capitalize() == 'Да':
        user.bnews = True
    elif message.text.capitalize() == 'Нет':
        user.bnews = False
    else:
        bot.send_message(message.chat.id, 'Неправильный ввод. Введите да или нет.')
        bot.register_next_step_handler(message, edit_news, user)
        return

    update_user_in_db(user, 'news', int(user.bnews))
    user.remove_plan()
    user.planing()
    bot.send_message(message.chat.id, 'Настройка получения новостей обновлена.')


def edit_horoscope(message, user):
    if message.text.capitalize() == 'Да':
        user.bhoro = True
    elif message.text.capitalize() == 'Нет':
        user.bhoro = False
    else:
        bot.send_message(message.chat.id, 'Неправильный ввод. Введите да или нет.')
        bot.register_next_step_handler(message, edit_horoscope, user)
        return

    update_user_in_db(user, 'horoscope', int(user.bhoro))
    user.remove_plan()
    user.planing()
    bot.send_message(message.chat.id, 'Настройка получения гороскопа обновлена.')


def edit_weather(message, user):
    if message.text.capitalize() == 'Да':
        user.bweat = True
    elif message.text.capitalize() == 'Нет':
        user.bweat = False
    else:
        bot.send_message(message.chat.id, 'Неправильный ввод. Введите да или нет.')
        bot.register_next_step_handler(message, edit_weather, user)
        return

    update_user_in_db(user, 'weather', int(user.bweat))
    user.remove_plan()
    user.planing()
    bot.send_message(message.chat.id, 'Настройка получения погоды обновлена.')


def thread_func():
    while True:
        schedule.run_pending()
        time.sleep(1)


# Запуск функции планирования в отдельном потоке
t = threading.Thread(target=thread_func)
t.start()

bot.polling(none_stop=True)
