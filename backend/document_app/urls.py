from rest_framework.routers import DefaultRouter
from .views import (
    ClientViewSet,
    ProformaViewSet, AnalysisViewSet, CompanySettingsViewSet, TipoMuestraViewSet, InformeViewSet
)

router = DefaultRouter()
router.register(r'clients', ClientViewSet, basename='clients')
router.register(r'proformas', ProformaViewSet, basename='proformas')
router.register(r'analysis', AnalysisViewSet, basename='analysis')
router.register(r'settings', CompanySettingsViewSet, basename='settings')
router.register(r'tipos-muestra', TipoMuestraViewSet, basename='tipos-muestra')
router.register(r'informes', InformeViewSet, basename='informes')


urlpatterns = router.urls

# Si quieres rutas tipo /search/clients/ puedes agregarlas como extra,
# pero DRF con @action ya expone /clients/search/ y /tipos-muestra/search/
