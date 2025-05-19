from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from core_apps.autenticacion.views import logout_view
from core_apps.common.models import (
    Decano, EncargadoConsejo, EstadoDecano, EstadoEncargadoConsejo, EstadoEvaluador, Evaluador
)


def get_user_rol(user):
  if not user.is_authenticated:
    return "Anonimo"
  if user.is_superuser:
    return "Administrador"

  persona = getattr(user, "persona", None)
  if not persona:
    return "Usuario"

  if Decano.objects.filter(persona=persona, estadoDecano=EstadoDecano.ACTIVO).exists():
    return "Decano"
  elif EncargadoConsejo.objects.filter(persona=persona, estadoEncargadoConsejo=EstadoEncargadoConsejo.ACTIVO).exists():
    return "Encargado Consejo"
  elif Evaluador.objects.filter(persona=persona).exists():
    return "Evaluador"

  return "Usuario"


class VerificarSesionMiddleware:
  """
  Middleware para validar la sesión y rol del usuario.
  - Redirige a login si no está autenticado.
  - Redirige a home si accede a '/' ya autenticado.
  - Cierra sesión si no tiene un rol autorizado.
  """

  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    # Excluir el admin
    if request.path.startswith('/admin'):
      return self.get_response(request)

    # Usuario autenticado
    if request.user.is_authenticated:
      rol = get_user_rol(request.user)

      if rol not in ["Administrador", "Decano", "Encargado Consejo", "Evaluador"]:
        logout_view(request)
        return redirect('login')  # Cierra sesión y redirige

      if request.path == '/':
        return redirect('home')  # Ya autenticado, va a home
    else:
      # Usuario no autenticado
      if request.path == '/':
        return redirect('login')

    return self.get_response(request)


class Redirigir404Middleware:
  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    response = self.get_response(request)

    if response.status_code == 404:
      return HttpResponseRedirect(reverse('login'))
    return response
