from django.db import models

# Create your models here.

from mongoengine import Document, StringField, BooleanField, EmailField


class User(Document):
    username = StringField(required=True, unique=True)
    password = StringField(required=True)
    email = EmailField(required=True, unique=True)
    is_admin = BooleanField(default=False)
    is_active = BooleanField(default=True)






