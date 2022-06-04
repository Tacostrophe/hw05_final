# Yatube

### Описание
**Yatube** - это проект сайта для публикации персональныйх блогов, созданный с целью получения навыков работы с Django.

Доступный функционал:
- регистрация пользователей;
- публикация постов;
- редактирование собственных постов;
- комментирование постов;
- подписка на авторов.

### Инструкция по развертыванию
Все нижеперечисленные действия выполнять из hw05_final/

Создание виртуального окружения:
```
python3 -m venv /path/to/new/virtual/environment
```
Активация виртуального окружения:
```
source /path/to/new/virtual/environment/bin/activate
```
Установка необходимых пакетов:
```
pip install -r /path/to/requirements.txt
```
Миграции:
```
python yatube/manage.py makemigrations
python yatube/manage.py migrate
```
Запуск сервера:
```
python yatube/manage.py runserver
```
