# Corregido: Todos los modelos convertidos a mongoengine
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

# --- Parámetro ---
class Parameter(Document):
    CATEGORY_CHOICES = ('water', 'gas', 'noise', 'logistics')

    name = StringField(required=True, max_length=100)
    category = StringField(required=True, choices=CATEGORY_CHOICES)
    default_unit = StringField(max_length=50)
    default_price = DecimalField(precision=2)
    is_active = BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.category}"

# --- Método ---
class Method(Document):
    name = StringField(required=True, max_length=100)
    description = StringField()
    category = StringField(choices=Parameter.CATEGORY_CHOICES)
    is_active = BooleanField(default=True)

    def __str__(self):
        return self.name

# --- Técnica ---
class Technique(Document):
    name = StringField(required=True, max_length=100)
    description = StringField()
    category = StringField(choices=Parameter.CATEGORY_CHOICES)
    is_active = BooleanField(default=True)

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
    parameter = ReferenceField(Parameter, required=True)
    unit = StringField(max_length=50)
    method = ReferenceField(Method, required=True)
    technique = ReferenceField(Technique, required=True)
    unit_price = DecimalField(precision=2)
    quantity = IntField(default=1)
    subtotal = DecimalField(precision=2)
    order = IntField(default=0)
    created_at = DateTimeField(default=datetime.utcnow)

    def save(self, *args, **kwargs):
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)
        self.proforma.subtotal = sum([a.subtotal for a in Analysis.objects(proforma=self.proforma)])
        self.proforma.tax_amount = self.proforma.subtotal * 0.12
        self.proforma.total = self.proforma.subtotal + self.proforma.tax_amount
        self.proforma.save()

    def __str__(self):
        return f"{self.parameter.name} - {self.proforma.proforma_number}"

# --- Tipo de Muestra ---
class TipoMuestra(Document):
    nombre = StringField(required=True, unique=True, max_length=100)
    descripcion = StringField()

    def __str__(self):
        return self.nombre
    

class AnalisisCatalogo(Document):
    TIPOS_CHOICES = ("agua", "ruido", "emisiones", "logistica")

    tipo = StringField(required=True, choices=TIPOS_CHOICES)  # Ej: 'agua'
    parametro = StringField(required=True, max_length=100)
    unidad = StringField(max_length=50)
    metodo = StringField(max_length=100)
    tecnica = StringField(max_length=100)
    precio = DecimalField(precision=2, required=True)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)

    def __str__(self):
        return f"{self.tipo.upper()}: {self.parametro} ({self.metodo})"