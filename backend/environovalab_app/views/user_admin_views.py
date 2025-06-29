from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from environovalab_app.models.user import User
from django.contrib.auth.hashers import make_password

class UserAdminViewSet(ViewSet):
    def list(self, request):
        users = User.objects.all()
        return Response([
            {
                'id': str(u.id),
                'username': u.username,
                'email': u.email,
                'is_admin': u.is_admin,
                'activo': u.is_active
            }
            for u in users
        ])

    def create(self, request):
        data = request.data
        if not data.get("username") or not data.get("email") or not data.get("password"):
            return Response({'error': 'Todos los campos son obligatorios'}, status=status.HTTP_400_BAD_REQUEST)

        user = User(
            username=data["username"],
            email=data["email"],
            password=make_password(data["password"]),
            is_admin=data.get("is_admin", False),
            is_active=True
        )
        user.save()
        return Response({'msg': 'Usuario creado correctamente'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def update_role(self, request, pk=None):
        user = User.objects(id=pk).first()
        if not user:
            return Response({'error': 'Usuario no encontrado'}, status=404)
        user.is_admin = request.data.get('is_admin', False)
        user.save()
        return Response({'msg': 'Rol actualizado correctamente'})

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        user = User.objects(id=pk).first()
        if not user:
            return Response({'error': 'Usuario no encontrado'}, status=404)
        user.is_active = not user.is_active
        user.save()
        return Response({'msg': f'Usuario ahora está {"activo" if user.is_active else "inactivo"}'})
