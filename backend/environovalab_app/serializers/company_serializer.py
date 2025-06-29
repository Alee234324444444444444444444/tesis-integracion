from rest_framework import serializers
from environovalab_app.models.company_settings import CompanySettings

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
