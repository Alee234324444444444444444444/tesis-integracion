from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from mongoengine.queryset.visitor import Q
from environovalab_app.models.client import Client
from environovalab_app.serializers.client_serializer import ClientSerializer, ClientSearchSerializer

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
