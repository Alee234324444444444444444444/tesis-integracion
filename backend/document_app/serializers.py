from rest_framework import serializers
from .models import (
    Client, 
    Proforma, Analysis, CompanySettings, TipoMuestra, Resultado, Informe
)
from decimal import Decimal

# ------------------- CLIENTE -------------------
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

class ClientSearchSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField()
    ruc = serializers.CharField()

# ------------------- ANÁLISIS -------------------
class AnalysisSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    parameter = serializers.CharField()
    unit = serializers.CharField()
    method = serializers.CharField()
    technique = serializers.CharField()
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity = serializers.IntegerField()
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    order = serializers.IntegerField(required=False)

    def create(self, validated_data):
        return Analysis(**validated_data).save()

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

# ------------------- PROFORMA -------------------
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
        # Mapea el estado si quieres mostrarlo bonito
        mapping = {
            "draft": "Borrador",
            "sent": "Enviada",
            "approved": "Aprobada",
            "rejected": "Rechazada"
        }
        return mapping.get(obj.status, obj.status)

    def create(self, validated_data):
        analysis_data = validated_data.pop('analysis_data', [])

        # Configuración de la empresa
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

# ------------------- CONFIGURACIÓN EMPRESA -------------------
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

# ------------------- TIPO DE MUESTRA -------------------
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

# ------------------- BUSQUEDA DE CLIENTES -------------------
class ClientSearchSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField()
    ruc = serializers.CharField()



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

        # 👇 Extraemos y convertimos el ID de proforma a objeto
        proforma_id = validated_data.pop("proforma")
        proforma = Proforma.objects.get(id=proforma_id)

        # 👇 Creamos el informe con los datos restantes y el objeto proforma
        informe = Informe(**validated_data, proforma=proforma)
        informe.save()

        # 👇 Creamos los resultados asociados
        for r in resultados_data:
            Resultado(informe=informe, **r).save()

        return informe
