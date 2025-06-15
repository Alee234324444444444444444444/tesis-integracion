from rest_framework import serializers
from .models import (
    Client, Parameter, Method, Technique,
    Proforma, Analysis, CompanySettings, TipoMuestra
)

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

    def validate(self, data):
        from .models import Parameter, Method, Technique
        parameter = Parameter.objects(id=data.get('parameter')).first()
        method = Method.objects(id=data.get('method')).first()
        technique = Technique.objects(id=data.get('technique')).first()

        if parameter and method and parameter.category != method.category:
            raise serializers.ValidationError("El método no es compatible con la categoría del parámetro")

        if parameter and technique and parameter.category != technique.category:
            raise serializers.ValidationError("La técnica no es compatible con la categoría del parámetro")

        return data

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
        from .models import Analysis
        analyses = Analysis.objects(proforma=obj)
        return AnalysisSerializer(analyses, many=True).data

    def create(self, validated_data):
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
        return Proforma(**validated_data).save()

class ProformaCreateSerializer(serializers.Serializer):
    client = serializers.CharField()
    date = serializers.DateField()
    status = serializers.CharField()
    created_by = serializers.CharField()
    analysis_data = AnalysisSerializer(many=True)

    def create(self, validated_data):
        analysis_data = validated_data.pop('analysis_data', [])
        proforma = ProformaSerializer().create(validated_data)

        for i, analysis in enumerate(analysis_data):
            analysis['proforma'] = proforma
            analysis['order'] = i
            Analysis(**analysis).save()

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
    nombre = serializers.CharField()
    descripcion = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        return TipoMuestra(**validated_data).save()

    def update(self, instance, validated_data):
        instance.nombre = validated_data.get('nombre', instance.nombre)
        instance.descripcion = validated_data.get('descripcion', instance.descripcion)
        instance.save()
        return instance
