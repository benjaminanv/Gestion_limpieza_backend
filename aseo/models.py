from django.core.validators import RegexValidator
from django.db import models

validar_rut = RegexValidator(
    regex=r"^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$",
    message="El RUT debe tener el formato 12.345.678-9",
)

class Edificio(models.Model):
    codigo = models.CharField(max_length=5, unique=True)  # ej: "L"
    nombre = models.CharField(max_length=100)  # ej: "Edificio L"

    class Meta:
        ordering = ["codigo"]

    def __str__(self):
        return self.nombre

class Trabajador(models.Model):
    nombre = models.CharField(max_length=100)
    rut = models.CharField(max_length=12, unique=True, validators=[validar_rut])
    inicio_turno = models.TimeField()
    fin_turno = models.TimeField()

    class Meta:
        ordering = ["id"]
        verbose_name_plural = "trabajadores"

    def __str__(self):
        return self.nombre