from django.core.management import call_command
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import MAX_SALAS_POR_TRABAJADOR, Edificio, Incidencia, Sala, Trabajador


class BaseApiTest(APITestCase):
    def setUp(self):
        # Usa los mismos datos del front (también prueba el comando de carga)
        call_command("cargar_datos", verbosity=0)
        self.edificio = Edificio.objects.get(codigo="L")


class SalaCrudTests(BaseApiTest):
    def test_listar_salas(self):
        r = self.client.get("/api/salas/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(len(r.json()), 29)

    def test_detalle_sala_y_404(self):
        self.assertEqual(self.client.get("/api/salas/1/").status_code, 200)
        self.assertEqual(self.client.get("/api/salas/9999/").status_code, 404)

    def test_crear_sala(self):
        r = self.client.post("/api/salas/", {"edificio": self.edificio.id, "numero": "L-60", "piso": 5})
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r.json()["estado"], "pendiente")  # valor por defecto

    def test_editar_sala_put_y_patch(self):
        r = self.client.put("/api/salas/1/", {
            "edificio": self.edificio.id, "numero": "L-11", "piso": 1, "estado": "pendiente",
        })
        self.assertEqual(r.status_code, 200)
        r = self.client.patch("/api/salas/1/", {"estado": "en_proceso"})
        self.assertEqual(r.json()["estado"], "en_proceso")

    def test_eliminar_sala(self):
        self.assertEqual(self.client.delete("/api/salas/1/").status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.client.get("/api/salas/1/").status_code, 404)

    # ---- validaciones ----
    def test_piso_invalido(self):
        r = self.client.post("/api/salas/", {"edificio": self.edificio.id, "numero": "L-99", "piso": 0})
        self.assertEqual(r.status_code, 400)
        self.assertIn("piso", r.json())

    def test_estado_invalido(self):
        r = self.client.patch("/api/salas/1/", {"estado": "inventado"})
        self.assertEqual(r.status_code, 400)

    def test_numero_repetido_en_mismo_edificio(self):
        r = self.client.post("/api/salas/", {"edificio": self.edificio.id, "numero": "L-11", "piso": 1})
        self.assertEqual(r.status_code, 400)

    def test_faltan_campos_obligatorios(self):
        r = self.client.post("/api/salas/", {"numero": "L-70"})
        self.assertEqual(r.status_code, 400)
        self.assertIn("edificio", r.json())

    # ---- filtros ----
    def test_filtros(self):
        self.assertEqual(len(self.client.get("/api/salas/?piso=4").json()), 10)
        pendientes = self.client.get("/api/salas/?estado=pendiente").json()
        self.assertTrue(all(s["estado"] == "pendiente" for s in pendientes))
        buscadas = self.client.get("/api/salas/?buscar=L-36").json()
        self.assertEqual([s["numero"] for s in buscadas], ["L-36"])
        self.assertEqual(len(self.client.get("/api/salas/?edificio=L&piso=1").json()), 2)
        self.assertEqual(len(self.client.get("/api/salas/?edificio=ZZ").json()), 0)


