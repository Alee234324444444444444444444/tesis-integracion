from mongoengine import Document, ReferenceField, StringField
from .informe import Informe

class Resultado(Document):
    informe = ReferenceField(Informe, required=True)
    parameter = StringField()
    unit = StringField()
    method = StringField()
    resultados = StringField()
    limite = StringField()
    incertidumbre = StringField()
