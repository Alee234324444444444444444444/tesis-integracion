from urllib import request
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from mongoengine.queryset.visitor import Q
from .utils import generate_proforma_preview
from .models import Client, Parameter, Method, Technique, Proforma, Analysis, CompanySettings, TipoMuestra, AnalisisCatalogo
from .serializers import (
    ClientSerializer, ParameterSerializer, MethodSerializer, TechniqueSerializer,
    ProformaSerializer, AnalysisSerializer, CompanySettingsSerializer,
    ProformaCreateSerializer, ParameterSearchSerializer, MethodSearchSerializer,
    TechniqueSearchSerializer, ClientSearchSerializer, TipoMuestraSerializer, AnalisisCatalogoSerializer
)
from .permissions import IsAdminUserCustom  # Nuevo permiso personalizado

class ClientViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = Parameter.objects(is_active=True)
        serializer = ParameterSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        print("SESION ACTUAL:", request.session.get('user'))
        if not IsAdminUserCustom().has_permission(request, self):
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        serializer = ParameterSerializer(data=request.data)
        if serializer.is_valid():
            parameter = serializer.save()
            return Response(ParameterSerializer(parameter).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = Method.objects(is_active=True)
        serializer = MethodSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        if not IsAdminUserCustom().has_permission(request, self):
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        serializer = MethodSerializer(data=request.data)
        if serializer.is_valid():
            method = serializer.save()
            return Response(MethodSerializer(method).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = Technique.objects(is_active=True)
        serializer = TechniqueSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        if not IsAdminUserCustom().has_permission(request, self):
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        serializer = TechniqueSerializer(data=request.data)
        if serializer.is_valid():
            technique = serializer.save()
            return Response(TechniqueSerializer(technique).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = Analysis.objects()
        serializer = AnalysisSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        if not IsAdminUserCustom().has_permission(request, self):
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        serializer = AnalysisSerializer(data=request.data)
        if serializer.is_valid():
            analysis = serializer.save()
            return Response(AnalysisSerializer(analysis).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = TipoMuestra.objects()
        serializer = TipoMuestraSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        if not IsAdminUserCustom().has_permission(request, self):
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
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
    

class AnalisisCatalogoViewSet(viewsets.ViewSet):
    """
    ViewSet para gestionar análisis predefinidos por tipo (agua, ruido, etc.)
    """

    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        Listar todos los análisis filtrables por tipo o búsqueda.
        """
        tipo = request.query_params.get('tipo')
        q = request.query_params.get('q', '')

        queryset = AnalisisCatalogo.objects(is_active=True)

        if tipo:
            queryset = queryset.filter(tipo=tipo)

        if q:
            queryset = queryset.filter(Q(parametro__icontains=q) | Q(metodo__icontains=q) | Q(tecnica__icontains=q))

        serializer = AnalisisCatalogoSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        print("🔍 Sesión activa:", request.session.get("user"))
        print("🔒 Headers CSRF:", request.META.get("HTTP_X_CSRFTOKEN"))
        """
        Crear un nuevo análisis (solo admin).
        """
        if not IsAdminUserCustom().has_permission(request, self):
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)

        serializer = AnalisisCatalogoSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(AnalisisCatalogoSerializer(instance).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Eliminar un análisis por ID (solo admin).
        """
        if not IsAdminUserCustom().has_permission(request, self):
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)

        try:
            item = AnalisisCatalogo.objects.get(id=pk)
            item.delete()
            return Response({'message': 'Eliminado correctamente'})
        except AnalisisCatalogo.DoesNotExist:
            return Response({'error': 'No encontrado'}, status=status.HTTP_404_NOT_FOUND)
        



@ensure_csrf_cookie
def csrf_token_view(request):
    return JsonResponse({'msg': 'CSRF cookie set'})