from rest_framework import serializers
from .models import (
    Client, 
    Proforma, Analysis, CompanySettings, TipoMuestra
)
from decimal import Decimal

class ClientSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField()
    ruc = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    contact_person = serializers.CharField(required=False, allow_blank=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        return Client(**validated_data).save()

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class ParameterSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField()
    category = serializers.CharField()
    default_unit = serializers.CharField()
    default_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    is_active = serializers.BooleanField()

    def create(self, validated_data):
        return Parameter(**validated_data).save()

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class MethodSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)
    category = serializers.CharField()
    is_active = serializers.BooleanField()

    def create(self, validated_data):
        return Method(**validated_data).save()

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class TechniqueSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)
    category = serializers.CharField()
    is_active = serializers.BooleanField()

    def create(self, validated_data):
        return Technique(**validated_data).save()

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class AnalysisSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    parameter = serializers.CharField()
    parameter_name = serializers.CharField(read_only=True)
    parameter_category = serializers.CharField(read_only=True)
    unit = serializers.CharField()
    method = serializers.CharField()
    method_name = serializers.CharField(read_only=True)
    technique = serializers.CharField()
    technique_name = serializers.CharField(read_only=True)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity = serializers.IntegerField()
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    order = serializers.IntegerField(required=False)



class ProformaSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    client = serializers.CharField()
    client_name = serializers.CharField(read_only=True)
    client_ruc = serializers.CharField(read_only=True)
    proforma_number = serializers.CharField(read_only=True)
    date = serializers.DateField()
    status = serializers.CharField()
    status_display = serializers.CharField(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    tax_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    created_by = serializers.CharField()
    analysis_set = serializers.SerializerMethodField()

    def get_analysis_set(self, obj):
        analyses = Analysis.objects(proforma=obj)
        return AnalysisSerializer(analyses, many=True).data

    def create(self, validated_data):
        analysis_data = validated_data.pop('analysis_data', [])

        # Configuración de la empresa
        company_settings = CompanySettings.objects.first()
        if not company_settings:
            company_settings = CompanySettings.objects.create(
                company_name="ENVIRONOVALAB",
                company_address="Dirección por defecto",
                company_phone="000-000-0000",
                company_email="info@environovalab.com",
                company_ruc="0000000000000"
            )

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
    date = serializers.DateField()
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

class CompanySettingsSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    company_name = serializers.CharField()
    company_address = serializers.CharField()
    company_phone = serializers.CharField()
    company_email = serializers.EmailField()
    company_ruc = serializers.CharField()

    def create(self, validated_data):
        return CompanySettings(**validated_data).save()

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class ParameterSearchSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField()
    default_unit = serializers.CharField()
    default_price = serializers.DecimalField(max_digits=10, decimal_places=2)

class MethodSearchSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField()

class TechniqueSearchSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField()

class ClientSearchSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField()
    ruc = serializers.CharField()

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

#Serializer para informes
class AnalysisReportSerializer(serializers.Serializer):
    parameter = serializers.CharField()
    unit = serializers.CharField()
    method = serializers.CharField()
    technique = serializers.CharField()
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity = serializers.IntegerField()
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)

class ProformaReportSerializer(serializers.Serializer):
    proforma_number = serializers.CharField()
    date = serializers.DateTimeField()
    client_name = serializers.CharField()
    created_by = serializers.CharField()
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    total = serializers.DecimalField(max_digits=10, decimal_places=2)
    analysis_data = AnalysisReportSerializer(many=True)