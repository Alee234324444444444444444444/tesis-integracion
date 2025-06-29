from rest_framework import serializers
from environovalab_app.models.analysis import Analysis

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
