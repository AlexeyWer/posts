### REST API для приложения posts:

Документация доступна локально: localhost/redoc/

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

``` bash
git clone git@github.com:AlexeyWer/posts.git
```

``` bash
cd posts
```

Cоздать и активировать виртуальное окружение:

``` bash
python3 -m venv venv
```

``` bash
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

``` bash
python3 -m pip install --upgrade pip
```

``` bash
pip install -r requirements.txt
```

Выполнить миграции:
``` bash
cd posts_api/
```

``` bash
python3 manage.py migrate
```

Запустить проект:

``` bash
python3 manage.py runserver
```

### Запустить тесты:

``` bash
python3 manage.py tests
```
