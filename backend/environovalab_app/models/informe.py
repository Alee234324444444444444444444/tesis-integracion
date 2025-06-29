from mongoengine import Document, ReferenceField, StringField, DateTimeField
from datetime import datetime
from .proforma import Proforma

class Informe(Document):
    proforma = ReferenceField(Proforma, required=True, unique=True)
    fecha_emision = DateTimeField(default=datetime.utcnow)
    tomado_por = StringField()
    procedimiento = StringField()
    analizado_por = StringField()
    pdf_url = StringField()

    def __str__(self):
        return f"Informe de {self.proforma.proforma_number}"
