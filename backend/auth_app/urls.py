from .views import RegisterView, LoginView, LogoutView, ForgotPasswordView, ResetPasswordView, UserAdminViewSet
from rest_framework.routers import DefaultRouter
from django.urls import path, include

router = DefaultRouter()

router.register(r'admin/users', UserAdminViewSet, basename='user-admin')
urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('forgot-password/', ForgotPasswordView.as_view()),
    path('reset-password/<str:token>/', ResetPasswordView.as_view()),
    path('', include(router.urls)), 
]
