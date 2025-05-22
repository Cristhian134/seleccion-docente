from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render
from django.http import JsonResponse

from core_apps.protegido.crear_convocatoria.utils import convocatoria_externa_obtener_datos_profesor, crear_convocatoria
from core_apps.common.models import Curso, Docente, TipoPlaza
from .forms import ConvocatoriaExternaForm

import json


@login_required
def crear_convocatoria_view(request):
  return render(request, 'crear_convocatoria.html', {
    "url_volver": "/home"
  })


@login_required
def crear_convocatoria_interna_view(request):
  context = {
    "url_volver": "/crear-convocatoria/"
  }

  if request.method == 'GET':
    dni = request.GET.get('cod_profesor', '').strip()

    if dni.isdigit() and int(dni) > 0:
      pass
    else:
      context["error_busqueda"] = "El codigo debe ser un numero entero mayor o igual a 1"
      return render(request, 'crear_convocatoria_interna.html', context)

    if not dni:
      context["error_busqueda"] = "Codigo no proporcionado"
    else:
      profesor = Docente.objects.get(id=dni)
      print(profesor.id, "ssssssss")
      if profesor:
        data = convocatoria_externa_obtener_datos_profesor(dni)
        context["data"] = data
      else:
        context["error_db"] = f"No se encontró un docente con el Codigo {dni}"

    return render(request, 'crear_convocatoria_interna.html', context)

  if request.method == 'POST':
    return render(request, 'crear_convocatoria_interna.html', {
      "url_volver": "/crear-convocatoria/"
    })

  return render(request, 'crear_convocatoria_interna.html', {
    "url_volver": "/crear-convocatoria/"
  })


@login_required
def crear_convocatoria_externa_view(request):
  user = getattr(request, 'user', AnonymousUser())
  facultad = getattr(user, "facultad", None)

  cursos = Curso.objects.prefetch_related('seccion_set').all().filter(facultad=facultad).prefetch_related(
    'seccion_set__horario_set'
  )
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
