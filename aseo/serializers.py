from rest_framework import serializers

from .models import Edificio, Incidencia, Sala, Trabajador

class EdificioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Edificio
        fields = ["id", "codigo", "nombre"]

class TrabajadorSerializer(serializers.ModelSerializer):
    salas = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Trabajador
        fields = ["id", "nombre", "rut", "inicio_turno", "fin_turno", "salas"]

    def validate_nombre(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("El nombre debe tener al menos 3 caracteres.")
        return value

    def validate(self, datos):
        inicio = datos.get("inicio_turno", getattr(self.instance, "inicio_turno", None))
        fin = datos.get("fin_turno", getattr(self.instance, "fin_turno", None))
        if inicio and fin and fin <= inicio:
            raise serializers.ValidationError("El fin del turno debe ser posterior al inicio.")
        return datos