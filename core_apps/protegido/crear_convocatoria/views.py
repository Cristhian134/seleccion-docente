from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from core_apps.protegido.crear_convocatoria.utils import crear_convocatoria
from core_apps.common.models import Curso, TipoPlaza
from .forms import ConvocatoriaExternaForm

import json


@login_required
def crear_convocatoria_view(request):
  return render(request, 'crear_convocatoria.html', {
    "url_volver": "/home"
  })


@login_required
def crear_convocatoria_interna_view(request):
  return render(request, 'crear_convocatoria_interna.html', {
    "url_volver": "/crear-convocatoria/"
  })


@login_required
def crear_convocatoria_externa_view(request):
  cursos = Curso.objects.prefetch_related('seccion_set').all()
  tipo_plazas = TipoPlaza.choices

  if request.method == 'POST':
    form = ConvocatoriaExternaForm(request.POST)
    print("Validando formulario")
    if form.is_valid():
      # form.save()

      cursos_json = request.POST.get("cursos_json", "[]")
      try:
        cursos_list = json.loads(cursos_json)
      except json.JSONDecodeError:
        cursos_list = []
        print("Error al parsear cursos_json")

      print("cursos_list", cursos_list)

      mensaje, exito = crear_convocatoria(form.cleaned_data, cursos_list)
      print("Datos del formulario recibidos:")
      for campo, valor in form.cleaned_data.items():
        print(f"{campo}: {valor}")
      return render(
        request,
        'crear_convocatoria_externa.html',
        {
          'form': form,
          'cursos': cursos,
          'tipo_plazas': tipo_plazas,
          "url_volver": "/crear-convocatoria/",
          "mensaje": {
            "descripcion": mensaje,
            "exito": exito,
          }
        }
      )
  else:
    form = ConvocatoriaExternaForm()

  return render(
    request,
    'crear_convocatoria_externa.html',
    {
      'form': form,
      'cursos': cursos,
      'tipo_plazas': tipo_plazas,
      "url_volver": "/crear-convocatoria/"
    }
  )
