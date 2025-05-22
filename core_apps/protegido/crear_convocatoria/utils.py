
from django.utils.timezone import now

from core_apps.common.models import Convocatoria, Docente, EstadoConvocatoria, EstadoPlaza, EstadoSeccion, EvaluacionDocente, Plaza, Requisito, Seccion

# cursos_list
# [
#   {
#     'curso': 'BIC01-U',
#     'requisitos': ['sas', 'das', 'dasd'],
#     'tipo': 'laboratorio', 'horas': 4
#   }
# ]


def crear_modelo_convocatoria(cleaned_data):
  print(cleaned_data)

  return Convocatoria.objects.create(
      descripcionConvocatoria=cleaned_data["descripcionConvocatoria"],
      tipoConvocatoria="externa",
      fechaPublicacion=now(),
      fechaCierre=cleaned_data["fechaCierre"],
      fechaAsignacionTema=cleaned_data["fechaAsignacionTema"],
      fechaClaseMagistral=cleaned_data["fechaClaseMagistral"],
      estadoConvocatoria=EstadoConvocatoria.ACTIVO,
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
            vigencia="actual"  # Puedes cambiarlo luego si quieres
        )

    except Seccion.DoesNotExist:
      print(f"⚠️ No se encontró la sección {curso['curso']}")
      return "Error al crear la convocaotoria", False
    except Exception as e:
      print(f"❌ Error al procesar curso {curso['curso']}: {e}")
      return "Error al crear la convocaotoria", False

  return "Convocatoria creada correctamente", True


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
