from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from mongoengine.queryset.visitor import Q
from rest_framework.exceptions import NotFound
from .utils import generate_proforma_preview
from .models import Client, Proforma, Analysis, CompanySettings, TipoMuestra
from .serializers import (
    ClientSerializer,
    ProformaSerializer, AnalysisSerializer, CompanySettingsSerializer,
    ProformaCreateSerializer, ClientSearchSerializer, TipoMuestraSerializer
)

class ClientViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Client.objects()
        serializer = ClientSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            client = serializer.save()
            return Response(ClientSerializer(client).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        if len(query) < 2:
            return Response([])
        clients = Client.objects(Q(name__icontains=query) | Q(ruc__icontains=query)).limit(10)
        serializer = ClientSearchSerializer(clients, many=True)
        return Response(serializer.data)



class ProformaViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Proforma.objects()
        serializer = ProformaSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = ProformaCreateSerializer(data=request.data)
        if serializer.is_valid():
            proforma = serializer.save()
            return Response(ProformaSerializer(proforma).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def add_analysis(self, request, pk=None):
        proforma = Proforma.objects.get(id=pk)
        serializer = AnalysisSerializer(data=request.data)
        if serializer.is_valid():
            last_order = Analysis.objects(proforma=proforma).count()
            serializer.save(proforma=proforma, order=last_order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def remove_analysis(self, request, pk=None):
        proforma = Proforma.objects.get(id=pk)
        analysis_id = request.data.get('analysis_id')
        if not analysis_id:
            return Response({'error': 'analysis_id requerido'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            analysis = Analysis.objects.get(id=analysis_id, proforma=proforma)
            analysis.delete()
            return Response({'message': 'Análisis eliminado exitosamente'}, status=status.HTTP_200_OK)
        except Analysis.DoesNotExist:
            return Response({'error': 'Análisis no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        try:
            proforma = Proforma.objects.get(id=pk)
            html = generate_proforma_preview(proforma)
            return HttpResponse(html, content_type="text/html")
        except Proforma.DoesNotExist:
            return Response({'error': 'Proforma no encontrada'}, status=404)

class AnalysisViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Analysis.objects()
        serializer = AnalysisSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def reorder(self, request):
        analysis_orders = request.data.get('analysis_orders', [])
        for item in analysis_orders:
            try:
                analysis = Analysis.objects.get(id=item['id'])
                analysis.order = item['order']
                analysis.save()
            except Analysis.DoesNotExist:
                continue
        return Response({'message': 'Orden actualizado exitosamente'})

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

class TipoMuestraViewSet(viewsets.ViewSet):
    
    def list(self, request):
        queryset = TipoMuestra.objects()
        serializer = TipoMuestraSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = TipoMuestraSerializer(data=request.data)
        if serializer.is_valid():
            tipo = serializer.save()
            return Response(TipoMuestraSerializer(tipo).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        try:
            tipo = TipoMuestra.objects.get(id=pk)
            serializer = TipoMuestraSerializer(tipo)
            return Response(serializer.data)
        except TipoMuestra.DoesNotExist:
            raise NotFound('Tipo de muestra no encontrado')

    def update(self, request, pk=None):
        try:
            tipo = TipoMuestra.objects.get(id=pk)
        except TipoMuestra.DoesNotExist:
            raise NotFound('Tipo de muestra no encontrado')

        serializer = TipoMuestraSerializer(tipo, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        try:
            tipo = TipoMuestra.objects.get(id=pk)
            tipo.delete()
            return Response({'msg': 'Eliminado correctamente'}, status=status.HTTP_204_NO_CONTENT)
        except TipoMuestra.DoesNotExist:
            raise NotFound('Tipo de muestra no encontrado')

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        if not query or len(query) < 2:
            return Response([])
        tipos = TipoMuestra.objects(parametro__icontains=query)[:10]
        serializer = TipoMuestraSerializer(tipos, many=True)
        return Response(serializer.data)
    

    #Informes
    @action(detail=True, methods=['get'])
    def informe(self, request, pk=None):
        try:
            proforma = Proforma.objects.get(id=pk)
        except Proforma.DoesNotExist:
            return Response({'error': 'Proforma no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        analysis_data = Analysis.objects(proforma=proforma)

        data = {
            'proforma_number': proforma.proforma_number,
            'date': proforma.date,
            'client_name': proforma.client.name,
            'created_by': proforma.created_by,
            'subtotal': proforma.subtotal,
            'tax_amount': proforma.tax_amount,
            'total': proforma.total,
            'analysis_data': [
                {
                    'parameter': a.parameter,
                    'unit': a.unit,
                    'method': a.method,
                    'technique': a.technique,
                    'unit_price': a.unit_price,
                    'quantity': a.quantity,
                    'subtotal': a.subtotal,
                } for a in analysis_data
            ]
        }

        from .serializers import ProformaReportSerializer
        serializer = ProformaReportSerializer(data)
        return Response(serializer.data)
