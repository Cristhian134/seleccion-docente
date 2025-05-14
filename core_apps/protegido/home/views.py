from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required  # Solo accesible si el usuario está autenticado
def home_view(request):
  return render(request, 'home.html')  # Asegúrate de tener esta plantilla
