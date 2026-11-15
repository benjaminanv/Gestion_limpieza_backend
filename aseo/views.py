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

