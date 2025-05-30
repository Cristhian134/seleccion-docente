from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from core_apps.common.models import (
    Convocatoria, Plaza, Requisito,
    TipoConvocatoria, EstadoConvocatoria,
    TipoPlaza, EstadoPlaza, Seccion
)
from datetime import datetime, timedelta


CONVOCATORIAS_MOCK = []

descripcion = (
    "Del viernes 22 de marzo hasta el día 26 de marzo a las 15:00 hrs al Correo de la Oficina "
    "de MESA DE PARTES de la Facultad de Ingeniería Industrial y de Sistemas mesadepartesfiis@uni.edu.pe\n\n"
    "Documentos:\n"
    "a. Currículo Vitae documentado\n"
    "b. Copia del Título Legalizado o Autenticado\n"
    "c. Solicitud dirigida a la Decana FIIS"
)

# Fecha base
base_date = datetime(2025, 3, 22, 10, 0)

TOTAL_CONVOCATORIAS = 14

for i in range(14):
  # Creamos fechas naive
  pub_naive = base_date + timedelta(days=i * 2)
  cierre_naive = pub_naive + timedelta(days=2)
  asignacion_naive = cierre_naive + timedelta(days=1)
  clase_naive = asignacion_naive + timedelta(days=2)

  # Convertimos cada una a aware SOLO UNA VEZ
  fecha_pub = make_aware(pub_naive)
  fecha_cierre = make_aware(cierre_naive)
  fecha_asignacion = make_aware(asignacion_naive)
  fecha_clase = make_aware(clase_naive)

  CONVOCATORIAS_MOCK.append({
      "descripcionConvocatoria": f"CONVOCATORIA DOCENTE - {descripcion}",
      "tipoConvocatoria": TipoConvocatoria.EXTERNA,
      "fechaPublicacion": fecha_pub,
      "fechaCierre": fecha_cierre,
      "fechaAsignacionTema": fecha_asignacion,
      "fechaClaseMagistral": fecha_clase,
      "estadoConvocatoria": EstadoConvocatoria.PUBLICADO,
      "plazas": [
          {
              "estadoPlaza": EstadoPlaza.ACTIVO,
              "tipoPlaza": TipoPlaza.PRACTICA,
              "requisitos": [
                  {
                      "descripcion": "Experiencia práctica en el área",
                      "vigencia": "actual",
                  }
              ]
          },
          {
              "estadoPlaza": EstadoPlaza.ACTIVO,
              "tipoPlaza": TipoPlaza.TEORIA,
              "requisitos": [
                  {
                      "descripcion": "Conocimientos teóricos sólidos",
                      "vigencia": "actual",
                  }
              ]
          },
      ]
  })


class Command(BaseCommand):
  help = 'Carga convocatorias de prueba usando las primeras 14 secciones existentes.'

  def handle(self, *args, **options):
    secciones = Seccion.objects.select_related("curso").all()[:TOTAL_CONVOCATORIAS]

    if len(secciones) < TOTAL_CONVOCATORIAS:
      self.stdout.write(self.style.WARNING('No hay suficientes secciones (mínimo 14 requeridas).'))
      return

    for data, seccion in zip(CONVOCATORIAS_MOCK, secciones):
      descripcion_final = f"{seccion.curso.nombreCurso.upper()} - SECCIÓN {seccion.codigoSeccion} - {data['descripcionConvocatoria']}"

      convocatoria = Convocatoria.objects.create(
          descripcionConvocatoria=descripcion_final,
          tipoConvocatoria=data["tipoConvocatoria"],
          fechaPublicacion=data["fechaPublicacion"],
          fechaCierre=data["fechaCierre"],
          fechaAsignacionTema=data["fechaAsignacionTema"],
          fechaClaseMagistral=data["fechaClaseMagistral"],
          estadoConvocatoria=data["estadoConvocatoria"],
      )

      for plaza_data in data["plazas"]:
        plaza = Plaza.objects.create(
            convocatoria=convocatoria,
            seccion=seccion,
            estadoPlaza=plaza_data["estadoPlaza"],
            tipoPlaza=plaza_data["tipoPlaza"]
        )
        for req in plaza_data["requisitos"]:
          Requisito.objects.create(
              plaza=plaza,
              descripcion=req["descripcion"],
              vigencia=req["vigencia"]
          )

      self.stdout.write(self.style.SUCCESS(f"Convocatoria creada para sección: {seccion.curso.nombreCurso} - {seccion.codigoSeccion}"))

    self.stdout.write(self.style.SUCCESS("Proceso completado: se crearon todas las convocatorias mock."))
