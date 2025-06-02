from django.db import models

# Create your models here.

from mongoengine import Document, StringField, ReferenceField, FloatField, DateTimeField, BooleanField, EmailField
from datetime import datetime

class User(Document):
    username = StringField(required=True, unique=True)
    password = StringField(required=True)
    email = EmailField(required=True, unique=True)
    is_admin = BooleanField(default=False)

class Cliente(Document):
    nombre_cliente = StringField(required=True)
    empresa_asociada = StringField()

class Analisis(Document):
    tipo_muestra = StringField(required=True)
    nombre_muestra = StringField(required=True)
    precio_analisis = FloatField(required=True)

class Proforma(Document):
    cliente = ReferenceField(Cliente, required=True)
    analisis = ReferenceField(Analisis, required=True)
    precio_unitario = FloatField(required=True)
    precio_total = FloatField(required=True)
    fecha = DateTimeField(default=datetime.utcnow)
    usuario = ReferenceField(User, required=True)

class Informe(Document):
    proforma = ReferenceField(Proforma, required=True)
    analisis = ReferenceField(Analisis, required=True)
    muestra = StringField(required=True)
    fecha = DateTimeField(default=datetime.utcnow)

class Historial(Document):
    id_documento = StringField(required=True)
    nombre_documento = StringField(required=True)
    fecha_modificacion = DateTimeField(default=datetime.utcnow)
    usuario = ReferenceField(User, required=True)
