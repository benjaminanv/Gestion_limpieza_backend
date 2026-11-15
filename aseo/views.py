from rest_framework import viewsets

from .models import Edificio, Incidencia, Sala, Trabajador
from .serializers import (
    EdificioSerializer,
    IncidenciaSerializer,
    SalaSerializer,
    TrabajadorSerializer,
)
class EdificioViewSet(viewsets.ModelViewSet):
    queryset = Edificio.objects.all()
    serializer_class = EdificioSerializer


class TrabajadorViewSet(viewsets.ModelViewSet):
    queryset = Trabajador.objects.prefetch_related("salas")
    serializer_class = TrabajadorSerializer


class SalaViewSet(viewsets.ModelViewSet):
    """CRUD de salas (entidad principal) con filtros opcionales."""

    serializer_class = SalaSerializer

    def get_queryset(self):
        salas = Sala.objects.prefetch_related("trabajadores", "incidencias")
        params = self.request.query_params
        if params.get("piso"):
            salas = salas.filter(piso=params["piso"])
        if params.get("estado"):
            salas = salas.filter(estado=params["estado"])
        if params.get("edificio"):
            salas = salas.filter(edificio__codigo=params["edificio"])
        if params.get("buscar"):
            salas = salas.filter(numero__icontains=params["buscar"])
        return salas

class IncidenciaViewSet(viewsets.ModelViewSet):
    serializer_class = IncidenciaSerializer

    def get_queryset(self):
        incidencias = Incidencia.objects.all()
        params = self.request.query_params
        if params.get("sala"):
            incidencias = incidencias.filter(sala_id=params["sala"])
        if params.get("estado"):
            incidencias = incidencias.filter(estado=params["estado"])
        return incidencias