class ReglasDeNegocioTests(BaseApiTest):
    def test_pasar_a_limpio_registra_hora(self):
        sala = Sala.objects.get(numero="L-12")  # pendiente, con hora antigua
        antes = sala.hora_ultima_limpieza
        r = self.client.patch(f"/api/salas/{sala.id}/", {"estado": "limpio"})
        self.assertEqual(r.status_code, 200)
        sala.refresh_from_db()
        self.assertGreater(sala.hora_ultima_limpieza, antes)

    def test_cliente_no_puede_fijar_la_hora(self):
        sala = Sala.objects.get(numero="L-12")
        antes = sala.hora_ultima_limpieza
        self.client.patch(f"/api/salas/{sala.id}/", {"hora_ultima_limpieza": "2000-01-01T00:00:00Z"})
        sala.refresh_from_db()
        self.assertEqual(sala.hora_ultima_limpieza, antes)

    def test_alternar_trabajador_asigna_y_quita(self):
        sala = Sala.objects.get(numero="L-11")  # trabajadores 1 y 4
        r = self.client.post(f"/api/salas/{sala.id}/alternar-trabajador/", {"trabajador": 2})
        self.assertEqual(r.status_code, 200)
        self.assertIn(2, r.json()["trabajadores"])
        r = self.client.post(f"/api/salas/{sala.id}/alternar-trabajador/", {"trabajador": 2})
        self.assertNotIn(2, r.json()["trabajadores"])

    def test_alternar_trabajador_inexistente(self):
        r = self.client.post("/api/salas/1/alternar-trabajador/", {"trabajador": 999})
        self.assertEqual(r.status_code, 404)

    def test_tope_de_salas_por_trabajador(self):
        trabajador = Trabajador.objects.create(
            nombre="Pedro Soto", rut="10.111.222-3", inicio_turno="08:00", fin_turno="16:00"
        )
        for n in range(MAX_SALAS_POR_TRABAJADOR):
            Sala.objects.create(edificio=self.edificio, numero=f"T-{n}", piso=1).trabajadores.add(trabajador)
        # por el endpoint de asignación
        r = self.client.post("/api/salas/1/alternar-trabajador/", {"trabajador": trabajador.id})
        self.assertEqual(r.status_code, 400)
        # y también al editar la sala con PATCH
        r = self.client.patch("/api/salas/1/", {"trabajadores": [trabajador.id]}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_incidencia_solo_la_reporta_quien_tiene_la_sala(self):
        # trabajador 2 no está asignado a la sala 2 (L-12)
        r = self.client.post("/api/incidencias/", {
            "sala": 2, "trabajador": 2, "descripcion": "Piso mojado en la entrada",
        })
        self.assertEqual(r.status_code, 400)
        r = self.client.post("/api/incidencias/", {
            "sala": 2, "trabajador": 1, "descripcion": "Piso mojado en la entrada",
        })
        self.assertEqual(r.status_code, 201)


class IncidenciaTests(BaseApiTest):
    def test_crear_listar_y_filtrar(self):
        r = self.client.post("/api/incidencias/", {"sala": 3, "descripcion": "Ventana rota"})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()["estado"], "pendiente")
        self.assertEqual(len(self.client.get("/api/incidencias/?sala=3").json()), 1)
        self.assertEqual(len(self.client.get("/api/incidencias/").json()), 2)

    def test_descripcion_muy_corta(self):
        r = self.client.post("/api/incidencias/", {"sala": 3, "descripcion": "ok"})
        self.assertEqual(r.status_code, 400)
        r = self.client.post("/api/incidencias/", {"sala": 3, "descripcion": "     "})
        self.assertEqual(r.status_code, 400)

    def test_sala_inexistente(self):
        r = self.client.post("/api/incidencias/", {"sala": 9999, "descripcion": "Algo pasó aquí"})
        self.assertEqual(r.status_code, 400)

    def test_alternar_estado(self):
        r = self.client.post("/api/incidencias/1/alternar-estado/")
        self.assertEqual(r.json()["estado"], "resuelta")
        r = self.client.post("/api/incidencias/1/alternar-estado/")
        self.assertEqual(r.json()["estado"], "pendiente")

    def test_editar_y_eliminar(self):
        r = self.client.patch("/api/incidencias/1/", {"descripcion": "Falta jabón y papel"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.client.delete("/api/incidencias/1/").status_code, 204)
        self.assertEqual(Incidencia.objects.count(), 0)

    def test_sala_muestra_incidencias_pendientes(self):
        self.assertEqual(self.client.get("/api/salas/2/").json()["incidencias_pendientes"], 1)
        self.client.post("/api/incidencias/1/alternar-estado/")
        self.assertEqual(self.client.get("/api/salas/2/").json()["incidencias_pendientes"], 0)


class TrabajadorTests(BaseApiTest):
    datos = {"nombre": "Pedro Soto", "rut": "10.111.222-3", "inicio_turno": "08:00", "fin_turno": "16:00"}

    def test_listar_incluye_sus_salas(self):
        r = self.client.get("/api/trabajadores/1/")
        self.assertEqual(len(r.json()["salas"]), 10)

    def test_crud(self):
        r = self.client.post("/api/trabajadores/", self.datos)
        self.assertEqual(r.status_code, 201)
        id_nuevo = r.json()["id"]
        r = self.client.patch(f"/api/trabajadores/{id_nuevo}/", {"fin_turno": "17:00"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.client.delete(f"/api/trabajadores/{id_nuevo}/").status_code, 204)

    def test_rut_con_formato_invalido(self):
        r = self.client.post("/api/trabajadores/", {**self.datos, "rut": "123"})
        self.assertEqual(r.status_code, 400)
        self.assertIn("rut", r.json())

    def test_rut_repetido(self):
        r = self.client.post("/api/trabajadores/", {**self.datos, "rut": "12.345.678-9"})
        self.assertEqual(r.status_code, 400)

    def test_turno_fin_antes_del_inicio(self):
        r = self.client.post("/api/trabajadores/", {**self.datos, "inicio_turno": "16:00", "fin_turno": "08:00"})
        self.assertEqual(r.status_code, 400)
        # también al editar solo uno de los dos campos
        r = self.client.patch("/api/trabajadores/1/", {"fin_turno": "07:00"})
        self.assertEqual(r.status_code, 400)

    def test_nombre_muy_corto(self):
        r = self.client.post("/api/trabajadores/", {**self.datos, "nombre": "Al"})
        self.assertEqual(r.status_code, 400)


class EdificioYResumenTests(BaseApiTest):
    def test_crud_edificio(self):
        r = self.client.post("/api/edificios/", {"codigo": "M", "nombre": "Edificio M"})
        self.assertEqual(r.status_code, 201)
        r = self.client.post("/api/edificios/", {"codigo": "M", "nombre": "Repetido"})
        self.assertEqual(r.status_code, 400)  # codigo unico

    def test_resumen(self):
        r = self.client.get("/api/resumen/")
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.assertEqual(d["total_salas"], 29)
        self.assertEqual(d["limpias"] + d["pendientes"] + d["en_proceso"], 29)
        self.assertEqual(d["incidencias_pendientes"], 1)
        self.assertEqual(self.client.get("/api/resumen/?edificio=ZZ").json()["total_salas"], 0)

    def test_resumen_cambia_al_actualizar_una_sala(self):
        antes = self.client.get("/api/resumen/").json()["limpias"]
        sala = Sala.objects.exclude(estado="limpio").first()
        self.client.patch(f"/api/salas/{sala.id}/", {"estado": "limpio"})
        self.assertEqual(self.client.get("/api/resumen/").json()["limpias"], antes + 1)