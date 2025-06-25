from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from core_apps.common.models import (
    Convocatoria, Documento, Postulante, EstadoDocumento, Persona, ClaseMagistral, Usuario, Evaluador, NotaPostulante, EstadoNotaPostulante, EstadoPostulante,
    EstadoClaseMagistral, Plaza, Temas, Seccion, EstadoPostulante, EstadoConvocatoria  
)
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, Http404, JsonResponse, HttpResponseForbidden
from django.urls import reverse
from django.contrib import messages
from django.core.files.uploadedfile import UploadedFile
from django.db.models import Sum, F, FloatField
from io import BytesIO
import mimetypes
from datetime import datetime, timedelta
from xhtml2pdf import pisa
from django.template.loader import render_to_string, get_template
from django.utils.timezone import make_aware
from datetime import datetime, time, timedelta
from django.db import transaction


import random


@login_required
def ver_convocatorias(request):
  user = getattr(request, 'user', AnonymousUser())
  facultad = getattr(user, "facultad", None)

  if request.method == "POST":
    convocatoria_id = request.POST.get("convocatoria_id")
    accion = request.POST.get("accion")

    if not convocatoria_id:

      return render(request, 'ver_convocatorias.html', {
          "convocatorias": Convocatoria.objects.all(),
          "error": "Debe seleccionar una convocatoria.",
          "url_volver": "/home"
      })

    if accion == "documentos":
      return redirect('gestionar_documentos', convocatoria_id=convocatoria_id)
    elif accion == "calificacion":
      return redirect('dirigir_calificacion', convocatoria_id=convocatoria_id)

  query = request.GET.get('q')
  convocatorias = Convocatoria.objects.filter(
      plaza__seccion__curso__facultad=facultad
  ).distinct()

  if query:
    convocatorias = convocatorias.filter(
        plaza__seccion__curso__nombreCurso__icontains=query
    )

  for convocatoria in convocatorias:
    primer_curso = None
    for plaza in Plaza.objects.filter(convocatoria=convocatoria).select_related('seccion__curso'):
      if plaza.seccion and plaza.seccion.curso:
        primer_curso = plaza.seccion.curso
        break
    convocatoria.curso = primer_curso

  return render(request, 'ver_convocatorias.html', {
      "convocatorias": convocatorias,
      "url_volver": "/home",
  })


@login_required
def convocatoria_gestionar_documentos(request, convocatoria_id):
  convocatoria = get_object_or_404(Convocatoria, id=convocatoria_id)
  postulantes = Postulante.objects.filter(convocatoria=convocatoria).select_related("persona")
  postulantes = Postulante.objects.filter(convocatoria=convocatoria).prefetch_related('documento_set')

  for postulante in postulantes:
    doc = postulante.documento_set.order_by("fechaRecepcion").first()
    postulante.fecha_documento_mas_antiguo = doc.fechaRecepcion if doc else None

    postulante.documentos_json = [
        {
            "tipoDocumento": d.tipoDocumento,
            "fechaRecepcion": d.fechaRecepcion.strftime("%Y-%m-%d"),
            "url": reverse('ver_documento', args=[d.id])
        }
        for d in postulante.documento_set.all()
    ]

  """if request.method == "POST" and "eliminar" in request.POST:
    postulante_id = request.POST.get("postulante_id")
    postulante = get_object_or_404(Postulante, id=postulante_id)
    postulante.delete()
    return redirect('gestionar_documentos/', convocatoria_id=convocatoria_id)"""
  
  if request.method == "POST" and "eliminar" in request.POST:
    postulante_id = request.POST.get("postulante_id")
    if not postulante_id:
        messages.error(request, "Debe seleccionar un postulante para eliminar.")
    else:
        postulante = get_object_or_404(Postulante, id=postulante_id)
        postulante.delete()
        messages.success(request, "Postulante eliminado correctamente.")
    return redirect("gestionar_documentos", convocatoria_id=convocatoria_id)

  if request.method == "POST" and "accion_documentos" in request.POST:
    postulante_id = request.POST.get("postulante_id")
    accion = request.POST.get("accion_documentos")

    postulante = get_object_or_404(Postulante, id=postulante_id)
    documentos = Documento.objects.filter(postulante=postulante)

    if accion == "aceptar":
      documentos.update(estadoDocumento=EstadoDocumento.ACEPTADO)
      postulante.estadoPostulante = EstadoPostulante.ACEPTADO
    elif accion == "rechazar":
      documentos.update(estadoDocumento=EstadoDocumento.RECHAZADO)
      postulante.estadoPostulante = EstadoPostulante.RECHAZADO

    postulante.save()
    return redirect('gestionar_documentos', convocatoria_id=convocatoria_id)

  return render(request, 'gestionar_documentos.html', {
      "convocatoria": convocatoria,
      "postulantes": postulantes,
      "url_volver": "/ver_convocatorias/"
  })


