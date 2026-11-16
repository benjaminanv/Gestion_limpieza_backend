# Gestion_limpieza_backend

## Bienvenido al README.md del backend de Gestion Aseo  

### Tecnologias Usadas

Framework: Django
API: Django rest Framework
DataBase: Sqlite3
Lenguaje: Python 3.X

## Modelos
Edificio -  Codigo, Nombre
Trabajador - Nombre , Rut, Inicio_turno, Fin_turno
Sala - Numero, Piso. Estado, Hora_ultima_limpieza
Incidencia - Descripcion, Fecha, estado

## Validaciones y Reglas de Negocio
- EL piso debe ser 1 o mayor y no debe repetirse el numero de sala dentro de un mismo edificio.
- El rut debe tener el formato 12.345.678-9
- El fin del turno tiene que ocurrir despues del inicio del turno
- Regla de negocio 1: Al actualizar el estado de limpieza a limpio de una sala el servidor automaticamente genera el registro de hora de ultima limpieza.
- regla de negocio 2: Un trabajador no puede tener mas de 20 salas asignadas. ( facil de modificar segun necesidad ).
. Regla de negocio 3: Un trabajador solamente puede generar incidencias de sus salas asignadas
  
## Instalacion y Ejecuciom
1. Clonar repositorio
   git clone https://github.com/benjaminanv/Gestion_limpieza_backend.git
   cd Gestion_limpieza_backend
2. Crear y activar un entorno virtual:
   python -m venv venv
   venv\Scripts\activate
3. Instalar Dependencias
   pip install -r requeriments.txt
4. Cargar datos inciales
