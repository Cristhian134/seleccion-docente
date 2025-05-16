from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from core_apps.common.models import Convocatoria

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
    return render(request, 'gestionar_documentos.html', {
        "convocatoria_id": convocatoria_id,
        "url_volver": "/ver_convocatorias"
    })

@login_required
def convocatoria_dirigir_calificacion(request, convocatoria_id):
    return render(request, 'dirigir_calificacion.html', {
        "convocatoria_id": convocatoria_id,
        "url_volver": "/ver_convocatorias"
    })