'''
@login_required
def agregar_postulante(request, convocatoria_id):
  convocatoria = get_object_or_404(Convocatoria, id=convocatoria_id)

  if request.method == "POST":
    nombre = request.POST.get("nombre")
    apellido_paterno = request.POST.get("apellidoPaterno")
    apellido_materno = request.POST.get("apellidoMaterno")
    tipo_documento = request.POST.get("tipoDocumento")
    archivo: UploadedFile = request.FILES.get("archivo")

    if not archivo:
      messages.error(request, "Debe subir un archivo.")
      return redirect(request.path)

    # Validar tipo MIME (solo pdf o imagen)
    mime_type, _ = mimetypes.guess_type(archivo.name)
    if mime_type not in ["application/pdf", "image/png", "image/jpeg"]:
      messages.error(request, "Formato de archivo no permitido. Solo PDF o imágenes.")
      return redirect(request.path)

    # Buscar o crear Persona
    persona, _ = Persona.objects.get_or_create(
        nombre=nombre,
        apellidoPaterno=apellido_paterno,
        apellidoMaterno=apellido_materno,
        defaults={
            "dni": "00000000",  # Ajustar o solicitar en formulario real
            "correo": "sin@email.com",
            "telefono": "000000000",
            "genero": "otro",
        }
    )

    # Crear Postulante
    postulante, _ = Postulante.objects.get_or_create(
        persona=persona,
        convocatoria=convocatoria,
        defaults={"estadoPostulante": EstadoPostulante.REGISTRADO}
    )

    # Crear Documento asociado
    Documento.objects.create(
        postulante=postulante,
        tipoDocumento=tipo_documento,
        archivo=archivo.read(),  # Guarda binario
        fechaRecepcion=timezone.now(),
        estadoDocumento=EstadoDocumento.REGISTRADO
    )

    archivos = request.FILES.getlist("archivos")
    for archivo in archivos:
      Documento.objects.create(
          postulante=postulante,
          tipoDocumento=tipo_documento,  # o uno por archivo si tu HTML lo permite
          archivo=archivo.read(),
          fechaRecepcion=timezone.now(),
          estadoDocumento=EstadoDocumento.REGISTRADO
      )

    messages.success(request, "Postulante y documento agregados correctamente.")
    return redirect("gestionar_documentos", convocatoria_id=convocatoria.id)

    return render(request, "agregar_postulante.html", {
        "convocatoria": convocatoria
    })'''


@login_required
def agregar_postulante(request, convocatoria_id):
  convocatoria = get_object_or_404(Convocatoria, id=convocatoria_id)

  with transaction.atomic():
    convocatoria.estadoConvocatoria = EstadoConvocatoria.EN_PROCESO
    convocatoria.save()

  if request.method == "POST":
    nombre = request.POST.get("nombre")
    apellido_paterno = request.POST.get("apellidoPaterno")
    apellido_materno = request.POST.get("apellidoMaterno")
    tipo_documento = request.POST.get("tipoDocumento")
    dni = request.POST.get("dni")
    correo = request.POST.get("correo")
    telefono = request.POST.get("telefono")
    genero = request.POST.get("genero")

    archivo: UploadedFile = request.FILES.get("archivo")

    if not archivo:
      messages.error(request, "Debe subir un archivo.")
      return redirect(request.path)

    mime_type, _ = mimetypes.guess_type(archivo.name)
    if mime_type not in ["application/pdf", "image/png", "image/jpeg"]:
      messages.error(request, "Formato de archivo no permitido. Solo PDF o imágenes.")
      return redirect(request.path)

    # Buscar o crear Persona por DNI
    persona, creada = Persona.objects.get_or_create(
        dni=dni,
        defaults={
            "nombre": nombre,
            "apellidoPaterno": apellido_paterno,
            "apellidoMaterno": apellido_materno,
            "correo": correo,
            "telefono": telefono,
            "genero": genero,
        }
    )

    # Si la persona existe pero no está asociada a este postulante
    postulante, _ = Postulante.objects.get_or_create(
        persona=persona,
        convocatoria=convocatoria,
        defaults={"estadoPostulante": EstadoPostulante.REGISTRADO}
    )

    # Documento principal
    Documento.objects.create(
        postulante=postulante,
        tipoDocumento=tipo_documento,
        archivo=archivo.read(),
        fechaRecepcion=timezone.now(),
        estadoDocumento=EstadoDocumento.REGISTRADO
    )

    # Múltiples archivos si los hay
    archivos = request.FILES.getlist("archivos")
    for archivo in archivos:
      Documento.objects.create(
          postulante=postulante,
          tipoDocumento=tipo_documento,
          archivo=archivo.read(),
          fechaRecepcion=timezone.now(),
          estadoDocumento=EstadoDocumento.REGISTRADO
      )

    messages.success(request, "Postulante y documento agregados correctamente.")
    return redirect("gestionar_documentos", convocatoria_id=convocatoria.id)

  return render(request, "agregar_postulante.html", {
      "convocatoria": convocatoria
  })


