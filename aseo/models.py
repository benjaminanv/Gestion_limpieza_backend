from django.core.validators import RegexValidator
from django.db import models

validar_rut = RegexValidator(
    regex=r"^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$",
    message="El RUT debe tener el formato 12.345.678-9",
)