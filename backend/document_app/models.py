# Corregido: Todos los modelos convertidos a mongoengine
from decimal import Decimal
from mongoengine import (
    Document, StringField, EmailField, DateTimeField, FloatField, 
    BooleanField, ReferenceField, IntField, DecimalField, ListField
)
from datetime import datetime

# --- Cliente ---
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



# --- Configuración de empresa ---
class CompanySettings(Document):
    company_name = StringField(required=True, max_length=200)
    company_address = StringField()
    company_phone = StringField(max_length=20)
    company_email = EmailField()
    company_ruc = StringField(max_length=20)
    company_logo = StringField()
    proforma_prefix = StringField(default="PRF", max_length=10)
    next_proforma_number = IntField(default=1)
    tax_rate = DecimalField(precision=4, default=0.12)

    def __str__(self):
        return self.company_name

    def get_next_proforma_number(self):
        current_number = self.next_proforma_number
        self.next_proforma_number += 1
        self.save()
        return f"{self.proforma_prefix}-{current_number:04d}"

# --- Proforma ---
class Proforma(Document):
    STATUS_CHOICES = ('draft', 'sent', 'approved', 'rejected')

    client = ReferenceField(Client, required=True)
    proforma_number = StringField(required=True, unique=True)
    date = DateTimeField(default=datetime.utcnow)
    status = StringField(choices=STATUS_CHOICES, default='draft')
    subtotal = DecimalField(precision=2, default=0)
    tax_amount = DecimalField(precision=2, default=0)
    total = DecimalField(precision=2, default=0)
    created_by = StringField()
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    def __str__(self):
        return f"Proforma {self.proforma_number} - {self.client.name}"

# --- Análisis ---
class Analysis(Document):
    proforma = ReferenceField(Proforma, required=True)
    parameter = StringField(required=True)
    unit = StringField(max_length=50)
    method = StringField(required=True)
    technique = StringField(required=True)
    unit_price = DecimalField(precision=2)
    quantity = IntField(default=1)
    subtotal = DecimalField(precision=2)
    order = IntField(default=0)
    created_at = DateTimeField(default=datetime.utcnow)

    def save(self, *args, **kwargs):
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)
        self.proforma.subtotal = sum([a.subtotal for a in Analysis.objects(proforma=self.proforma)])
        self.proforma.tax_amount = self.proforma.subtotal * Decimal("0.12")
        self.proforma.total = self.proforma.subtotal + self.proforma.tax_amount
        self.proforma.save()

    def __str__(self):
        return f"{self.parameter.name} - {self.proforma.proforma_number}"

# --- Tipo de Muestra ---
class TipoMuestra(Document):
    tipo = StringField(required=True)
    parametro = StringField(required=True)
    unidad = StringField(required=True)
    metodo = StringField(required=True)
    tecnica = StringField(required=True)
    precio = DecimalField(required=True)

    def __str__(self):
        return self.parametro
