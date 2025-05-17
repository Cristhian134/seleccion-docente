from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from core_apps.common.models import (
    Postulante, Documento, Convocatoria, Persona, ClaseMagistral,
    NotaPostulante, EstadoDocumento, EstadoPostulante, EstadoClaseMagistral,
    EstadoNotaPostulante, CalificacionDocumento, CalificacionClase
)
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.core.files.uploadedfile import UploadedFile
from django.db.models import Sum, F, FloatField
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import mimetypes


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

def ver_convocatorias(request):
    convocatorias = Convocatoria.objects.all()
    return render(request, 'ver_convocatorias.html', {'convocatorias': convocatorias})

def convocatoria_gestionar_documentos(request, convocatoria_id):
    convocatoria = get_object_or_404(Convocatoria, id=convocatoria_id)
    postulantes = convocatoria.postulante_set.all()
    return render(request, 'gestionar_documentos.html', {'convocatoria': convocatoria, 'postulantes': postulantes})

def agregar_postulante(request, convocatoria_id):
    convocatoria = get_object_or_404(Convocatoria, id=convocatoria_id)
    if request.method == 'POST':
        form = PostulanteForm(request.POST)
        if form.is_valid():
            postulante = form.save(commit=False)
            postulante.convocatoria = convocatoria
            postulante.save()
            return redirect('gestionar_documentos', convocatoria_id=convocatoria.id)
    else:
        form = PostulanteForm()
    return render(request, 'agregar_postulante.html', {'form': form, 'convocatoria': convocatoria})

def convocatoria_dirigir_calificacion(request, convocatoria_id):
    convocatoria = get_object_or_404(Convocatoria, id=convocatoria_id)
    postulantes = convocatoria.postulante_set.all()
    return render(request, 'dirigir_calificacion.html', {'convocatoria': convocatoria, 'postulantes': postulantes})

def ver_documentos(request, postulante_id):
    postulante = get_object_or_404(Postulante, id=postulante_id)
    documentos = postulante.documento_set.all()
    return render(request, 'ver_documentos.html', {'postulante': postulante, 'documentos': documentos})

def calificar_documentos(request, postulante_id):
    postulante = get_object_or_404(Postulante, id=postulante_id)
    documentos = postulante.documento_set.all()

    if request.method == 'POST':
        for documento in documentos:
            form = CalificacionDocumentoForm(request.POST, instance=documento, prefix=str(documento.id))
            if form.is_valid():
                form.save()
        return redirect('mostrar_documentos', postulante_id=postulante.id)

    else:
        forms = []
        for documento in documentos:
            form = CalificacionDocumentoForm(instance=documento, prefix=str(documento.id))
            forms.append((documento, form))
        return render(request, 'calificar_documentos.html', {'postulante': postulante, 'forms': forms})

def clase_magistral(request, postulante_id):
    postulante = get_object_or_404(Postulante, id=postulante_id)

    if request.method == 'POST':
        form = ClaseMagistralForm(request.POST, instance=postulante)
        if form.is_valid():
            form.save()
            return redirect('mostrar_documentos', postulante_id=postulante.id)
    else:
        form = ClaseMagistralForm(instance=postulante)

    return render(request, 'evaluar_clase_magistral.html', {'form': form, 'postulante': postulante})

def generar_informe_pdf(request):
    # Tu lógica para generar el informe
    return render(request, 'informe_pdf.html')

def ver_documento(request, documento_id):
    documento = get_object_or_404(Documento, id=documento_id)
    return render(request, 'ver_documento.html', {'documento': documento})