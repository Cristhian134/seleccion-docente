from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from core_apps.common.models import Postulante, Documento, Convocatoria, Persona
from core_apps.common.models import EstadoDocumento, EstadoPostulante
from django.views.decorators.http import require_http_methods

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
        archivo = request.FILES.get("archivo")

        # Buscar o crear Persona
        persona, created = Persona.objects.get_or_create(
            nombre=nombre,
            apellidoPaterno=apellido_paterno,
            apellidoMaterno=apellido_materno,
            defaults={
                "dni": "00000000",  # Ajustar en producción
                "correo": "sin@email.com",
                "telefono": "000000000",
                "genero": "otro",
            }
        )

        # Crear postulante
        postulante, created_postulante = Postulante.objects.get_or_create(
            persona=persona,
            convocatoria=convocatoria,
            defaults={"estadoPostulante": EstadoPostulante.REGISTRADO}
        )

        # Crear documento
        if archivo:
            Documento.objects.create(
                postulante=postulante,
                tipoDocumento=tipo_documento,
                archivo=archivo.read(),
                fechaRecepcion=timezone.now(),
                estadoDocumento=EstadoDocumento.REGISTRADO
            )

        # Redireccionar de nuevo a la vista de gestión
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
