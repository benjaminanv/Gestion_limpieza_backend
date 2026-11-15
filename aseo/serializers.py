from rest_framework import serializers

from .models import Edificio, Incidencia, Sala, Trabajador

class EdificioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Edificio
        fields = ["id", "codigo", "nombre"]
