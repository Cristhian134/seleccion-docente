from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.


@login_required
def listar_docentes_view(request):
  return render(request, 'listar_docentes.html', {
    "url_volver": "/home"
  })
