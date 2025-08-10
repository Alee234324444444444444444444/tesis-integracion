from rest_framework import serializers
from environovalab_app.models.client import Client

class ClientSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)

    name = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'El nombre del cliente es obligatorio.',
            'blank': 'El nombre del cliente no puede estar vacío.'
        }
    )

    ruc = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'El RUC es obligatorio.',
            'blank': 'El RUC no puede estar vacío.'
        }
    )

    phone = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)

    email = serializers.EmailField(
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'El correo es obligatorio.',
            'invalid': 'El correo ingresado no es válido.',
            'blank': 'El correo no puede estar vacío.'
        }
    )

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
