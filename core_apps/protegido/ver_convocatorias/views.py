from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from core_apps.common.models import Postulante, Documento, Convocatoria, Persona, ClaseMagistral, NotaPostulante
from core_apps.common.models import EstadoDocumento, EstadoPostulante, EstadoClaseMagistral, EstadoNotaPostulante
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


@login_required
def convocatoria_dirigir_calificacion(request, convocatoria_id):
    return render(request, 'dirigir_calificacion.html', {
        "convocatoria_id": convocatoria_id,
        "url_volver": "/ver_convocatorias"
    })





# -------------------------- NAVHI --------------------------



def ver_documentos(request, postulante_id):
    postulante = get_object_or_404(Postulante, id=postulante_id)
    documentos = Documento.objects.filter(postulante=postulante)
    return render(request, 'ver_documentos.html', {'postulante': postulante, 'documentos': documentos})


@require_http_methods(["GET", "POST"])
def calificar_documentos(request, postulante_id):
    postulante = get_object_or_404(Postulante, id=postulante_id)

    if request.method == "POST":
        # Aquí recibís las notas de cada criterio (suponiendo que están en POST)
        # Validar y guardar la calificación
        try:
            c1 = int(request.POST.get('c1', 0))
            c2 = int(request.POST.get('c2', 0))
            c3 = int(request.POST.get('c3', 0))
            c4 = int(request.POST.get('c4', 0))
            c5 = int(request.POST.get('c5', 0))
            c6 = int(request.POST.get('c6', 0))
        except ValueError:
            return render(request, 'calificar_documentos.html', {
                'postulante': postulante,
                'error': 'Por favor, ingrese números válidos.'
            })

        # Validar rangos
        if not (0 <= c1 <= 10 and 0 <= c2 <= 10 and 0 <= c3 <= 10 and 0 <= c4 <= 5 and 0 <= c5 <= 5 and 0 <= c6 <= 10):
            return render(request, 'calificar_documentos.html', {
                'postulante': postulante,
                'error': 'Los puntajes deben estar dentro de los rangos permitidos.'
            })

        total = c1 + c2 + c3 + c4 + c5 + c6

        calificacion, created = CalificacionDocumento.objects.update_or_create(
            postulante=postulante,
            defaults={
                'criterio1': c1,
                'criterio2': c2,
                'criterio3': c3,
                'criterio4': c4,
                'criterio5': c5,
                'criterio6': c6,
                'total': total
            }
        )

        return redirect('ver_documentos', postulante_id=postulante.id)

    # GET
    return render(request, 'calificar_documentos.html', {'postulante': postulante})


@require_http_methods(["GET", "POST"])
def clase_magistral(request, postulante_id):
    postulante = get_object_or_404(Postulante, id=postulante_id)

    # Horarios fijos o sacados de BD
    hora = {
        'inicio': '10:00',
        'fin': '12:00'
    }

    if request.method == "POST":
        try:
            c1 = int(request.POST.get('c1', 0))
            c2 = int(request.POST.get('c2', 0))
            c3 = int(request.POST.get('c3', 0))
            c4 = int(request.POST.get('c4', 0))
        except ValueError:
            return render(request, 'clase_magistral.html', {
                'postulante': postulante,
                'hora': hora,
                'error': 'Ingrese números válidos.'
            })

        if not (0 <= c1 <= 20 and 0 <= c2 <= 10 and 0 <= c3 <= 10 and 0 <= c4 <= 10):
            return render(request, 'clase_magistral.html', {
                'postulante': postulante,
                'hora': hora,
                'error': 'Los puntajes deben estar dentro de los rangos permitidos.'
            })

        total = c1 + c2 + c3 + c4

        calificacion, created = CalificacionClase.objects.update_or_create(
            postulante=postulante,
            defaults={
                'criterio1': c1,
                'criterio2': c2,
                'criterio3': c3,
                'criterio4': c4,
                'total': total
            }
        )

        return redirect('clase_magistral', postulante_id=postulante.id)

    return render(request, 'clase_magistral.html', {'postulante': postulante, 'hora': hora})


def generar_informe_pdf(request):
    # Obtener todas las calificaciones combinadas para ordenarlas
    # Sumamos calificación documento + clase (puede ser null)
    postulantes = Postulante.objects.all().annotate(
        puntaje_documento=Sum('calificaciondocumento__total'),
        puntaje_clase=Sum('calificacionclase__total'),
    )

    # Calcular total sumado de ambas calificaciones (tratando None como 0)
    datos = []
    for p in postulantes:
        doc = p.puntaje_documento or 0
        clase = p.puntaje_clase or 0
        total = doc + clase
        datos.append({
            'nombre': f"{p.nombre} {p.apellido}",
            'puntaje_documento': doc,
            'puntaje_clase': clase,
            'total': total
        })

    datos_ordenados = sorted(datos, key=lambda x: x['total'], reverse=True)

    # Generar PDF con reportlab
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 750, "Informe de Puntajes - Sistema de Selección Docente")

    p.setFont("Helvetica", 12)
    y = 720
    p.drawString(50, y, "Nombre")
    p.drawString(300, y, "Documento")
    p.drawString(400, y, "Clase")
    p.drawString(480, y, "Total")

    y -= 20
    for d in datos_ordenados:
        if y < 50:
            p.showPage()
            y = 750
        p.drawString(50, y, d['nombre'])
        p.drawString(300, y, str(d['puntaje_documento']))
        p.drawString(400, y, str(d['puntaje_clase']))
        p.drawString(480, y, str(d['total']))
        y -= 20

    p.showPage()
    p.save()

    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')