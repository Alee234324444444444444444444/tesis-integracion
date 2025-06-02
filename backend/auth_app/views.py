from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from django.contrib.auth.hashers import make_password, check_password

class RegisterView(APIView):
    def post(self, request):
        data = request.data

        if not data.get('username') or not data.get('password'):
            return Response({'error': 'Faltan campos requeridos'}, status=400)

        if User.objects(username=data['username']).first():
            return Response({'error': 'Usuario ya existe'}, status=400)

        user = User(
            username=data['username'],
            password=make_password(data['password'])
        )
        user.save()
        return Response({'msg': 'Usuario creado correctamente'}, status=201)


class LoginView(APIView):
    def post(self, request):
        user = User.objects(username=request.data.get('username')).first()

        if user and check_password(request.data.get('password'), user.password):
            request.session['user'] = user.username
            return Response({
                'msg': 'Login correcto',
                'username': user.username  # ✅ enviamos el username al frontend
            })
        return Response({'error': 'Credenciales incorrectas'}, status=400)



class LogoutView(APIView):
    def post(self, request):
        request.session.flush()
        return Response({'msg': 'Sesión cerrada'})


class ForgotPasswordView(APIView):
    def post(self, request):
        username = request.data.get('username')

        if not username:
            return Response({'error': 'El campo usuario es requerido'}, status=400)

        user = User.objects(username=username).first()
        if not user:
            return Response({'error': 'Usuario no encontrado'}, status=404)

        # Aquí iría lógica real de recuperación (correo, token, etc.)
        # Por ahora solo devolvemos el mensaje simulado
        return Response({'msg': 'Solicitud enviada. Revisa tu correo.'}, status=200)
