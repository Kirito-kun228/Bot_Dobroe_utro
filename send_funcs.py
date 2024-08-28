from main import bot
import requests
from bs4 import BeautifulSoup as BS
import json

def sendin(s_user):
    bot.send_message(s_user.user_id, 'Доброе утро, ' + s_user.name)
    if s_user.bweat:
        weather(s_user)
    if s_user.bhoro:
        horoscope(s_user)
    if s_user.bnews:
        news(s_user)


# функция получения погоды
def weather(user):
    url = f"https://api.weather.yandex.ru/v2/forecast?lat={user.shirota}&lon={user.dolgota}&ru_RU"
    headers = {"X-Yandex-Weather-Key": "433a6c98-9ea6-4200-a892-09c9e40e6fb8"}

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

    text = (
        f"Главные новости за последнее время:\n -------------- \n {mas_news[0][0]} \n Время новости: {mas_news[1][0]}, Источник {mas_news[2][0]}\n"
        f"-------------- \n {mas_news[0][1]} \n Время новости: {mas_news[1][1]}, Источник {mas_news[2][1]}\n"
        f"-------------- \n {mas_news[0][2]} \n Время новости: {mas_news[1][2]}, Источник {mas_news[2][2]}\n")
    bot.send_message(user.user_id, text)

