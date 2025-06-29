from rest_framework import serializers
from environovalab_app.models.informe import Informe
from environovalab_app.models.proforma import Proforma
from environovalab_app.models.resultado import Resultado
from environovalab_app.serializers.resultado_serializer import ResultadoSerializer

class InformeSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    proforma = serializers.CharField()
    fecha_emision = serializers.DateTimeField()
    tomado_por = serializers.CharField()
    procedimiento = serializers.CharField()
    analizado_por = serializers.CharField()
    pdf_url = serializers.CharField(read_only=True)
    resultados = ResultadoSerializer(many=True, required=False)

    def create(self, validated_data):
        resultados_data = validated_data.pop("resultados", [])
        proforma_id = validated_data.pop("proforma")
        proforma = Proforma.objects.get(id=proforma_id)
        informe = Informe(**validated_data, proforma=proforma)
        informe.save()

        for r in resultados_data:
            Resultado(informe=informe, **r).save()

        return informe
