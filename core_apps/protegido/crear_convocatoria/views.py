import random
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render
from django.http import JsonResponse

from core_apps.protegido.crear_convocatoria.utils import convocatoria_externa_obtener_datos_profesor, crear_convocatoria
from core_apps.common.models import Curso, Docente, Seccion, Temas, TipoPlaza
from .forms import ConvocatoriaExternaForm
from .utils import crear_convocatoria_interna

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
    codigo = request.GET.get('cod_profesor', '').strip()
    sortear_tema = request.GET.get('sortear_tema') == 'true'

    if not codigo:
      return render(request, 'crear_convocatoria_interna.html', context)

    user = getattr(request, 'user', AnonymousUser())
    facultad = getattr(user, "facultad", None)

    tipo_plazas = TipoPlaza.choices
    cursos = Curso.objects.prefetch_related('seccion_set').all().filter(facultad=facultad)

    if codigo.isdigit() and int(codigo) > 0:
      pass
    else:
      context["error_busqueda"] = "El codigo debe ser un numero entero mayor o igual a 1"
      return render(request, 'crear_convocatoria_interna.html', context)

    if not codigo:
      context["error_busqueda"] = "Codigo no proporcionado"
    else:

      try:
        profesor = Docente.objects.get(id=codigo)
        data = convocatoria_externa_obtener_datos_profesor(codigo)
        context["data"] = data
        context["cod_profesor"] = codigo
      except Docente.DoesNotExist:
        context["error_db"] = f"No se encontró un docente con el código {codigo}"
        return render(request, 'crear_convocatoria_interna.html', context)

    if sortear_tema:
      seccion_seleccionada = request.GET.get("curso_seleccionado")

      if not seccion_seleccionada:
        context["error_busqueda"] = "Debe seleccionar un curso para sortear un tema"
      else:
        seccion = Seccion.objects.get(id=seccion_seleccionada)
        curso_seleccionado = seccion.curso.codigoCurso

        secciones = Seccion.objects.filter(curso__codigoCurso=curso_seleccionado)
        temas_disponibles = Temas.objects.filter(silabus__curso__seccion__in=secciones)
        tema_asignado = random.choice(list(temas_disponibles)) if temas_disponibles.exists() else None
        context["curso_sorteado"] = tema_asignado.nombreTema

    context["cursos"] = cursos
    context["tipo_plazas"] = tipo_plazas

    return render(request, 'crear_convocatoria_interna.html', context)

  if request.method == 'POST':
    cod_profesor = request.POST.get("cod_profesor")
    tema = request.POST.get("tema")
    fecha = request.POST.get("fecha")
    hora = request.POST.get("hora")
    seccion_id = request.POST.get("seccion_id")
    tipo_plaza = request.POST.get("tipoPlaza")

    crear_convocatoria_interna(cod_profesor, tema, fecha, hora, seccion_id, tipo_plaza)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
      return JsonResponse({"success": True, "mensaje": "Clase magistral creada exitosamente"})

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
