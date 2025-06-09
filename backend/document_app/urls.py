from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    ClientViewSet, ParameterViewSet, MethodViewSet, TechniqueViewSet,
    ProformaViewSet, AnalysisViewSet, CompanySettingsViewSet
)

# Crear el router
router = DefaultRouter()
router.register(r'clients', ClientViewSet)
router.register(r'parameters', ParameterViewSet)
router.register(r'methods', MethodViewSet)
router.register(r'techniques', TechniqueViewSet)
router.register(r'proformas', ProformaViewSet)
router.register(r'analysis', AnalysisViewSet)
router.register(r'settings', CompanySettingsViewSet)

# Combinar rutas del router con rutas personalizadas
urlpatterns = router.urls + [
    path('search/clients/', ClientViewSet.as_view({'get': 'search'}), name='client-search'),
    path('search/parameters/<str:category>/', ParameterViewSet.as_view({'get': 'by_category'}), name='parameter-by-category'),
    path('search/methods/<str:category>/', MethodViewSet.as_view({'get': 'by_category'}), name='method-by-category'),
    path('search/techniques/<str:category>/', TechniqueViewSet.as_view({'get': 'by_category'}), name='technique-by-category'),
]