from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("edificios", views.EdificioViewSet, basename="edificio")
router.register("trabajadores", views.TrabajadorViewSet, basename="trabajador")
router.register("salas", views.SalaViewSet, basename="sala")
router.register("incidencias", views.IncidenciaViewSet, basename="incidencia")

urlpatterns = [
    path("resumen/", views.ResumenView.as_view(), name="resumen"),
    path("", include(router.urls)),
]