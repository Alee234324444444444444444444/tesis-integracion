from mongoengine import Document, StringField, EmailField, DateTimeField
from datetime import datetime

# ------------------- Cliente -------------------

class Client(Document):
    name = StringField(required=True, max_length=200)
    ruc = StringField(max_length=20)
    phone = StringField(max_length=15)
    address = StringField()
    email = EmailField()
    contact_person = StringField(max_length=200)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    def __str__(self):
        return self.name
