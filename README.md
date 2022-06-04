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

Клонировать репозиторий:

```
git clone https://github.com/Tacostrophe/hw05_final.git
```
Все нижеперечисленные действия выполнять из hw05_final/

В репозитории создать и активировать виртуальное окружение:
```
python3 -m venv /path/to/new/virtual/environment
```
```
source /path/to/new/virtual/environment/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```
Выполнить миграции:
```
python yatube/manage.py migrate
```
Запуск проекта:
```
python yatube/manage.py runserver
```

<sub>Всегда рад замечаниям и советам</sub>
