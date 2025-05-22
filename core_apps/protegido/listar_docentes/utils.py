def formatear_docentes(evaluaciones):
  docentes_formateados = []

  for evaluacion in evaluaciones:

    curso_nombre = f'{evaluacion.seccion.curso.codigoCurso}-{evaluacion.seccion.curso.nombreCurso}'

    limite = 44
    if len(curso_nombre) > limite:
      curso_nombre = curso_nombre[:limite]

    docentes_formateados.append({
      "id": evaluacion.docente.id,
      "nombres": evaluacion.docente.persona.nombre,
      "apellidos": f"{evaluacion.docente.persona.apellidoPaterno} {evaluacion.docente.persona.apellidoMaterno}",
      "facultad": evaluacion.seccion.curso.facultad,
      "curso": curso_nombre,
      "notaEvaluacion": evaluacion.notaEvaluacion,
    })

  return docentes_formateados
