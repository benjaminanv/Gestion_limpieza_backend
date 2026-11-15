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
        fi  n = datos.get("fin_turno", getattr(self.instance, "fin_turno", None))
        if inicio and fin and fin <= inicio:
            raise serializers.ValidationError("El fin del turno debe ser posterior al inicio.")
        return datos
    
class SalaSerializer(serializers.ModelSerializer):
    incidencias_pendientes = serializers.SerializerMethodField()

    class Meta:
        model = Sala
        fields = [
            "id", "edificio", "numero", "piso", "estado",
            "hora_ultima_limpieza", "trabajadores", "incidencias_pendientes",
        ]
        read_only_fields = ["hora_ultima_limpieza"]

    def get_incidencias_pendientes(self, sala):
        return sala.incidencias.filter(estado="pendiente").count()

    def validate_piso(self, value):
        if value < 1:
            raise serializers.ValidationError("El piso debe ser 1 o mayor.")
        return value

class IncidenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incidencia
        fields = ["id", "sala", "trabajador", "descripcion", "fecha", "estado"]
        read_only_fields = ["fecha"]

    def validate_descripcion(self, value):
        value = value.strip()
        if len(value) < 5:
            raise serializers.ValidationError("Describe la incidencia con al menos 5 caracteres.")
        return value
