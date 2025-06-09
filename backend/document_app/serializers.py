from rest_framework import serializers
from .models import Client, Parameter, Method, Technique, Proforma, Analysis, CompanySettings


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class ParameterSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = Parameter
        fields = ['id', 'name', 'category', 'category_display', 'default_unit', 'default_price', 'is_active']
        

class MethodSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = Method
        fields = ['id', 'name', 'description', 'category', 'category_display', 'is_active']


class TechniqueSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = Technique
        fields = ['id', 'name', 'description', 'category', 'category_display', 'is_active']


class AnalysisSerializer(serializers.ModelSerializer):
    parameter_name = serializers.CharField(source='parameter.name', read_only=True)
    parameter_category = serializers.CharField(source='parameter.category', read_only=True)
    method_name = serializers.CharField(source='method.name', read_only=True)
    technique_name = serializers.CharField(source='technique.name', read_only=True)
    
    class Meta:
        model = Analysis
        fields = [
            'id', 'parameter', 'parameter_name', 'parameter_category',
            'unit', 'method', 'method_name', 'technique', 'technique_name',
            'unit_price', 'quantity', 'subtotal', 'order'
        ]
        read_only_fields = ('subtotal',)

    def validate(self, data):
        """Valida que el método y técnica sean compatibles con el parámetro"""
        parameter = data.get('parameter')
        method = data.get('method')
        technique = data.get('technique')
        
        if parameter and method and parameter.category != method.category:
            raise serializers.ValidationError(
                "El método seleccionado no es compatible con la categoría del parámetro"
            )
        
        if parameter and technique and parameter.category != technique.category:
            raise serializers.ValidationError(
                "La técnica seleccionada no es compatible con la categoría del parámetro"
            )
        
        return data


class ProformaSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)
    client_ruc = serializers.CharField(source='client.ruc', read_only=True)
    analysis_set = AnalysisSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Proforma
        fields = [
            'id', 'client', 'client_name', 'client_ruc', 'proforma_number',
            'date', 'status', 'status_display', 'subtotal', 'tax_amount', 'total',
            'created_at', 'updated_at', 'created_by', 'analysis_set'
        ]
        read_only_fields = ('id', 'proforma_number', 'subtotal', 'tax_amount', 'total', 'created_at', 'updated_at')

    def create(self, validated_data):
        """Crea una proforma con número automático"""
        # Obtener configuración de empresa para generar número
        try:
            company_settings = CompanySettings.objects.first()
        except CompanySettings.DoesNotExist:
            # Crear configuración por defecto
            company_settings = CompanySettings.objects.create(
                company_name="ENVIRONOVALAB",
                company_address="Dirección por defecto",
                company_phone="000-000-0000",
                company_email="info@environovalab.com",
                company_ruc="0000000000000"
            )
        
        validated_data['proforma_number'] = company_settings.get_next_proforma_number()
        return super().create(validated_data)


class ProformaCreateSerializer(serializers.ModelSerializer):
    """Serializador específico para crear proformas con análisis"""
    analysis_data = AnalysisSerializer(many=True, write_only=True)
    
    class Meta:
        model = Proforma
        fields = [
            'client', 'date', 'status', 'created_by', 'analysis_data'
        ]

    def create(self, validated_data):
        analysis_data = validated_data.pop('analysis_data', [])
        
        # Crear la proforma
        proforma = ProformaSerializer().create(validated_data)
        
        # Crear los análisis
        for i, analysis in enumerate(analysis_data):
            analysis['proforma'] = proforma
            analysis['order'] = i
            Analysis.objects.create(**analysis)
        
        return proforma


class CompanySettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanySettings
        fields = '__all__'


# Serializadores para autocompletado/búsqueda
class ParameterSearchSerializer(serializers.ModelSerializer):
    """Serializador ligero para búsquedas de parámetros"""
    class Meta:
        model = Parameter
        fields = ['id', 'name', 'default_unit', 'default_price']


class MethodSearchSerializer(serializers.ModelSerializer):
    """Serializador ligero para búsquedas de métodos"""
    class Meta:
        model = Method
        fields = ['id', 'name']


class TechniqueSearchSerializer(serializers.ModelSerializer):
    """Serializador ligero para búsquedas de técnicas"""
    class Meta:
        model = Technique
        fields = ['id', 'name']


class ClientSearchSerializer(serializers.ModelSerializer):
    """Serializador ligero para búsquedas de clientes"""
    class Meta:
        model = Client
        fields = ['id', 'name', 'ruc']