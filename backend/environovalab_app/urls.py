from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Importación de ViewSets
from .views.user_admin_views import UserAdminViewSet
from .views.tipo_muestra_views import TipoMuestraViewSet
from .views.proforma_views import ProformaViewSet
from .views.client_views import ClientViewSet
from .views.analysis_views import AnalysisViewSet
from .views.informe_views import InformeViewSet
from .views.company_views import CompanySettingsViewSet

# Importación de vistas tipo APIView
from .views.auth_views import RegisterView, LoginView, LogoutView
from .views.password_views import ForgotPasswordView, ResetPasswordView

router = DefaultRouter()
router.register(r'admin/users', UserAdminViewSet, basename='user-admin')
router.register(r'tipos-muestra', TipoMuestraViewSet, basename='tipos-muestra')
router.register(r'proformas', ProformaViewSet, basename='proformas')
router.register(r'clients', ClientViewSet, basename='clients')
router.register(r'analysis', AnalysisViewSet, basename='analysis')
router.register(r'informes', InformeViewSet, basename='informes')
router.register(r'settings', CompanySettingsViewSet, basename='settings')

urlpatterns = [
    # Rutas para autenticación
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('forgot-password/', ForgotPasswordView.as_view()),
    path('reset-password/<str:token>/', ResetPasswordView.as_view()),

    # Rutas RESTful
    path('', include(router.urls)),
]
