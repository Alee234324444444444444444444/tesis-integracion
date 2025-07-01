from mongoengine import Document, ReferenceField, StringField, DateTimeField
from datetime import datetime
from .proforma import Proforma

class Informe(Document):
    codigo = StringField(unique=True)  # ← nuevo campo
    proforma = ReferenceField(Proforma, required=True, unique=True)
    created_by = StringField()
    fecha_emision = DateTimeField(default=datetime.utcnow)
    tomado_por = StringField()
    procedimiento = StringField()
    analizado_por = StringField()
    pdf_url = StringField()

    def __str__(self):
        return f"Informe {self.codigo or '[sin código]'} de {self.proforma.proforma_number}"

    def save(self, *args, **kwargs):
        if not self.codigo:
            count = Informe.objects.count() + 1
            self.codigo = f"INF-{count:04d}"
        return super().save(*args, **kwargs)
