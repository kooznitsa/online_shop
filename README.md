# Online Shop

## Tech stack

- Asynchronous Django (ASGI)
- Celery tasks
- RabbitMQ broker
- Stripe payment system
- Redis Storage
- PostgreSQL database
- Monitoring with Flower
- Docker containers

## Online shop features

- Admin panel
- CSV export
- PDF export
- Notifications via email
- Coupon system
- Recommender system

## Database structure

[![draw-SQL-image-export-2024-03-20.png](https://i.postimg.cc/k4yYwmkW/draw-SQL-image-export-2024-03-20.png)](https://postimg.cc/qhzGM9B7)

## Launching project

### General

1. Create database **shop_db** with Postgres 16 and new server in PGAdmin:

- Host name/address: localhost
- Port: 5433
- Maintenance database: postgres
- Username: postgres

2. Add **.env.prod** (with Docker Compose) or **.env.local** (without Docker Compose), and **.env.stripe** to the project's root.

Generate new Django secret key:
```python
from django.core.management.utils import get_random_secret_key

print(get_random_secret_key())
```

### With Docker Compose

1. Create network: ```docker network create shop-net```

2. Build Docker containers: ```docker compose up -d --build```

3. To authenticate with Stripe, go to: https://dashboard.stripe.com/stripecli/confirm_auth?t=... (see Docker Desktop logs for full URL)

Remove Docker containers: ```docker compose down```

### Without Docker Compose

#### Collect static files

```bash
cd backend
python manage.py collectstatic --noinput --settings=backend.settings.local
```

#### Launch project

```bash
cd backend
python -m uvicorn backend.asgi:application --reload
```

#### Apply migrations

```bash
cd backend
# Make new migrations
python manage.py makemigrations --settings=backend.settings.local
# Apply migrations
python manage.py migrate --settings=backend.settings.local
```

#### Lanch RabbitMQ

1. Start Docker Desktop.

2. Run commands in terminal:

```bash
docker pull rabbitmq
docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:management
```

3. RabbitMQ interface is available at http://127.0.0.1:15672

#### Run a Celery worker

```bash
cd backend
python -m celery -A backend worker --pool=solo -l info
```

#### Launch Redis

```bash
# Once:
sudo add-apt-repository universe
sudo apt install redis
sudo service redis-service restart

# Always:
sudo service redis-server start
sudo service redis-server status
# Status: "Ready to accept connections"
redis-cli
```

#### Stripe payment system

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

#### Transfer database

```bash
# Dump data
cd backend
python -Xutf8 manage.py dumpdata --natural-foreign --exclude=auth.permission --exclude=contenttypes --indent=4 --output=db_data.json --settings=backend.settings.local

# Put db_data.json into backend/fixtures/

# Load data
cd backend
python manage.py loaddata db_data.json --settings=backend.settings.local
```

## Monitoring

Flower: http://localhost:5555/
