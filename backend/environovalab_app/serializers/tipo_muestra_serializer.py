from rest_framework import serializers
from environovalab_app.models.tipo_muestra import TipoMuestra

class TipoMuestraSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    tipo = serializers.CharField()
    parametro = serializers.CharField()
    unidad = serializers.CharField()
    metodo = serializers.CharField()
    tecnica = serializers.CharField()
    precio = serializers.DecimalField(max_digits=10, decimal_places=2)

    def create(self, validated_data):
        return TipoMuestra(**validated_data).save()

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
