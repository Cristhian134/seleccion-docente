def formatear_docentes(evaluaciones):
  docentes_formateados = []

  for evaluacion in evaluaciones:

    docentes_formateados.append({
      "id": evaluacion.docente.id,
      "nombres": evaluacion.docente.persona.nombre,
      "apellidos": f"{evaluacion.docente.persona.apellidoPaterno} {evaluacion.docente.persona.apellidoMaterno}",
      "facultad": evaluacion.seccion.curso.facultad,
      "curso": evaluacion.seccion.curso.nombreCurso,
      "notaEvaluacion": evaluacion.notaEvaluacion,
    })

  return docentes_formateados
