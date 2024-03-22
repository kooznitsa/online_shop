# Online Shop

Features:

- Asynchronous Django (ASGI)
- Celery tasks
- RabbitMQ broker
- Stripe payment system
- Monitoring with Flower

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
python manage.py makemigrations --settings=backend.settings.local
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
python -m celery -A backend worker --pool=solo -l info
```

## Monitoring

Flower: http://localhost:5555/

## Stripe payment system

Test data:

- Card number: 4242 4242 4242 4242
- Expiration date: 12/29
- CVC: 123
- Country: United States 10001

Links:

- [Stripe test data](https://docs.stripe.com/testing)
- [Stripe dashboard](https://dashboard.stripe.com/test/payments)
- [Stripe webhooks](https://dashboard.stripe.com/test/webhooks)

Set webhook locally:

- Download stripe_1.19.2_windows_x86_64.zip from [GitHub](https://github.com/stripe/stripe-cli/releases/tag/v1.19.2)
- Add stripe.exe to your venv/scripts
- ```stripe login --api-key sk_test_...```
- ```stripe listen --forward-to localhost:8000/payment/webhook/```

Set webhook with Docker (not tested):

- Install Stripe CLI: ```docker run --rm -it stripe/stripe-cli:latest```
- ```docker run -it stripe/stripe-cli login```
- ```docker run -it stripe/stripe-cli listen --api-key ${STRIPE_SECRET_KEY} --forward-to backend:8000/payment/webhook/```
