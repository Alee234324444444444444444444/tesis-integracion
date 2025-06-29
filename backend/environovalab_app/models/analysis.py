from mongoengine import Document, ReferenceField, StringField, DecimalField, IntField, DateTimeField
from datetime import datetime
from decimal import Decimal

class Analysis(Document):
    # Usamos el nombre como string para evitar la importación circular
    proforma = ReferenceField('Proforma', required=True)
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
        if self.proforma:
            self.proforma.recalculate_totals()

    def __str__(self):
        return f"{self.parameter} - {self.proforma.proforma_number if self.proforma else ''}"
