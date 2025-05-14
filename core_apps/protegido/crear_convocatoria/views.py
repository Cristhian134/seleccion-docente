from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .forms import ConvocatoriaExternaForm

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


# @login_required
# def crear_convocatoria_externa_view(request):
#   return render(request, 'crear_convocatoria_externa.html', {
#     "url_volver": "/crear-convocatoria/"
#   })
@login_required
def crear_convocatoria_externa_view(request):
  if request.method == 'POST':
    form = ConvocatoriaExternaForm(request.POST)
    if form.is_valid():
      # form.save()
      # return redirect('ver-convocatorias/')  # Cambia esto
      print("Datos del formulario recibidos:")
      for campo, valor in form.cleaned_data.items():
        print(f"{campo}: {valor}")
      return render(
        request, 
        'crear_convocatoria_externa.html', 
        {
          'form': form, 
        "url_volver": "/crear-convocatoria/"
        }
      )
  else:
    form = ConvocatoriaExternaForm()
  return render(
    request, 
    'crear_convocatoria_externa.html', 
    {
      'form': form, 
      "url_volver": "/crear-convocatoria/"
    }
  )
