from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.conf import settings
from environovalab_app.models.user import User
import uuid

RESET_TOKENS = {}

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
