from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from mongoengine.queryset.visitor import Q
from .utils import generate_proforma_preview
from .models import Client, Parameter, Method, Technique, Proforma, Analysis, CompanySettings, TipoMuestra
from .serializers import (
    ClientSerializer, ParameterSerializer, MethodSerializer, TechniqueSerializer,
    ProformaSerializer, AnalysisSerializer, CompanySettingsSerializer,
    ProformaCreateSerializer, ParameterSearchSerializer, MethodSearchSerializer,
    TechniqueSearchSerializer, ClientSearchSerializer, TipoMuestraSerializer
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

class ParameterViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Parameter.objects(is_active=True)
        serializer = ParameterSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        category = request.query_params.get('category')
        query = request.query_params.get('q', '')
        if not category:
            return Response({'error': 'Categoría requerida'}, status=status.HTTP_400_BAD_REQUEST)
        parameters = Parameter.objects(category=category, is_active=True)
        if query:
            parameters = parameters.filter(name__icontains=query)
        serializer = ParameterSearchSerializer(parameters[:10], many=True)
        return Response(serializer.data)

class MethodViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Method.objects(is_active=True)
        serializer = MethodSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        category = request.query_params.get('category')
        query = request.query_params.get('q', '')
        if not category:
            return Response({'error': 'Categoría requerida'}, status=status.HTTP_400_BAD_REQUEST)
        methods = Method.objects(category=category, is_active=True)
        if query:
            methods = methods.filter(name__icontains=query)
        serializer = MethodSearchSerializer(methods[:10], many=True)
        return Response(serializer.data)

class TechniqueViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Technique.objects(is_active=True)
        serializer = TechniqueSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        category = request.query_params.get('category')
        query = request.query_params.get('q', '')
        if not category:
            return Response({'error': 'Categoría requerida'}, status=status.HTTP_400_BAD_REQUEST)
        techniques = Technique.objects(category=category, is_active=True)
        if query:
            techniques = techniques.filter(name__icontains=query)
        serializer = TechniqueSearchSerializer(techniques[:10], many=True)
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

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        if not query or len(query) < 2:
            return Response([])
        tipos = TipoMuestra.objects(nombre__icontains=query)[:10]
        serializer = TipoMuestraSerializer(tipos, many=True)
        return Response(serializer.data)
