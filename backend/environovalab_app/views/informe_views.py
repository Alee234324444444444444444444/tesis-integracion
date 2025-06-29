from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from environovalab_app.models.informe import Informe
from environovalab_app.models.resultado import Resultado
from environovalab_app.serializers.informe_serializer import InformeSerializer
from environovalab_app.serializers.resultado_serializer import ResultadoSerializer

class InformeViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = InformeSerializer(data=request.data)
        if serializer.is_valid():
            informe = serializer.save()
            return Response(InformeSerializer(informe).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        informes = Informe.objects()
        serializer = InformeSerializer(informes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def resultados(self, request, pk=None):
        try:
            informe = Informe.objects.get(id=pk)
        except Informe.DoesNotExist:
            raise NotFound("Informe no encontrado")
        resultados = Resultado.objects(informe=informe)
        serializer = ResultadoSerializer(resultados, many=True)
        return Response(serializer.data)
