from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from openpyxl.utils import get_column_letter
import openpyxl

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render
from django.http import HttpResponse
from reportlab.lib import colors
from django.shortcuts import redirect
from django.db.models import Q
from django.db.models import F
from reportlab.platypus import Table, TableStyle

from core_apps.common.models import Curso, Docente, EvaluacionDocente
from .utils import formatear_docentes


@login_required
def listar_docentes_view(request):
  cursos = Curso.objects.prefetch_related('seccion_set').distinct("nombreCurso")
  codigo_curso = request.GET.get("cod_curso")

  evaluaciones = EvaluacionDocente.objects.select_related(
    'docente__persona',     # para obtener los datos de persona
    'seccion__curso'        # para obtener los datos del curso
  )

  if codigo_curso:
    evaluaciones_filtradas = evaluaciones.filter(
      Q(seccion__curso__codigoCurso__icontains=codigo_curso) |
      Q(seccion__curso__nombreCurso__icontains=codigo_curso)
    )

    if len(evaluaciones_filtradas) == 0:
      return render(request, 'listar_docentes.html', {
        "url_volver": "/home",
        "docentes": [],
        "cursos": cursos,
        "mensaje": f'No hay docentes para la búsqueda de "{codigo_curso}"'
      })

    evaluaciones = list(evaluaciones_filtradas.order_by(F('notaEvaluacion').desc(nulls_last=True))[:5])
    evaluaciones_aux = list(evaluaciones_filtradas.order_by('-notaEvaluacion')[:5])

    if len(evaluaciones) > 2 and evaluaciones_aux[0].notaEvaluacion is None and evaluaciones_aux[0].docente.id != evaluaciones[len(evaluaciones) - 2].docente.id:
      evaluaciones[len(evaluaciones) - 1] = evaluaciones_aux[0]

    docentes = formatear_docentes(evaluaciones)
    curso = Curso.objects.filter(codigoCurso=codigo_curso).first()

    if len(evaluaciones) == 0:
      return render(request, 'listar_docentes.html', {
        "url_volver": "/home",
        "docentes": [],
        "cursos": cursos,
        "mensaje": f'No hay docentes para la búsqueda de "{codigo_curso}"'
      })

    titulo = None
    if curso:
      titulo = curso.nombreCurso.capitalize()

    return render(request, 'listar_docentes.html', {
      "url_volver": "/home",
      "docentes": docentes,
      "cursos": cursos,
      "titulo": titulo
    })

  return render(request, 'listar_docentes.html', {
    "url_volver": "/home",
    "docentes": [],
    "cursos": cursos,
    "mensaje": "Debe buscar un curso."
  })


@login_required
def exportar_docentes_pdf(request):
  codigo_curso = request.GET.get("cod_curso")
  evaluaciones = EvaluacionDocente.objects.select_related(
      'docente__persona', 'seccion__curso'
  )

  if not codigo_curso:
    return redirect('listar-docentes')

  evaluaciones_filtradas = evaluaciones.filter(
    Q(seccion__curso__codigoCurso__icontains=codigo_curso) |
    Q(seccion__curso__nombreCurso__icontains=codigo_curso)
  )

  if len(evaluaciones_filtradas) == 0:
    return redirect(f'/listar-docentes/?cod_curso_display={codigo_curso}&cod_curso={codigo_curso}')

  evaluaciones = list(evaluaciones_filtradas.order_by(F('notaEvaluacion').desc(nulls_last=True))[:5])
  evaluaciones_aux = list(evaluaciones_filtradas.order_by('-notaEvaluacion')[:5])

  if len(evaluaciones) > 2 and evaluaciones_aux[0].notaEvaluacion is None and evaluaciones_aux[0].docente.id != evaluaciones[len(evaluaciones) - 2].docente.id:
    evaluaciones[len(evaluaciones) - 1] = evaluaciones_aux[0]

  docentes = formatear_docentes(evaluaciones)

  response = HttpResponse(content_type='application/pdf')
  response['Content-Disposition'] = 'attachment; filename="docentes.pdf"'

  p = canvas.Canvas(response, pagesize=landscape(A4))
  width, height = landscape(A4)

  # Título
  p.setFont("Helvetica-Bold", 16)
  p.drawString(30, height - 40, "Lista de Docentes")  # Menor espacio con tabla

  # Datos
  data = [["Cod", "Apellidos", "Nombres", "Facultad", "Curso", "Nota"]]

  for d in docentes:
    data.append([
      d["id"], d["apellidos"], d["nombres"],
      d["facultad"], d["curso"],
      "--" if d["notaEvaluacion"] is None else d["notaEvaluacion"]
    ])

  # Definir proporciones más amplias para Nombres, Facultad y Curso
  colWidths = [50, 90, 90, 250, 250, 50]  # Suma aprox: 600 (ancho A4 horizontal útil)

  table = Table(data, colWidths=colWidths)
  style = TableStyle([
      ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#CCCCCC")),
      ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
      ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
      ('ALIGN', (2, 1), (4, -1), 'LEFT'),
      ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
      ('WORDWRAP', (0, 0), (-1, -1), 'CJK'),
      ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
      ('FONTSIZE', (0, 0), (-1, -1), 9),
      ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
      ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
  ])
  table.setStyle(style)

  # Posición de la tabla (más arriba)
  table_width, table_height = table.wrapOn(p, width, height)
  table.drawOn(p, 30, height - 50 - table_height)  # espacio reducido

  p.showPage()
  p.save()
  return response


@login_required
def exportar_docentes_excel(request):
  codigo_curso = request.GET.get("cod_curso")
  evaluaciones = EvaluacionDocente.objects.select_related(
      'docente__persona', 'seccion__curso'
  )
  if not codigo_curso:
    return redirect('listar-docentes')

  evaluaciones_filtradas = evaluaciones.filter(
    Q(seccion__curso__codigoCurso__icontains=codigo_curso) |
    Q(seccion__curso__nombreCurso__icontains=codigo_curso)
  )

  if len(evaluaciones_filtradas) == 0:
    return redirect(f'/listar-docentes/?cod_curso_display={codigo_curso}&cod_curso={codigo_curso}')

  evaluaciones = list(evaluaciones_filtradas.order_by(F('notaEvaluacion').desc(nulls_last=True))[:5])
  evaluaciones_aux = list(evaluaciones_filtradas.order_by('-notaEvaluacion')[:5])

  if len(evaluaciones) > 2 and evaluaciones_aux[0].notaEvaluacion is None and evaluaciones_aux[0].docente.id != evaluaciones[len(evaluaciones) - 2].docente.id:
    evaluaciones[len(evaluaciones) - 1] = evaluaciones_aux[0]

  docentes = formatear_docentes(evaluaciones)

  wb = openpyxl.Workbook()
  ws = wb.active
  ws.title = "Docentes"

  headers = ["Cod", "Apellidos", "Nombres", "Facultad", "Curso", "Nota"]
  ws.append(headers)

  for docente in docentes:
    ws.append([
        docente["id"],
        docente["apellidos"],
        docente["nombres"],
        docente["facultad"],
        docente["curso"],
        docente["notaEvaluacion"]
    ])

  response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
  response["Content-Disposition"] = 'attachment; filename=docentes.xlsx'
  wb.save(response)
  return response
