from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from .utils import generate_proforma_preview
from django.db.models import Q
from django.http import HttpResponse
from .models import Client, Parameter, Method, Technique, Proforma, Analysis, CompanySettings
from .serializers import (
    ClientSerializer, ParameterSerializer, MethodSerializer, TechniqueSerializer,
    ProformaSerializer, AnalysisSerializer, CompanySettingsSerializer,
    ProformaCreateSerializer, ParameterSearchSerializer, MethodSearchSerializer,
    TechniqueSearchSerializer, ClientSearchSerializer
)


class ClientViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de clientes"""
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    # permission_classes = [IsAuthenticated]  # Descomenta cuando tengas auth
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'ruc', 'email']
    filterset_fields = ['name', 'ruc']

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Endpoint para autocompletado de clientes"""
        query = request.query_params.get('q', '')
        if len(query) < 2:
            return Response([])
        
        clients = Client.objects.filter(
            Q(name__icontains=query) | Q(ruc__icontains=query)
        )[:10]
        
        serializer = ClientSearchSerializer(clients, many=True)
        return Response(serializer.data)


class ParameterViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de parámetros"""
    queryset = Parameter.objects.filter(is_active=True)
    serializer_class = ParameterSerializer
    # permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']
    filterset_fields = ['category', 'is_active']

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Obtiene parámetros filtrados por categoría"""
        category = request.query_params.get('category')
        query = request.query_params.get('q', '')
        
        if not category:
            return Response({'error': 'Categoría requerida'}, status=status.HTTP_400_BAD_REQUEST)
        
        parameters = Parameter.objects.filter(category=category, is_active=True)
        
        if query:
            parameters = parameters.filter(name__icontains=query)
        
        serializer = ParameterSearchSerializer(parameters[:10], many=True)
        return Response(serializer.data)


class MethodViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de métodos"""
    queryset = Method.objects.filter(is_active=True)
    serializer_class = MethodSerializer
    # permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']
    filterset_fields = ['category', 'is_active']

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Obtiene métodos filtrados por categoría"""
        category = request.query_params.get('category')
        query = request.query_params.get('q', '')
        
        if not category:
            return Response({'error': 'Categoría requerida'}, status=status.HTTP_400_BAD_REQUEST)
        
        methods = Method.objects.filter(category=category, is_active=True)
        
        if query:
            methods = methods.filter(name__icontains=query)
        
        serializer = MethodSearchSerializer(methods[:10], many=True)
        return Response(serializer.data)


class TechniqueViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de técnicas"""
    queryset = Technique.objects.filter(is_active=True)
    serializer_class = TechniqueSerializer
    # permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']
    filterset_fields = ['category', 'is_active']

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Obtiene técnicas filtradas por categoría"""
        category = request.query_params.get('category')
        query = request.query_params.get('q', '')
        
        if not category:
            return Response({'error': 'Categoría requerida'}, status=status.HTTP_400_BAD_REQUEST)
        
        techniques = Technique.objects.filter(category=category, is_active=True)
        
        if query:
            techniques = techniques.filter(name__icontains=query)
        
        serializer = TechniqueSearchSerializer(techniques[:10], many=True)
        return Response(serializer.data)


class ProformaViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de proformas"""
    queryset = Proforma.objects.all()
    # permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['proforma_number', 'client__name', 'client__ruc']
    filterset_fields = ['status', 'date', 'client']

    def get_serializer_class(self):
        if self.action == 'create':
            return ProformaCreateSerializer
        return ProformaSerializer

    @action(detail=True, methods=['post'])
    def add_analysis(self, request, pk=None):
        """Añade un análisis a una proforma existente"""
        proforma = self.get_object()
        serializer = AnalysisSerializer(data=request.data)
        
        if serializer.is_valid():
            # Obtener el último orden para esta proforma
            last_order = Analysis.objects.filter(proforma=proforma).count()
            serializer.save(proforma=proforma, order=last_order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def remove_analysis(self, request, pk=None):
        """Elimina un análisis de una proforma"""
        proforma = self.get_object()
        analysis_id = request.data.get('analysis_id')
        
        if not analysis_id:
            return Response({'error': 'analysis_id requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            analysis = Analysis.objects.get(id=analysis_id, proforma=proforma)
            analysis.delete()
            return Response({'message': 'Análisis eliminado exitosamente'}, status=status.HTTP_200_OK)
        except Analysis.DoesNotExist:
            return Response({'error': 'Análisis no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplica una proforma existente"""
        original_proforma = self.get_object()
        
        # Crear nueva proforma
        new_proforma_data = {
            'client': original_proforma.client.id,
            'date': request.data.get('date', original_proforma.date),
            'status': 'draft',
            'created_by': request.data.get('created_by', original_proforma.created_by)
        }
        
        # Obtener análisis originales
        original_analyses = Analysis.objects.filter(proforma=original_proforma)
        analysis_data = []
        
        for analysis in original_analyses:
            analysis_data.append({
                'parameter': analysis.parameter.id,
                'unit': analysis.unit,
                'method': analysis.method.id,
                'technique': analysis.technique.id,
                'unit_price': analysis.unit_price,
                'quantity': analysis.quantity
            })
        
        new_proforma_data['analysis_data'] = analysis_data
        
        serializer = ProformaCreateSerializer(data=new_proforma_data)
        if serializer.is_valid():
            new_proforma = serializer.save()
            response_serializer = ProformaSerializer(new_proforma)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def export_pdf(self, request, pk=None):
        """Exporta la proforma como PDF"""
        proforma = self.get_object()
        
        try:
            from .utils import generate_proforma_pdf
            pdf_content = generate_proforma_pdf(proforma)
            
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="proforma_{proforma.proforma_number}.pdf"'
            return response
            
        except ImportError:
            return Response(
                {'error': 'Generación de PDF no implementada aún'}, 
                status=status.HTTP_501_NOT_IMPLEMENTED
            )
        except Exception as e:
            return Response(
                {'error': f'Error generando PDF: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        from .utils import generate_proforma_preview
        proforma = self.get_object()
        html_content = generate_proforma_preview(proforma)
        return HttpResponse(html_content)
    
    @action(detail=False, methods=['post'])
    def preview_temp(self, request):
        """
        Genera una vista previa de una proforma SIN GUARDARLA.
        """
        data = request.data

        # Simular objetos como si fueran reales
        try:
            client_data = data.get("client_data", {})
            analysis_data = data.get("analysis_data", [])
            from datetime import datetime

            date_str = data.get("date")
            proforma_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.today().date()

            # Crear cliente falso (no se guarda)
            from .models import Client, Proforma, Analysis, Parameter, Method, Technique

            class Dummy:
                pass

            dummy_client = Dummy()
            dummy_client.name = client_data["name"]
            dummy_client.ruc = client_data["ruc"]
            dummy_client.address = client_data["address"]
            dummy_client.phone = client_data["phone"]
            dummy_client.email = client_data["email"]
            dummy_client.contact_person = client_data["contact_person"]

            dummy_proforma = Dummy()
            dummy_proforma.proforma_number = "SIN-GUARDAR"
            dummy_proforma.date = proforma_date
            dummy_proforma.client = dummy_client
            dummy_proforma.subtotal = 0
            dummy_proforma.tax_amount = 0
            dummy_proforma.total = 0

            dummy_proforma.analysis_set = []

            subtotal = 0

            for item in analysis_data:
                a = Dummy()
                param = Parameter.objects.get(id=item["parameter"])
                method = Method.objects.get(id=item["method"])
                tech = Technique.objects.get(id=item["technique"])
                a.parameter = param
                a.method = method
                a.technique = tech
                a.unit = item["unit"]
                a.quantity = int(item["quantity"])
                a.unit_price = float(item["unit_price"])
                a.subtotal = a.quantity * a.unit_price
                subtotal += a.subtotal
                dummy_proforma.analysis_set.append(a)

            dummy_proforma.subtotal = subtotal
            dummy_proforma.tax_amount = subtotal * 0.12
            dummy_proforma.total = dummy_proforma.subtotal + dummy_proforma.tax_amount

            html = generate_proforma_preview(dummy_proforma)
            return HttpResponse(html)

        except Exception as e:
            return Response({"error": str(e)}, status=400)


class AnalysisViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de análisis individuales"""
    queryset = Analysis.objects.all()
    serializer_class = AnalysisSerializer
    # permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['proforma', 'parameter__category']

    def perform_create(self, serializer):
        """Asigna orden automáticamente al crear análisis"""
        proforma = serializer.validated_data['proforma']
        last_order = Analysis.objects.filter(proforma=proforma).count()
        serializer.save(order=last_order)

    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """Reordena análisis de una proforma"""
        analysis_orders = request.data.get('analysis_orders', [])
        
        for item in analysis_orders:
            try:
                analysis = Analysis.objects.get(id=item['id'])
                analysis.order = item['order']
                analysis.save()
            except Analysis.DoesNotExist:
                continue
        
        return Response({'message': 'Orden actualizado exitosamente'})


class CompanySettingsViewSet(viewsets.ModelViewSet):
    """ViewSet para configuración de empresa"""
    queryset = CompanySettings.objects.all()
    serializer_class = CompanySettingsSerializer
    # permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def current(self, request):
        """Obtiene la configuración actual de la empresa"""
        try:
            settings = CompanySettings.objects.first()
            if not settings:
                # Crear configuración por defecto
                settings = CompanySettings.objects.create(
                    company_name="ENVIRONOVALAB",
                    company_address="Dirección por defecto",
                    company_phone="000-000-0000",
                    company_email="info@environovalab.com",
                    company_ruc="0000000000000"
                )
            
            serializer = CompanySettingsSerializer(settings)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': f'Error obteniendo configuración: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    