from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import MAX_SALAS_POR_TRABAJADOR, Edificio, Incidencia, Sala, Trabajador
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
    """CRUD de salas (entidad principal) + filtros por query params."""

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

    @action(detail=True, methods=["post"], url_path="alternar-trabajador")
    def alternar_trabajador(self, request, pk=None):
        """Asigna el trabajador a la sala, o lo quita si ya estaba asignado."""
        sala = self.get_object()
        trabajador = get_object_or_404(Trabajador, pk=request.data.get("trabajador"))

        if sala.trabajadores.filter(pk=trabajador.pk).exists():
            sala.trabajadores.remove(trabajador)
        else:
            if trabajador.salas.count() >= MAX_SALAS_POR_TRABAJADOR:
                return Response(
                    {"trabajador": f"{trabajador.nombre} ya tiene {MAX_SALAS_POR_TRABAJADOR} salas asignadas."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            sala.trabajadores.add(trabajador)
        return Response(self.get_serializer(sala).data)


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

    @action(detail=True, methods=["post"], url_path="alternar-estado")
    def alternar_estado(self, request, pk=None):
        """Pasa la incidencia de pendiente a resuelta y viceversa (botón "Reabrir")."""
        incidencia = self.get_object()
        incidencia.estado = "resuelta" if incidencia.estado == "pendiente" else "pendiente"
        incidencia.save()
        return Response(self.get_serializer(incidencia).data)


class ResumenView(APIView):
    """Datos para la Vista principal: totales por estado y porcentaje de salas limpias."""

    def get(self, request):
        salas = Sala.objects.all()
        if request.query_params.get("edificio"):
            salas = salas.filter(edificio__codigo=request.query_params["edificio"])

        total = salas.count()
        limpias = salas.filter(estado="limpio").count()
        return Response({
            "total_salas": total,
            "limpias": limpias,
            "pendientes": salas.filter(estado="pendiente").count(),
            "en_proceso": salas.filter(estado="en_proceso").count(),
            "porcentaje_limpio": round(limpias / total * 100) if total else 0,
            "incidencias_pendientes": Incidencia.objects.filter(
                estado="pendiente", sala__in=salas
            ).count(),
        })