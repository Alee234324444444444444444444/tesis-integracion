from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from environovalab_app.models.proforma import Proforma
from environovalab_app.models.analysis import Analysis
from environovalab_app.serializers.proforma_serializer import ProformaSerializer, ProformaCreateSerializer, AnalysisSerializer
from environovalab_app.utils import generate_proforma_pdf, generate_informe_pdf
from django.http import FileResponse
import os

class ProformaViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Proforma.objects()
        serializer = ProformaSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = ProformaCreateSerializer(data=request.data)
        if serializer.is_valid():
            proforma = serializer.save()
            generate_proforma_pdf(proforma.id)
            proforma.reload()
            return Response(ProformaSerializer(proforma).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def add_analysis(self, request, pk=None):
        try:
            proforma = Proforma.objects.get(id=pk)
        except Proforma.DoesNotExist:
            raise NotFound('Proforma no encontrada')
        serializer = AnalysisSerializer(data=request.data)
        if serializer.is_valid():
            last_order = Analysis.objects(proforma=proforma).count()
            analysis = serializer.save(proforma=proforma, order=last_order)
            generate_proforma_pdf(proforma.id)
            proforma.reload()
            return Response(ProformaSerializer(proforma).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def remove_analysis(self, request, pk=None):
        try:
            proforma = Proforma.objects.get(id=pk)
        except Proforma.DoesNotExist:
            raise NotFound('Proforma no encontrada')
        analysis_id = request.data.get('analysis_id')
        if not analysis_id:
            return Response({'error': 'analysis_id requerido'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            analysis = Analysis.objects.get(id=analysis_id, proforma=proforma)
            analysis.delete()
            generate_proforma_pdf(proforma.id)
            proforma.reload()
            return Response(ProformaSerializer(proforma).data, status=status.HTTP_200_OK)
        except Analysis.DoesNotExist:
            return Response({'error': 'Análisis no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def pdf(self, request, pk=None):
        try:
            proforma = Proforma.objects.get(id=pk)
        except Proforma.DoesNotExist:
            raise NotFound('Proforma no encontrada')
        if not proforma.pdf_url or not os.path.exists(proforma.pdf_url):
            return Response({'error': 'PDF no encontrado'}, status=404)
        return FileResponse(open(proforma.pdf_url, 'rb'), as_attachment=True, filename=os.path.basename(proforma.pdf_url))

    @action(detail=True, methods=['get'])
    def informe(self, request, pk=None):
        try:
            proforma = Proforma.objects.get(id=pk)
        except Proforma.DoesNotExist:
            raise NotFound('Proforma no encontrada')

        analysis = Analysis.objects(proforma=proforma).order_by('order')
        data = {
            "proforma_number": proforma.proforma_number,
            "date": proforma.date.isoformat(),
            "created_by": proforma.created_by,
            "client_name": proforma.client.name,
            "client_ruc": proforma.client.ruc,
            "client_address": proforma.client.address,
            "client_email": proforma.client.email,
            "client_contact": proforma.client.contact_person,
            "analysis_data": [
                {
                    "parameter": a.parameter,
                    "unit": a.unit,
                    "method": a.method,
                }
                for a in analysis
            ]
        }
        return Response(data)

    @action(detail=True, methods=['get'])
    def informe_pdf(self, request, pk=None):
        try:
            proforma = Proforma.objects.get(id=pk)
        except Proforma.DoesNotExist:
            raise NotFound('Proforma no encontrada')

        informe_pdf_path = generate_informe_pdf(proforma.id)
        return FileResponse(open(informe_pdf_path, 'rb'), as_attachment=True, filename=os.path.basename(informe_pdf_path))
