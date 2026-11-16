import json
from datetime import datetime
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils import timezone

from aseo.models import Edificio, Incidencia, Sala, Trabajador

ARCHIVO = Path(__file__).resolve().parent.parent.parent / "data" / "datos_iniciales.json"


def a_fecha(texto):
    """'2026-09-16T08:15:00' -> datetime con zona horaria"""
    return timezone.make_aware(datetime.fromisoformat(texto))


class Command(BaseCommand):
    help = "Carga los datos iniciales (los mismos que usa el front de React). Se puede ejecutar varias veces."

    def handle(self, *args, **opciones):
        datos = json.loads(ARCHIVO.read_text(encoding="utf-8"))

        for e in datos["edificios"]:
            Edificio.objects.update_or_create(codigo=e["codigo"], defaults={"nombre": e["nombre"]})

        for t in datos["trabajadores"]:
            Trabajador.objects.update_or_create(id=t["id"], defaults={
                "nombre": t["nombre"], "rut": t["rut"],
                "inicio_turno": t["inicio_turno"], "fin_turno": t["fin_turno"],
            })

        for s in datos["salas"]:
            sala, _ = Sala.objects.update_or_create(id=s["id"], defaults={
                "edificio": Edificio.objects.get(codigo=s["edificio"]),
                "numero": s["numero"], "piso": s["piso"], "estado": s["estado"],
                "hora_ultima_limpieza": a_fecha(s["hora_ultima_limpieza"]),
            })
            sala.trabajadores.set(s["trabajadores"])

        for i in datos["incidencias"]:
            Incidencia.objects.update_or_create(id=i["id"], defaults={
                "sala_id": i["sala"], "trabajador_id": i["trabajador"],
                "descripcion": i["descripcion"], "estado": i["estado"],
            })
            # 'fecha' es auto_now_add: se corrige después para conservar la fecha original
            Incidencia.objects.filter(pk=i["id"]).update(fecha=a_fecha(i["fecha"]))

        if opciones["verbosity"] > 0:
            self.stdout.write(self.style.SUCCESS(
                f"Datos cargados: {Edificio.objects.count()} edificio(s), "
                f"{Trabajador.objects.count()} trabajadores, {Sala.objects.count()} salas, "
                f"{Incidencia.objects.count()} incidencia(s)."
            ))