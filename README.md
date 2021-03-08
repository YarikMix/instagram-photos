## Скрипт для скачивания фотографий пользователей instagram

[![Github All Releases](https://img.shields.io/github/downloads/YarikMix/instagram-photos/total.svg)]()

Скрипт позволяет скачать все фотографии с instagram аккаунта

Скрипт работает на библиотеке instabot

### Системные требования:

* Python 3 и выше
* Доступ к интернету
* Логин и пароль от instagram аккаунта

### Как использовать:

Скачиваем зависимости:
```bash
pip3 install -r requirements.txt
```

В файл config.yaml вписываем свой логин и пароль от instagram:
```yaml
instagram:
  username: ""  # Ваш логин от инстаграма
  password: ""  # Ваш пароль от инстаграма
```

Запускаем скрипт:
```bash
python instagram-photos/main.py
```

Вводим имя пользователя, чьи фотографии хотим скачать:
```bash
Введите никнейм
> 
```

В папке photos появится папка с фотографиями пользователя