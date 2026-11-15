from rest_framework import viewsets

from .models import Edificio, Incidencia, Sala, Trabajador
from .serializers import (
    EdificioSerializer,
    IncidenciaSerializer,
    SalaSerializer,
    TrabajadorSerializer,
)


