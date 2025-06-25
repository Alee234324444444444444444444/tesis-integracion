from decimal import Decimal
from mongoengine import (
    Document, StringField, EmailField, DateTimeField, FloatField,
    BooleanField, ReferenceField, IntField, DecimalField, ListField
)
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

# ------------------- Configuración de empresa -------------------
class CompanySettings(Document):
    company_name = StringField(required=True, max_length=200)
    company_address = StringField()
    company_phone = StringField(max_length=20)
    company_email = EmailField()
    company_ruc = StringField(max_length=20)
    company_logo = StringField()  # Ruta al logo (ej: 'media/logo.png')
    proforma_prefix = StringField(default="PRF", max_length=10)
    next_proforma_number = IntField(default=1)
    tax_rate = DecimalField(precision=4, default=Decimal("0.12"))

    def __str__(self):
        return self.company_name

    def get_next_proforma_number(self):
        current = self.next_proforma_number
        self.next_proforma_number += 1
        self.save()
        return f"{self.proforma_prefix}-{current:04d}"

# ------------------- Tipo de Muestra -------------------
class TipoMuestra(Document):
    tipo = StringField(required=True)
    parametro = StringField(required=True)
    unidad = StringField(required=True)
    metodo = StringField(required=True)
    tecnica = StringField(required=True)
    precio = DecimalField(required=True, precision=2)

    def __str__(self):
        return f"{self.tipo} - {self.parametro}"

# ------------------- Proforma -------------------
class Proforma(Document):
    STATUS_CHOICES = ('draft', 'sent', 'approved', 'rejected')

    client = ReferenceField(Client, required=True)
    proforma_number = StringField(required=True, unique=True)
    date = DateTimeField(default=datetime.utcnow)
    status = StringField(choices=STATUS_CHOICES, default='draft')
    subtotal = DecimalField(precision=2, default=Decimal("0.00"))
    tax_amount = DecimalField(precision=2, default=Decimal("0.00"))
    total = DecimalField(precision=2, default=Decimal("0.00"))
    created_by = StringField()
    pdf_url = StringField()  # Ruta al PDF generado
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    def __str__(self):
        return f"Proforma {self.proforma_number} - {self.client.name}"

    def recalculate_totals(self):
        analyses = Analysis.objects(proforma=self)
        self.subtotal = sum([a.subtotal for a in analyses]) if analyses else Decimal("0.00")
        # Toma la tasa de la empresa, si existe:
        company = CompanySettings.objects.first()
        rate = company.tax_rate if company else Decimal("0.12")
        self.tax_amount = self.subtotal * rate
        self.total = self.subtotal + self.tax_amount
        self.save()

# ------------------- Análisis (Detalle de Proforma) -------------------
class Analysis(Document):
    proforma = ReferenceField(Proforma, required=True)
    parameter = StringField(required=True)
    unit = StringField(max_length=50)
    method = StringField(required=True)
    technique = StringField(required=True)
    unit_price = DecimalField(precision=2, required=True)
    quantity = IntField(default=1)
    subtotal = DecimalField(precision=2, default=Decimal("0.00"))
    order = IntField(default=0)
    created_at = DateTimeField(default=datetime.utcnow)

    def save(self, *args, **kwargs):
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)
        # Actualiza totales de la proforma automáticamente:
        if self.proforma:
            self.proforma.recalculate_totals()

    def __str__(self):
        return f"{self.parameter} - {self.proforma.proforma_number if self.proforma else ''}"
    

    # models.py
class Informe(Document):
    proforma = ReferenceField(Proforma, required=True, unique=True)
    fecha_emision = DateTimeField(default=datetime.utcnow)
    tomado_por = StringField()
    procedimiento = StringField()
    analizado_por = StringField()
    pdf_url = StringField()

    def __str__(self):
        return f"Informe de {self.proforma.proforma_number}"

class Resultado(Document):
    informe = ReferenceField(Informe, required=True)
    parameter = StringField()
    unit = StringField()
    method = StringField()
    resultados = StringField()
    limite = StringField()
    incertidumbre = StringField()

