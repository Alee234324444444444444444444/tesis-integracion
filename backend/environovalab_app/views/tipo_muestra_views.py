from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from environovalab_app.models.tipo_muestra import TipoMuestra
from environovalab_app.serializers.tipo_muestra_serializer import TipoMuestraSerializer

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
