from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from environovalab_app.models.analysis import Analysis
from environovalab_app.serializers.analysis_serializer import AnalysisSerializer

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
