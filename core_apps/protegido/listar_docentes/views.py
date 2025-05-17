from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from openpyxl.utils import get_column_letter
import openpyxl

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from reportlab.lib import colors
from django.shortcuts import redirect
from reportlab.platypus import Table, TableStyle

from core_apps.common.models import Curso, Docente, EvaluacionDocente
from .utils import formatear_docentes


@login_required
def listar_docentes_view(request):
  cursos = Curso.objects.prefetch_related('seccion_set').all()
  codigo_curso = request.GET.get("cod_curso")

  evaluaciones = EvaluacionDocente.objects.select_related(
    'docente__persona',     # para obtener los datos de persona
    'seccion__curso'        # para obtener los datos del curso
  )

  if codigo_curso:
    evaluaciones = evaluaciones.filter(seccion__curso__codigoCurso=codigo_curso)
    docentes = formatear_docentes(evaluaciones)

    return render(request, 'listar_docentes.html', {
      "url_volver": "/home",
      "docentes": docentes,
      "cursos": cursos,
    })

  return render(request, 'listar_docentes.html', {
    "url_volver": "/home",
    "docentes": [],
    "cursos": cursos,
    "mensaje": "Debe seleccionar un curso."
  })


@login_required
def exportar_docentes_pdf(request):
  codigo_curso = request.GET.get("cod_curso")
  evaluaciones = EvaluacionDocente.objects.select_related(
      'docente__persona', 'seccion__curso'
  )
  if not codigo_curso:
    return redirect('listar-docentes')

  evaluaciones = evaluaciones.filter(seccion__curso__codigoCurso=codigo_curso) \
      .order_by('-notaEvaluacion')[:5]

  docentes = formatear_docentes(evaluaciones)

  response = HttpResponse(content_type='application/pdf')
  response['Content-Disposition'] = 'attachment; filename="docentes.pdf"'

  p = canvas.Canvas(response, pagesize=landscape(A4))
  width, height = landscape(A4)
  p.setFont("Helvetica-Bold", 16)
  p.drawString(50, height - 50, "Lista de Docentes")

  data = [["Cod", "Apellido", "Nombres", "Facultad", "Curso", "Nota"]]
  for d in docentes:
    data.append([
        d["id"], d["apellidos"], d["nombres"],
        d["facultad"], d["curso"], d["notaEvaluacion"]
    ])

  table = Table(data, colWidths=[60, 100, 100, 100, 100, 60])
  style = TableStyle([
      ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#003366")),
      ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
      ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
      ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
      ('FONTSIZE', (0, 0), (-1, -1), 9),
      ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
      ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
  ])
  table.setStyle(style)

  table_width, table_height = table.wrapOn(p, width, height)
  table.drawOn(p, 30, height - 100 - table_height)

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

  evaluaciones = evaluaciones.filter(seccion__curso__codigoCurso=codigo_curso) \
      .order_by('-notaEvaluacion')[:5]

  docentes = formatear_docentes(evaluaciones)

  wb = openpyxl.Workbook()
  ws = wb.active
  ws.title = "Docentes"

  headers = ["Cod", "Apellido", "Nombres", "Facultad", "Curso", "Nota"]
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
