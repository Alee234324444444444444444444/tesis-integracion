from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password, check_password
from environovalab_app.models.user import User

class RegisterView(APIView):
    def post(self, request):
        data = request.data
        if not data.get('username') or not data.get('password') or not data.get('email'):
            return Response({'error': 'Faltan campos requeridos'}, status=400)
        if User.objects(username=data['username']).first():
            return Response({'error': 'Usuario ya existe'}, status=400)
        if User.objects(email=data['email']).first():
            return Response({'error': 'Email ya está en uso'}, status=400)

        user = User(
            username=data['username'],
            password=make_password(data['password']),
            email=data['email'],
            is_admin=data.get('is_admin', False),
            is_active=True
        )
        user.save()
        return Response({'msg': 'Usuario creado correctamente'}, status=201)

class LoginView(APIView):
    def post(self, request):
        user = User.objects(username=request.data.get('username')).first()
        if user and check_password(request.data.get('password'), user.password):
            if not user.is_active:
                return Response({'error': 'Cuenta inactiva. Contacta con el administrador.'}, status=403)
            request.session['user'] = user.username
            return Response({
                'msg': 'Login correcto',
                'username': user.username,
                'is_admin': user.is_admin
            })
        return Response({'error': 'Credenciales incorrectas'}, status=400)

class LogoutView(APIView):
    def post(self, request):
        request.session.flush()
        return Response({'msg': 'Sesión cerrada'})