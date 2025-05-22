from django.contrib import admin, messages
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.template.response import TemplateResponse

from .models import (
    Persona, Usuario, Decano, EncargadoConsejo,
    Convocatoria, Postulante, Curso, Seccion, Plaza,
    Requisito, Docente, EvaluacionDocente, Horario,
    Silabus, Temas, ClaseMagistral, Evaluador,
    Documento, NotaPostulante
)

from .forms import DecanoCreationForm, UsuarioCreationForm, UsuarioChangeForm, DocumentoAdminForm

from .admin_utils.usuarios_admin import EncargadoConsejoAdmin, EvaluadorAdmin


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


@admin.register(Decano)
class DecanoAdmin(admin.ModelAdmin):
  form = DecanoCreationForm
  add_form_template = 'admin/decano_add_form.html'
  change_form_template = 'admin/readonly_form.html'
  change_form = None  # Para evitar edición directa del Decano una vez creado

  def get_form(self, request, obj=None, **kwargs):
    if obj is None:
      return DecanoCreationForm
    return super().get_form(request, obj, **kwargs)

  def has_add_permission(self, request):
    return True

  def has_change_permission(self, request, obj=None):
    return False

  def has_delete_permission(self, request, obj=None):
    return True

  def add_view(self, request, form_url='', extra_context=None):
    if request.method == 'POST':
      form = DecanoCreationForm(request.POST)
      if form.is_valid():
        # Crear Persona
        persona = Persona.objects.create(
            nombre=form.cleaned_data['nombre'],
            apellidoPaterno=form.cleaned_data['apellidoPaterno'],
            apellidoMaterno=form.cleaned_data['apellidoMaterno'],
            dni=form.cleaned_data['dni'],
            correo=form.cleaned_data['correo'],
            telefono=form.cleaned_data['telefono'],
            genero=form.cleaned_data['genero'],
        )

        # Crear Usuario
        usuario = Usuario.objects.create_user(
            codigoUser=form.cleaned_data['codigoUsuario'],
            nombreUser=form.cleaned_data['nombreUsuario'],
            claveUser=form.cleaned_data['password'],
            facultad=form.cleaned_data['facultad'],
            persona=persona,
            is_staff=False  # Importante: sin acceso al admin
        )

        # Crear Decano
        Decano.objects.create(
            persona=persona,
            estadoDecano=form.cleaned_data['estadoDecano']
        )

        self.message_user(request, _('Decano creado exitosamente.'), messages.SUCCESS)
        return self.response_post_save_add(request, None)
    else:
      form = DecanoCreationForm()

    context = {
        **self.admin_site.each_context(request),
        'opts': self.model._meta,
        'form': form,
    }
    return TemplateResponse(request, "admin/decano_add_form.html", context)


admin.site.register(Persona)
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(EncargadoConsejo, EncargadoConsejoAdmin)
admin.site.register(Evaluador, EvaluadorAdmin)
admin.site.register(Documento, DocumentoAdmin)

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
admin.site.register(NotaPostulante)
