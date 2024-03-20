# Weasleys' Wizard Wheezes Online Shop

## Database structure

[![draw-SQL-image-export-2024-03-20.png](https://i.postimg.cc/k4yYwmkW/draw-SQL-image-export-2024-03-20.png)](https://postimg.cc/qhzGM9B7)

## Collect static files

```bash
cd backend
python manage.py collectstatic --noinput --settings=backend.settings.local
```

## Launch project

Development mode:

```bash
cd backend
python -m uvicorn backend.asgi:application --reload
```

Production mode: ```poetry run python -m gunicorn backend.asgi:application -k uvicorn.workers.UvicornWorker```

## Migrations

```bash
cd backend
poetry run python manage.py makemigrations --settings=backend.settings.local
python manage.py migrate --settings=backend.settings.local
```

## Lanch RabbitMQ

1. Start Docker Desktop.

2. Run commands in terminal:

```bash
docker pull rabbitmq
docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:management
```

3. RabbitMQ interface is available at http://127.0.0.1:15672

## Run a Celery worker

```bash
cd backend
celery -A backend worker --pool=solo -l info
```

## Monitoring

Flower: http://localhost:5555/
