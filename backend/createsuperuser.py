from dotenv import load_dotenv
import os

from django.contrib.auth.models import User
from django.db import IntegrityError

load_dotenv()

try:
    superuser = User.objects.create_superuser(
        username=os.environ.get('DJANGO_SUPERUSER_USERNAME', default='admin'),
        password=os.environ.get('DJANGO_SUPERUSER_PASSWORD', default='admin'),
    )
    superuser.save()
except IntegrityError:
    print(f"Superuser with username {os.environ.get('DJANGO_SUPERUSER_USERNAME')} already exists.")
except Exception as e:
    print(e)
