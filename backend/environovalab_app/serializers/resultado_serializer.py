from rest_framework import serializers
from environovalab_app.models.resultado import Resultado

class ResultadoSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    parameter = serializers.CharField()
    unit = serializers.CharField()
    method = serializers.CharField()
    resultados = serializers.CharField()
    limite = serializers.CharField()
    incertidumbre = serializers.CharField()

    def create(self, validated_data):
        return Resultado(**validated_data).save()
