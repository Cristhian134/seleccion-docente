
from django.utils.timezone import now, make_aware

from core_apps.common.models import ClaseMagistral, Convocatoria, Docente, EstadoClaseMagistral, EstadoConvocatoria, EstadoPlaza, EstadoPostulante, EstadoSeccion, EvaluacionDocente, Persona, Plaza, Postulante, Requisito, Seccion, TipoConvocatoria, TipoPlaza

from datetime import datetime, timedelta

# cursos_list
# [
#   {
#     'curso': 'BIC01-U',
#     'requisitos': ['sas', 'das', 'dasd'],
#     'tipo': 'laboratorio', 'horas': 4
#   }
# ]


def crear_modelo_convocatoria(cleaned_data, tipo=TipoConvocatoria.EXTERNA, fechaPublicacion=now()):
  return Convocatoria.objects.create(
      descripcionConvocatoria=cleaned_data["descripcionConvocatoria"],
      tipoConvocatoria=tipo,
      fechaPublicacion=fechaPublicacion,
      fechaCierre=cleaned_data["fechaCierre"],
      fechaAsignacionTema=cleaned_data["fechaAsignacionTema"],
      fechaClaseMagistral=cleaned_data["fechaClaseMagistral"],
      estadoConvocatoria=EstadoConvocatoria.PUBLICADO,
  )


def crear_convocatoria(cleaned_data, cursos_list):
  convocatoria = crear_modelo_convocatoria(cleaned_data)

  for curso in cursos_list:
    try:
      # "BIC01-U" → curso_cod = "BIC01", seccion_cod = "U"
      cod_curso, cod_seccion = curso["curso"].strip().split("-")

      # Buscar sección activa
      seccion = Seccion.objects.select_related("curso").get(
          curso__codigoCurso=cod_curso,
          codigoSeccion=cod_seccion,
          estadoSeccion=EstadoSeccion.ACTIVO,
      )

      # Crear plaza
      plaza = Plaza.objects.create(
          convocatoria=convocatoria,
          seccion=seccion,
          estadoPlaza=EstadoPlaza.ACTIVO,
          tipoPlaza=curso["tipo"]
      )

      # Crear requisitos
      for req in curso["requisitos"]:
        Requisito.objects.create(
            plaza=plaza,
            descripcion=req,
            vigencia="actual"
        )

    except Seccion.DoesNotExist:
      print(f"⚠️ No se encontró la sección {curso['curso']}")
      return "Error al crear la convocaotoria", False
    except Exception as e:
      print(f"❌ Error al procesar curso {curso['curso']}: {e}")
      return "Error al crear la convocaotoria", False

  return "Convocatoria creada correctamente", True


def crear_convocatoria_interna(cod_profesor, tema, fecha, hora, seccion_id, tipo_plaza):
  naive_dt = datetime.strptime(f"{fecha}T{hora}", "%Y-%m-%dT%H:%M")
  aware_dt = make_aware(naive_dt)  # Usa la zona horaria por defecto de Django
  fecha_cierre = aware_dt + timedelta(hours=1)

  cleaned_data = {
    "descripcionConvocatoria": "",
    "fechaCierre": fecha_cierre,
    "fechaAsignacionTema": aware_dt,
    "fechaClaseMagistral": aware_dt,
  }
  convocatoria = crear_modelo_convocatoria(cleaned_data, tipo=TipoConvocatoria.INTERNA, fechaPublicacion=aware_dt)

  seccion = Seccion.objects.get(id=seccion_id)
  Plaza.objects.create(
    convocatoria=convocatoria,
    seccion=seccion,
    estadoPlaza=EstadoPlaza.ACTIVO,
    tipoPlaza=tipo_plaza,
  )

  persona = Docente.objects.get(id=cod_profesor).persona

  postulante = Postulante.objects.create(
    persona=persona,
    convocatoria=convocatoria,
    estadoPostulante=EstadoPostulante.ACEPTADO
  )

  ClaseMagistral.objects.create(
    postulante=postulante,
    fechaProgramacion=fecha,
    horaProgramada=hora,
    temaAsignado=tema,
    estadoClaseMagistral=EstadoClaseMagistral.PROGRAMADO
  )

  return


def convocatoria_externa_obtener_datos_profesor(dni):
  try:
    docente = Docente.objects.select_related("persona").get(id=dni)
  except Docente.DoesNotExist:
    return False

  persona = docente.persona
  evaluaciones = EvaluacionDocente.objects.select_related("seccion__curso").filter(docente=docente)

  cursos_por_facultad = {}
  cursos_vistos = {}

  for evaluacion in evaluaciones:
    curso = evaluacion.seccion.curso
    facultad = curso.get_facultad_display()

    if facultad not in cursos_por_facultad:
      cursos_por_facultad[facultad] = []
      cursos_vistos[facultad] = set()

    if curso.codigoCurso not in cursos_vistos[facultad]:
      cursos_por_facultad[facultad].append({
          "codigo": curso.codigoCurso,
          "nombre": curso.nombreCurso,
      })
      cursos_vistos[facultad].add(curso.codigoCurso)

  cursos_final = [
      {
          "facultad": facultad,
          "cursos": cursos
      }
      for facultad, cursos in cursos_por_facultad.items()
  ]

  return {
      "nombre": persona.nombre,
      "codigo": docente.id,
      "apellido_paterno": persona.apellidoPaterno,
      "apellido_materno": persona.apellidoMaterno,
      "dni": persona.dni,
      "email_uni": persona.correo,
      "cursos": cursos_final
  }
