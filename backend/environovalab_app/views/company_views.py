from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from environovalab_app.models.company_settings import CompanySettings
from environovalab_app.serializers.company_serializer import CompanySettingsSerializer

class CompanySettingsViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = CompanySettings.objects()
        serializer = CompanySettingsSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def current(self, request):
        try:
            settings = CompanySettings.objects.first()
            if not settings:
                settings = CompanySettings(
                    company_name="ENVIRONOVALAB",
                    company_address="Dirección por defecto",
                    company_phone="000-000-0000",
                    company_email="info@environovalab.com",
                    company_ruc="0000000000000"
                )
                settings.save()
            serializer = CompanySettingsSerializer(settings)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': f'Error obteniendo configuración: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
