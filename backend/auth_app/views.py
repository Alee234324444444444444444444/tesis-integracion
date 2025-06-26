from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from .models import User
from django.contrib.auth.hashers import make_password, check_password
import uuid
from django.core.mail import send_mail
from django.conf import settings

RESET_TOKENS = {}

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

class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'El campo correo electrónico es requerido'}, status=400)
        user = User.objects(email=email).first()
        if not user:
            return Response({'error': 'Usuario no encontrado con ese correo'}, status=404)

        token = str(uuid.uuid4())
        RESET_TOKENS[token] = user.username
        reset_link = f"http://localhost:3000/reset-password/{token}"

        send_mail(
            'Recuperación de contraseña - Environovalab',
            f'Hola, haz clic aquí para restablecer tu contraseña:\n{reset_link}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        return Response({'msg': 'Correo enviado. Revisa tu correo para recuperar tu cuenta.'})

class ResetPasswordView(APIView):
    def post(self, request, token):
        new_password = request.data.get('password')
        username = RESET_TOKENS.get(token)
        if not username:
            return Response({'error': 'Token inválido o expirado'}, status=400)

        user = User.objects(username=username).first()
        user.password = make_password(new_password)
        user.save()
        del RESET_TOKENS[token]
        return Response({'msg': 'Contraseña actualizada correctamente'})

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
