from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from core_apps.common.models import (
    Convocatoria, Documento, Postulante, EstadoDocumento, Persona, ClaseMagistral,  Usuario, Evaluador, NotaPostulante, EstadoNotaPostulante
)
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, Http404
from django.urls import reverse
from django.contrib import messages
from django.core.files.uploadedfile import UploadedFile
from django.db.models import Sum, F, FloatField
from io import BytesIO
import mimetypes
from datetime import datetime, timedelta
from xhtml2pdf import pisa
from django.template.loader import render_to_string, get_template


@login_required
def ver_convocatorias(request):
    if request.method == "POST":
        convocatoria_id = request.POST.get("convocatoria_id")
        accion = request.POST.get("accion")

        if not convocatoria_id:
            # Si no seleccionó convocatoria, redirige con error (opcional)
            return render(request, 'ver_convocatorias.html', {
                "convocatorias": Convocatoria.objects.all(),
                "error": "Debe seleccionar una convocatoria.",
                "url_volver": "/home"
            })

        # Redireccionar según el botón presionado
        if accion == "documentos":
            return redirect('gestionar_documentos', convocatoria_id=convocatoria_id)
        elif accion == "calificacion":
            return redirect('dirigir_calificacion', convocatoria_id=convocatoria_id)

    # GET con posible búsqueda
    query = request.GET.get('q')
    convocatorias = Convocatoria.objects.all()

    if query:
        convocatorias = convocatorias.filter(
            plaza__curso__nombreCurso__icontains=query
        )

    return render(request, 'ver_convocatorias.html', {
        "convocatorias": convocatorias,
        "url_volver": "/home"
    })

@login_required
def ver_documento(request, documento_id):
    documento = get_object_or_404(Documento, id=documento_id)

    tipo_mime = "application/pdf" if documento.tipoDocumento.lower().endswith("pdf") else "image/png"

    response = HttpResponse(documento.archivo, content_type=tipo_mime)
    response["Content-Disposition"] = f'inline; filename="documento_{documento_id}"'
    return response

#@login_required
#def gestionar_documentos(request):
#    if request.method == 'POST':
#        convocatoria_id = request.POST.get('convocatoria_id')
#        if convocatoria_id:
#            return redirect(f'/documentos/{convocatoria_id}/')  # O usa `reverse()`
#    return redirect('ver_convocatorias')

#@login_required
#def dirigir_calificacion(request):
    #if request.method == 'POST':
    #    convocatoria_id = request.POST.get('convocatoria_id')
    #    if convocatoria_id:
    #        return redirect(f'/calificacion/{convocatoria_id}/')
    #return redirect('ver_convocatorias')
# Create your views here.

@login_required
def convocatoria_gestionar_documentos(request, convocatoria_id):
    convocatoria = get_object_or_404(Convocatoria, id=convocatoria_id)
    postulantes = Postulante.objects.filter(convocatoria=convocatoria).select_related("persona")
    postulantes = Postulante.objects.filter(convocatoria=convocatoria).prefetch_related('documento_set')

    # Anotar fecha más antigua (mínima) por postulante
    for postulante in postulantes:
        doc = postulante.documento_set.order_by("fechaRecepcion").first()
        postulante.fecha_documento_mas_antiguo = doc.fechaRecepcion if doc else None

    # 🔥 Agrega esto: serialización para el frontend
        postulante.documentos_json = [
            {
                "tipoDocumento": d.tipoDocumento,
                "fechaRecepcion": d.fechaRecepcion.strftime("%Y-%m-%d"),
                "url": reverse('ver_documento', args=[d.id])
            }
            for d in postulante.documento_set.all()
        ]

    # Acción: Eliminar postulante
    if request.method == "POST" and "eliminar" in request.POST:
        postulante_id = request.POST.get("postulante_id")
        postulante = get_object_or_404(Postulante, id=postulante_id)
        postulante.delete()
        return redirect('gestionar_documentos', convocatoria_id=convocatoria_id)

    # Acción: Aceptar / Rechazar documentos
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
        "url_volver": "/ver_convocatorias"
    })


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
    })


# -------------------------- NAVHI --------------------------

@login_required
def dirigir_calificacion(request, convocatoria_id):

    ordenar = request.GET.get('ordenar', '0')

    postulantes = Postulante.objects.filter(convocatoria_id=convocatoria_id).select_related('persona', 'clasemagistral')

    if ordenar == '1':
        postulantes = postulantes.order_by('persona.apellidoPaterno', 'persona.apellidoMaterno', 'persona.nombre')
    
    cantidadPostulantes = Postulante.objects.filter(convocatoria_id=convocatoria_id).count()

    return render(request, 'dirigir_calificacion.html',{
        'postulantes':postulantes, 
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

    return render(request, 'mostrar_documentos.html',{
        'documentos':documentos, 
        'postulante_id': postulante_id,
        'convocatoria_id': convocatoria_id
    })

@login_required
def calificar_documentos(request, postulante_id):

    print(request.method)

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
            evaluador = evaluador,
            postulante= postulante,
            notaDocumentoCriterio1 = cd1,
            notaDocumentoCriterio2 = cd2,
            notaDocumentoCriterio3 = cd3,
            notaDocumentoCriterio4 = cd4,
            notaDocumentoCriterio5 = cd5,
            notaDocumentoCriterio6 = cd6,
            estadoNotaPostulante = EstadoNotaPostulante.REVISADO_PARCIALMENTE
            )

        return redirect('evaluar_clase_magistral', postulante_id=postulante.id)

        
    return render(request, 'calificar_documentos.html', {
        'postulante': postulante
    })

@login_required
def evaluar_clase_magistral(request, postulante_id):
    clase_magistral = ClaseMagistral.objects.filter(postulante_id=postulante_id).first()
    
    fecha = clase_magistral.fechaProgramacion
    hora = clase_magistral.horaProgramada
    datetime_combinado = datetime.combine(fecha, hora)

    # sumar una hora
    datetime_mas_una_hora = datetime_combinado + timedelta(hours=1)

    # si quieres la hora solamente después de sumar
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
        'convocatoria_id': convocatoria_id

    })

@login_required
def generar_informe_notas(request, convocatoria_id):
    postulantes = Postulante.objects.filter(convocatoria_id=convocatoria_id)

    datos_postulantes = []

    for postulante in postulantes:
        notas = NotaPostulante.objects.filter(postulante=postulante)

        # Calculamos nota total — puedes ajustar este cálculo
        nota_total = 0
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
            nota_total += suma_documentos + suma_clase

        datos_postulantes.append({
            'nombre': f"{postulante.persona.nombre} {postulante.persona.apellidoPaterno} {postulante.persona.apellidoMaterno} ",
            'nota_total': nota_total
        })

    # Ordenar de mayor a menor
    datos_postulantes = sorted(datos_postulantes, key=lambda x: x['nota_total'], reverse=True)

    # Cargar plantilla
    context = {'postulantes': datos_postulantes, 'convocatoria_id': convocatoria_id}
    template = get_template('pdf_informe_notas.html')
    html = template.render(context)

    # Crear el PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="informe_notas_convocatoria_{convocatoria_id}.pdf"'
    pisa_status = pisa.CreatePDF(BytesIO(html.encode('UTF-8')), dest=response, encoding='UTF-8')

    if pisa_status.err:
        return HttpResponse('Hubo un error generando el PDF: %s' % pisa_status.err)
    return response