from mongoengine import Document, StringField, DateTimeField, DecimalField, ReferenceField
from datetime import datetime
from decimal import Decimal
from .client import Client
from .company_settings import CompanySettings
from .analysis import Analysis

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
    pdf_url = StringField()
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    def __str__(self):
        return f"Proforma {self.proforma_number} - {self.client.name}"

    def recalculate_totals(self):
        analyses = Analysis.objects(proforma=self)
        self.subtotal = sum([a.subtotal for a in analyses]) if analyses else Decimal("0.00")
        company = CompanySettings.objects.first()
        rate = company.tax_rate if company else Decimal("0.12")
        self.tax_amount = self.subtotal * rate
        self.total = self.subtotal + self.tax_amount
        self.save()
