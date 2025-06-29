from mongoengine import Document, StringField, EmailField, IntField, DecimalField
from decimal import Decimal

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
