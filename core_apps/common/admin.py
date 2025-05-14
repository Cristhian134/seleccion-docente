from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (
    Persona, Usuario, Decano, EncargadoConsejo,
    Convocatoria, Postulante, Curso, Seccion, Plaza,
    Requisito, Docente, EvaluacionDocente, Horario,
    Silabus, Temas, ClaseMagistral, Evaluador,
    Documento, NotaPostulante
)

from .forms import UsuarioCreationForm, UsuarioChangeForm, DocumentoAdminForm


class UsuarioAdmin(BaseUserAdmin):
  form = UsuarioChangeForm
  add_form = UsuarioCreationForm

  list_display = ('codigoUsuario', 'nombreUsuario', 'is_staff', 'facultad')
  list_filter = ('is_staff', 'is_superuser', 'facultad')
  fieldsets = (
      (None, {'fields': ('codigoUsuario', 'nombreUsuario', 'password')}),
      ('Información Personal', {'fields': ('facultad', 'persona')}),
      ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
  )
  add_fieldsets = (
      (None, {
          'classes': ('wide',),
          'fields': ('codigoUsuario', 'nombreUsuario', 'facultad', 'persona', 'password1', 'password2')}
       ),
  )
  search_fields = ('codigoUsuario',)
  ordering = ('codigoUsuario',)
  filter_horizontal = ('groups', 'user_permissions',)


class DocumentoAdmin(admin.ModelAdmin):
  form = DocumentoAdminForm
  list_display = ('postulante', 'tipoDocumento', 'fechaRecepcion', 'estadoDocumento', 'descargar_pdf')

  def descargar_pdf(self, obj):
    if obj.archivo:
      return format_html('<a class="button" href="{}">Descargar</a>', obj.descargar_url())
    return "Sin archivo"
  descargar_pdf.short_description = "Archivo"


admin.site.register(Persona)
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Decano)
admin.site.register(EncargadoConsejo)
admin.site.register(Convocatoria)
admin.site.register(Postulante)
admin.site.register(Curso)
admin.site.register(Seccion)
admin.site.register(Plaza)
admin.site.register(Requisito)
admin.site.register(Docente)
admin.site.register(EvaluacionDocente)
admin.site.register(Horario)
admin.site.register(Silabus)
admin.site.register(Temas)
admin.site.register(ClaseMagistral)
admin.site.register(Evaluador)
admin.site.register(Documento, DocumentoAdmin)
admin.site.register(NotaPostulante)
