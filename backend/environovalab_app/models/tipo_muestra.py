from mongoengine import Document, StringField, DecimalField

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
