from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

MAX_SALAS_POR_TRABAJADOR = 20

validar_rut = RegexValidator(
    regex=r"^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$",
    message="El RUT debe tener el formato 12.345.678-9",
)


class Edificio(models.Model):
    codigo = models.CharField(max_length=5, unique=True)
    nombre = models.CharField(max_length=100) 

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


class Sala(models.Model):
    ESTADOS = [
        ("limpio", "Limpio"),
        ("pendiente", "Pendiente"),
        ("en_proceso", "En proceso"),
    ]

   
    edificio = models.ForeignKey(Edificio, on_delete=models.CASCADE, related_name="salas")
    numero = models.CharField(max_length=10)  
    piso = models.PositiveSmallIntegerField()
    estado = models.CharField(max_length=15, choices=ESTADOS, default="pendiente")
    hora_ultima_limpieza = models.DateTimeField(null=True, blank=True)
    trabajadores = models.ManyToManyField(Trabajador, related_name="salas", blank=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            
            models.UniqueConstraint(fields=["edificio", "numero"], name="sala_unica_por_edificio"),
        ]

    def __str__(self):
        return self.numero

    def save(self, *args, **kwargs):
        
        if self.estado == "limpio" and self.hora_ultima_limpieza is None:
            self.hora_ultima_limpieza = timezone.now()
        super().save(*args, **kwargs)


class Incidencia(models.Model):
    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("resuelta", "Resuelta"),
    ]

    
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, related_name="incidencias")
    
    trabajador = models.ForeignKey(
        Trabajador, on_delete=models.SET_NULL, null=True, blank=True, related_name="incidencias"
    )
    descripcion = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default="pendiente")

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.sala} - {self.descripcion[:30]}"