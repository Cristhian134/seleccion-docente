from django import template
from django.contrib.auth.models import AnonymousUser, User
from core_apps.common.models import Decano, Persona, EncargadoConsejo, EstadoDecano, EstadoEncargadoConsejo
from core_apps.permisos import ROLES, MODULOS

register = template.Library()

def get_user_rol(user):
    if not user.is_authenticated:
        return "Anonimo"

    persona = getattr(user, "persona", None)
    if not persona:
        return "Usuario"

    if Decano.objects.filter(persona=persona, estadoDecano=EstadoDecano.ACTIVO).exists():
        return ROLES.DECANO
    elif EncargadoConsejo.objects.filter(persona=persona, estadoEncargadoConsejo=EstadoEncargadoConsejo.ACTIVO).exists():
        return ROLES.ENCARGADO_CONSEJO
    
    if user.is_superuser:
        return ROLES.ADMINISTRADOR
    
    return "Usuario"

@register.inclusion_tag("sidenav.html", takes_context=True)
def render_sidenav(context):
    request = context.get('request')
    user = getattr(request, 'user', AnonymousUser())
    url_volver = context.get('url_volver', '/home')

    rol = get_user_rol(user)

    # Filtrar módulos según los roles permitidos
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

    if not user.is_authenticated:
        return {
            "usuario": user,
            "rol": "No autenticado",
            "facultad": None
        }

    # Determinar rol
    rol = "Usuario"

    if user.is_superuser:
        rol = ROLES.ADMINISTRADOR
    else:
        persona = getattr(user, "persona", None)
        if persona:
            if Decano.objects.filter(persona=persona, estadoDecano=EstadoDecano.ACTIVO).exists():
                rol = ROLES.DECANO
            elif EncargadoConsejo.objects.filter(persona=persona, estadoEncargadoConsejo=EstadoEncargadoConsejo.ACTIVO).exists():
                rol = ROLES.ENCARGADO_CONSEJO

    return {
        "usuario": user,
        "rol": rol,
        "facultad": getattr(user, 'facultad', 'No tiene facultad'),
    }