@login_required
def buscar_persona_por_dni(request):
  dni = request.GET.get("dni")
  try:
    persona = Persona.objects.get(dni=dni)
    data = {
        "nombre": persona.nombre,
        "apellidoPaterno": persona.apellidoPaterno,
        "apellidoMaterno": persona.apellidoMaterno,
        "correo": persona.correo,
        "telefono": persona.telefono,
        "genero": persona.genero,
    }
    return JsonResponse({"existe": True, "persona": data})
  except Persona.DoesNotExist:
    return JsonResponse({"existe": False})


@login_required
def postulantes_aptos(request, convocatoria_id):
  convocatoria = get_object_or_404(Convocatoria, id=convocatoria_id)
  postulantes_aceptados = Postulante.objects.filter(
      convocatoria=convocatoria,
      estadoPostulante=EstadoPostulante.ACEPTADO
  )

  clases_existentes = ClaseMagistral.objects.filter(
      postulante__in=postulantes_aceptados
  ).select_related("postulante")

  clases_por_postulante = {
      clase.postulante_id: clase for clase in clases_existentes
  }

  hora_base = time(11, 0)
  hora_maxima = time(20, 0)
  horas_ocupadas = {cm.horaProgramada for cm in clases_existentes}

  hora_actual = hora_base
  for postulante in postulantes_aceptados:
    if postulante.id not in clases_por_postulante:
      while hora_actual in horas_ocupadas and hora_actual <= hora_maxima:
        hora_actual = (datetime.combine(datetime.today(), hora_actual) + timedelta(hours=1)).time()

      if hora_actual > hora_maxima:
        messages.warning(request, f"No hay más horarios disponibles para asignar a {postulante}.")
        continue

      plazas = Plaza.objects.filter(convocatoria=convocatoria)
      secciones = [plaza.seccion for plaza in plazas]
      temas_disponibles = Temas.objects.filter(silabus__curso__seccion__in=secciones)

      tema_asignado = random.choice(list(temas_disponibles)) if temas_disponibles.exists() else None

      ClaseMagistral.objects.create(
          postulante=postulante,
          fechaProgramacion=convocatoria.fechaClaseMagistral.date(),
          horaProgramada=hora_actual,
          temaAsignado=tema_asignado.nombreTema if tema_asignado else "Tema pendiente",
          estadoClaseMagistral=EstadoClaseMagistral.PROGRAMADO
      )

      horas_ocupadas.add(hora_actual)

  clases_actualizadas = ClaseMagistral.objects.filter(
      postulante__in=postulantes_aceptados
  ).select_related("postulante")

  return render(request, "postulantes_aptos.html", {
      "convocatoria": convocatoria,
      "clases_magistrales": clases_actualizadas
  })


@login_required
def enviar_consolidado_pdf(request, convocatoria_id):
  convocatoria = get_object_or_404(Convocatoria, id=convocatoria_id)

  clases = ClaseMagistral.objects.filter(
      postulante__convocatoria=convocatoria,
      postulante__estadoPostulante=EstadoPostulante.ACEPTADO
  ).select_related("postulante__persona")


  template_path = 'consolidado_pdf.html'
  context = {
      'convocatoria': convocatoria,
      'clases': clases,
  }

  html = render_to_string(template_path, context)
  response = HttpResponse(content_type='application/pdf')
  response['Content-Disposition'] = f'attachment; filename="consolidado_convocatoria_{convocatoria.id}.pdf"'

  pisa_status = pisa.CreatePDF(
      html, dest=response, encoding='UTF-8'
  )

  if pisa_status.err:
    return HttpResponse('Error al generar el PDF', status=500)
  return response


