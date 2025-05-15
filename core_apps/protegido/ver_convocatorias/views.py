from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from core_apps.common.models import Convocatoria

@login_required
def ver_convocatorias(request):
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
def gestionar_documentos(request):
    if request.method == 'POST':
        convocatoria_id = request.POST.get('convocatoria_id')
        if convocatoria_id:
            return redirect(f'/documentos/{convocatoria_id}/')  # O usa `reverse()`
    return redirect('ver_convocatorias')

@login_required
def dirigir_calificacion(request):
    if request.method == 'POST':
        convocatoria_id = request.POST.get('convocatoria_id')
        if convocatoria_id:
            return redirect(f'/calificacion/{convocatoria_id}/')
    return redirect('ver_convocatorias')
# Create your views here.
