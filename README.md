Приветствую вас на странице моего бота Доброе_утро

Это телеграм бот, который работает на Python, с помощью него вы можете получать приветственное сообщение каждое утро (или по определенным дням), в определенное время.
В сообщении будут информация о погоде, где живет пользователь, гороскоп, и экономические новости.



Инструкция по установке:

1. Скачайте Python с официального сайта https://www.python.org/downloads/ 
2. Дальше создадим виртуальное окружение, откройте командную строку (Win+R, далее пишем cmd и жмем Enter) и перейдите в каталог, в котором будет создана виртуальная среда. (шпаргалка по командам в консоли: https://serverspace.ru/support/help/shpargalka-po-cmd-komandam-v-windows/?utm_source=google.com&utm_medium=organic&utm_campaign=google.com&utm_referrer=google.com)
3. Выполните команду: `python -m venv virt_name` (где virt_name – имя вашей виртуальной среды.), дождитесь завершения процесса создания виртуальной среды. Это может занять некоторое время.
4. Скачайте Zip архив проекта и распакуйте его в папку virt_name (для установки сначала нажимаем на кнопку в красном квадрате, после в синем)

![image](https://github.com/user-attachments/assets/cc7f4a50-70c0-48e3-a8d9-4c727a4b8199)

6. Вернитесь в консоль, перейдите в папку virt_name и пропишите команду `.\Scripts\activate`, после выполнения перед строкой ввода должна появиться надпись (virt_name), если она появилась - все работает. ВАЖНО! ПРИ КАЖДОМ ЗАПУСКЕ ПРОГРАММЫ, ЕСЛИ НАДПИСЬ НЕ ГОРИТ, НУЖНО ПОВТОРИТЬ 6 ШАГ ЕЩЕ РАЗ ДЛЯ ЕЕ ПОЯВЛЕНИЯ!!! Также, после выключения бота, используйте команду деактивации виртуального окружения: `Scripts\deactivate`
7. Зайдите в телеграм и в поиске найдите @BotFather, после чего напишите ему в личные сообщения `/newbot`, придумайте уникальное название для бота, после чего вы получите ссылку на вашего нового бота и токен (который никому нельзя показывать), скопируйте токен (светится оранжевым)
8. Снова вернитесь в консоль и напишите команду `set TOKEN=сюда просто вставьте токен который вы скопировали в тг`
9. Так же по ссылке https://yandex.ru/pogoda/b2b/console/api-page вам нужно зарегистрироваться и получить токен API яндекс погоды (скопировать его можно на кнопку в красном прямоугольнике на картинке)

![image](https://github.com/user-attachments/assets/982c45c8-cb4b-4ebf-b781-63bd920b47dc)

10. После вам нужно вставить свой токен вместо обведенного в синий прямоугольник значения в файле send_funcs (23 строка)

![image](https://github.com/user-attachments/assets/a54ff4c9-140a-4f42-b68c-59ab5c443121)

11. Далее скачаем дополнительные библиотеки выполнив команду `pip install -r requirements.txt`
12. Запустим нашего бота выполнив команду: `python main.py`


