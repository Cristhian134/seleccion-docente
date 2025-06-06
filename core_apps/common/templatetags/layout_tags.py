from django import template
from django.contrib.auth.models import AnonymousUser
from core_apps.common.models import Decano, Evaluador, EncargadoConsejo, EstadoDecano, EstadoEncargadoConsejo
from core_apps.permisos import ROLES, MODULOS

register = template.Library()


def get_user_rol(user):
  if not user.is_authenticated:
    return "Anonimo"

  persona = getattr(user, "persona", None)
  if not persona:
    return "Usuario"

  if user.is_superuser:
    return ROLES.ADMINISTRADOR

  if Decano.objects.filter(persona=persona, estadoDecano=EstadoDecano.ACTIVO).exists():
    return ROLES.DECANO
  elif EncargadoConsejo.objects.filter(persona=persona, estadoEncargadoConsejo=EstadoEncargadoConsejo.ACTIVO).exists():
    return ROLES.ENCARGADO_CONSEJO
  elif Evaluador.objects.filter(persona=persona).exists():
    return ROLES.EVALUADOR

  return "Usuario"


@register.inclusion_tag("sidenav.html", takes_context=True)
def render_sidenav(context):
  request = context.get('request')
  user = getattr(request, 'user', AnonymousUser())
  url_volver = context.get('url_volver', '/home')
  rol = get_user_rol(user)
  modulos_permitidos = [
      modulo for modulo in MODULOS
      if rol in modulo.get("roles", [])
  ]

  return {
      "modulos": modulos_permitidos,
      "rol": rol,
      'url_volver': url_volver,
  }


@register.inclusion_tag("header.html", takes_context=True)
def render_header(context):
  request = context.get('request')
  user = getattr(request, 'user', AnonymousUser())
  codigo = user.codigoUsuario
  if not user.is_authenticated:
    return {
        "usuario": user,
        "rol": "No autenticado",
        "facultad": None,
        "codigo": codigo,
    }
  rol = get_user_rol(user)
  persona = getattr(user, "persona", None)
  nombre_completo = f'{persona.nombre} {persona.apellidoPaterno} {persona.apellidoMaterno}'
  admin = False
  if rol == ROLES.ADMINISTRADOR:
    admin = True

  return {
      "usuario": nombre_completo,
      "rol": rol,
      "facultad": getattr(user, 'facultad', 'No tiene facultad'),
      "codigo": codigo,
      "admin": admin,
  }
