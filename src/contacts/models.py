import uuid

from django.db import models


class Contact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=11, blank=True, default='')
    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'Contact: {self.name}'