# -------------------------- NAVHI --------------------------

@login_required
def dirigir_calificacion(request, convocatoria_id):

  ordenar = request.GET.get('ordenar', '0')

  postulantes = Postulante.objects.filter(convocatoria_id=convocatoria_id,
  estadoPostulante=EstadoPostulante.ACEPTADO).select_related('persona', 'clasemagistral')

  if ordenar == '1':
    postulantes = postulantes.order_by('persona.apellidoPaterno', 'persona.apellidoMaterno', 'persona.nombre')

  cantidadPostulantes = Postulante.objects.filter(convocatoria_id=convocatoria_id,
  estadoPostulante=EstadoPostulante.ACEPTADO).count()

  return render(request, 'dirigir_calificacion.html', {
      'postulantes': postulantes,
      'convocatoria_id': convocatoria_id,
      'cantidadPostulantes': cantidadPostulantes,
      'ordenar': ordenar
  })


@login_required
def ver_documento(request, documento_id):
  try:
    documento = Documento.objects.get(id=documento_id)
    if not documento.archivo:
      return HttpResponse("Documento vacío.", content_type='text/plain')
    response = HttpResponse(documento.archivo, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="documento.pdf"'
    return response
  except Documento.DoesNotExist:
    raise Http404("Documento no encontrado")


@login_required
def mostrar_documentos(request, postulante_id):
  documentos = Documento.objects.filter(
      postulante_id=postulante_id,
      estadoDocumento=EstadoDocumento.ACEPTADO
  )
  postulante = get_object_or_404(Postulante, pk=postulante_id)
  convocatoria_id = postulante.convocatoria_id

  return render(request, 'mostrar_documentos.html', {
      'documentos': documentos,
      'postulante_id': postulante_id,
      'convocatoria_id': convocatoria_id
  })


@login_required
def calificar_documentos(request, postulante_id):

  postulante = get_object_or_404(Postulante, pk=postulante_id)
  convocatoria_id = postulante.convocatoria_id

  try:
    evaluador = Evaluador.objects.get(persona=request.user.persona)
  except Evaluador.DoesNotExist:
    return HttpResponseForbidden("No tienes permisos para calificar documentos")

  if request.method == 'POST':
    cd1 = int(request.POST.get('cd1', 0))
    cd2 = int(request.POST.get('cd2', 0))
    cd3 = int(request.POST.get('cd3', 0))
    cd4 = int(request.POST.get('cd4', 0))
    cd5 = int(request.POST.get('cd5', 0))
    cd6 = int(request.POST.get('cd6', 0))

    if NotaPostulante.objects.filter(postulante_id=postulante_id):
      nota_postulante = nota_postulante = NotaPostulante.objects.filter(postulante=postulante, evaluador=evaluador).order_by('-id').first()
      nota_postulante.notaDocumentoCriterio1 = cd1
      nota_postulante.notaDocumentoCriterio2 = cd2
      nota_postulante.notaDocumentoCriterio3 = cd3
      nota_postulante.notaDocumentoCriterio4 = cd4
      nota_postulante.notaDocumentoCriterio5 = cd5
      nota_postulante.notaDocumentoCriterio6 = cd6
      nota_postulante.save()

    else:
      NotaPostulante.objects.create(
          evaluador=evaluador,
          postulante=postulante,
          notaDocumentoCriterio1=cd1,
          notaDocumentoCriterio2=cd2,
          notaDocumentoCriterio3=cd3,
          notaDocumentoCriterio4=cd4,
          notaDocumentoCriterio5=cd5,
          notaDocumentoCriterio6=cd6,
          estadoNotaPostulante=EstadoNotaPostulante.REVISADO_PARCIALMENTE
      )

    return redirect('seleccionar_modulo', postulante_id=postulante.id)
  return render(request, 'calificar_documentos.html', {
      'postulante': postulante
  })


@login_required
def seleccionar_modulo(request, postulante_id):
  postulante = get_object_or_404(Postulante, pk=postulante_id)
  convocatoria_id = postulante.convocatoria_id

  if request.method == 'POST':
    tipo = request.POST.get('tipo')  # 'presencial' o 'virtual'
    return redirect('evaluar_clase_magistral', postulante_id=postulante.id, tipo=tipo)

  return render(request, 'seleccionar_modulo.html', {
      'postulante': postulante,
      'convocatoria_id': convocatoria_id
  })


@login_required
def evaluar_clase_magistral(request, postulante_id, tipo):
  if tipo == 'presencial':
    tipo_bool = True
  else:
    tipo_bool = False
  clase_magistral = ClaseMagistral.objects.filter(postulante_id=postulante_id).first()
  fecha = clase_magistral.fechaProgramacion
  hora = clase_magistral.horaProgramada
  datetime_combinado = datetime.combine(fecha, hora)
  datetime_mas_una_hora = datetime_combinado + timedelta(hours=1)
  hora_final = datetime_mas_una_hora.time()
  postulante = get_object_or_404(Postulante, pk=postulante_id)
  evaluador = Evaluador.objects.get(persona=request.user.persona)
  convocatoria_id = postulante.convocatoria_id

  if request.method == 'POST':
    c1 = int(request.POST.get('c1', 0))
    c2 = int(request.POST.get('c2', 0))
    c3 = int(request.POST.get('c3', 0))
    c4 = int(request.POST.get('c4', 0))

    nota_postulante = NotaPostulante.objects.filter(
        postulante=postulante,
        evaluador=evaluador
    ).order_by('-id').first()

    nota_postulante.notaClaseCriterio1 = c1
    nota_postulante.notaClaseCriterio2 = c2
    nota_postulante.notaClaseCriterio3 = c3
    nota_postulante.notaClaseCriterio4 = c4
    nota_postulante.estadoNotaPostulante = EstadoNotaPostulante.COMPLETO
    nota_postulante.save()

    return redirect('dirigir_calificacion', convocatoria_id=convocatoria_id)

  return render(request, 'evaluar_clase_magistral.html', {
      'clase_magistral': clase_magistral,
      'hora_final': hora_final,
      'postulante_id': postulante_id,
      'convocatoria_id': convocatoria_id,
      'tipo': tipo_bool,
      'postulante': postulante,
  })


@login_required
def generar_informe_notas(request, convocatoria_id):
  convocatoria = get_object_or_404(Convocatoria, id=convocatoria_id)
  postulantes = Postulante.objects.filter(convocatoria_id=convocatoria_id,
  estadoPostulante=EstadoPostulante.ACEPTADO)
  datos_postulantes = []

  with transaction.atomic():
    convocatoria.estadoConvocatoria = EstadoConvocatoria.FINALIZADO
    convocatoria.save()

  
  for postulante in postulantes:
    notas = NotaPostulante.objects.filter(postulante=postulante)
    nota_totales = []
    for nota in notas:
        suma_documentos = (
            (nota.notaDocumentoCriterio1 or 0) +
            (nota.notaDocumentoCriterio2 or 0) +
            (nota.notaDocumentoCriterio3 or 0) +
            (nota.notaDocumentoCriterio4 or 0) +
            (nota.notaDocumentoCriterio5 or 0) +
            (nota.notaDocumentoCriterio6 or 0)
        )
        suma_clase = (
            (nota.notaClaseCriterio1 or 0) +
            (nota.notaClaseCriterio2 or 0) +
            (nota.notaClaseCriterio3 or 0) +
            (nota.notaClaseCriterio4 or 0)
        )
        nota_total_evaluador = suma_documentos + suma_clase
        nota_totales.append(nota_total_evaluador)

    if nota_totales:
        promedio_nota_total = sum(nota_totales) / len(nota_totales)
    else:
        promedio_nota_total = 0
    
    datos_postulantes.append({
        'nombre': f"{postulante.persona.nombre} {postulante.persona.apellidoPaterno} {postulante.persona.apellidoMaterno} ",
        'nota_total': promedio_nota_total
    })

  datos_postulantes = sorted(datos_postulantes, key=lambda x: x['nota_total'], reverse=True)
  context = {'postulantes': datos_postulantes, 'convocatoria_id': convocatoria_id}
  template = get_template('pdf_informe_notas.html')
  html = template.render(context)

  response = HttpResponse(content_type='application/pdf')
  response['Content-Disposition'] = f'inline; filename="informe_notas_convocatoria_{convocatoria_id}.pdf"'
  pisa_status = pisa.CreatePDF(BytesIO(html.encode('UTF-8')), dest=response, encoding='UTF-8')

  if pisa_status.err:
    return HttpResponse('Hubo un error generando el PDF: %s' % pisa_status.err)
  return response
