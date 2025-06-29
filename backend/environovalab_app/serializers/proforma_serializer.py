from rest_framework import serializers
from decimal import Decimal
from environovalab_app.models.proforma import Proforma
from environovalab_app.models.analysis import Analysis
from environovalab_app.models.company_settings import CompanySettings
from environovalab_app.serializers.analysis_serializer import AnalysisSerializer

class ProformaSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    client = serializers.CharField()
    client_name = serializers.SerializerMethodField()
    client_ruc = serializers.SerializerMethodField()
    proforma_number = serializers.CharField(read_only=True)
    date = serializers.DateTimeField()
    status = serializers.CharField()
    status_display = serializers.SerializerMethodField()
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    tax_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    created_by = serializers.CharField()
    pdf_url = serializers.CharField(read_only=True)
    analysis_set = serializers.SerializerMethodField()

    def get_analysis_set(self, obj):
        analyses = Analysis.objects(proforma=obj)
        return AnalysisSerializer(analyses, many=True).data

    def get_client_name(self, obj):
        return obj.client.name if obj.client else ""

    def get_client_ruc(self, obj):
        return obj.client.ruc if obj.client else ""

    def get_status_display(self, obj):
        mapping = {
            "draft": "Borrador",
            "sent": "Enviada",
            "approved": "Aprobada",
            "rejected": "Rechazada"
        }
        return mapping.get(obj.status, obj.status)

    def create(self, validated_data):
        analysis_data = validated_data.pop('analysis_data', [])
        company_settings = CompanySettings.objects.first()
        if not company_settings:
            company_settings = CompanySettings(
                company_name="ENVIRONOVALAB",
                company_address="Dirección por defecto",
                company_phone="000-000-0000",
                company_email="info@environovalab.com",
                company_ruc="0000000000000"
            ).save()
        validated_data['proforma_number'] = company_settings.get_next_proforma_number()
        proforma = Proforma(**validated_data)
        proforma.save()

        for i, analysis in enumerate(analysis_data):
            Analysis(
                proforma=proforma,
                parameter=analysis['parameter'],
                unit=analysis['unit'],
                method=analysis['method'],
                technique=analysis['technique'],
                unit_price=Decimal(str(analysis['unit_price'])),
                quantity=int(analysis['quantity']),
                order=i
            ).save()

        return proforma

class ProformaCreateSerializer(serializers.Serializer):
    client = serializers.CharField()
    date = serializers.DateTimeField()
    status = serializers.CharField()
    created_by = serializers.CharField()
    analysis_data = AnalysisSerializer(many=True)

    def create(self, validated_data):
        analysis_data = validated_data.pop('analysis_data', [])
        proforma = ProformaSerializer().create({
            **validated_data,
            'analysis_data': analysis_data
        })
        return proforma
