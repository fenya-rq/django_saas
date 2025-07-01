"""https://docs.djangoproject.com/en/5.2/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project"""

from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass
