from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    ClientViewSet, ParameterViewSet, MethodViewSet, TechniqueViewSet,
    ProformaViewSet, AnalysisViewSet, CompanySettingsViewSet, TipoMuestraViewSet,
    AnalisisCatalogoViewSet, csrf_token_view  # 👈 Nuevo import agregado
)

# Crear el router
router = DefaultRouter()
router.register(r'clients', ClientViewSet, basename='clients')
router.register(r'parameters', ParameterViewSet, basename='parameters')
router.register(r'methods', MethodViewSet, basename='methods')
router.register(r'techniques', TechniqueViewSet, basename='techniques')
router.register(r'proformas', ProformaViewSet, basename='proformas')
router.register(r'analysis', AnalysisViewSet, basename='analysis')
router.register(r'settings', CompanySettingsViewSet, basename='settings')
router.register(r'tipos-muestra', TipoMuestraViewSet, basename='tipos-muestra')
router.register(r'catalogo-analisis', AnalisisCatalogoViewSet, basename='catalogo-analisis')  # ✅ Nuevo ViewSet

# Rutas adicionales personalizadas
urlpatterns = router.urls + [
    path('search/clients/', ClientViewSet.as_view({'get': 'search'}), name='client-search'),
    path('search/parameters/<str:category>/', ParameterViewSet.as_view({'get': 'by_category'}), name='parameter-by-category'),
    path('search/methods/<str:category>/', MethodViewSet.as_view({'get': 'by_category'}), name='method-by-category'),
    path('search/techniques/<str:category>/', TechniqueViewSet.as_view({'get': 'by_category'}), name='technique-by-category'),
    path('search/tipos-muestra/', TipoMuestraViewSet.as_view({'get': 'search'}), name='tipo-muestra-search'),
    path('csrf/', csrf_token_view, name='csrf-token'),
]