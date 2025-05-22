from django.contrib import admin, messages
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _

from core_apps.common.models import EncargadoConsejo, Evaluador, Persona, Usuario
from core_apps.common.forms import DecanoCreationForm, EvaluadorCreationForm, EncargadoConsejoCreationForm


class EncargadoConsejoAdmin(admin.ModelAdmin):
  form = EvaluadorCreationForm
  add_form_template = 'admin/encargado_consejo_add_form.html'
  change_form_template = 'admin/readonly_form.html'
  change_form = None  # Para evitar edición directa del Decano una vez creado

  def get_form(self, request, obj=None, **kwargs):
    if obj is None:
      return EncargadoConsejoCreationForm
    return super().get_form(request, obj, **kwargs)

  def has_add_permission(self, request):
    return True

  def has_change_permission(self, request, obj=None):
    return False

  def has_delete_permission(self, request, obj=None):
    return True

  def add_view(self, request, form_url='', extra_context=None):
    if request.method == 'POST':
      form = EncargadoConsejoCreationForm(request.POST)
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
        EncargadoConsejo.objects.create(
            persona=persona,
            estadoEncargadoConsejo=form.cleaned_data['estadoEncargadoConsejo'],
        )

        self.message_user(request, _('Encargado Consejo creado exitosamente.'), messages.SUCCESS)
        return self.response_post_save_add(request, None)
    else:
      form = EncargadoConsejoCreationForm()

    context = {
        **self.admin_site.each_context(request),
        'opts': self.model._meta,
        'form': form,
    }
    return TemplateResponse(request, "admin/encargado_consejo_add_form.html", context)


class EvaluadorAdmin(admin.ModelAdmin):
  form = EvaluadorCreationForm
  add_form_template = 'admin/evaluador_add_form.html'
  change_form_template = 'admin/readonly_form.html'
  change_form = None  # Para evitar edición directa del Decano una vez creado

  def get_form(self, request, obj=None, **kwargs):
    if obj is None:
      return EvaluadorCreationForm
    return super().get_form(request, obj, **kwargs)

  def has_add_permission(self, request):
    return True

  def has_change_permission(self, request, obj=None):
    return False

  def has_delete_permission(self, request, obj=None):
    return True

  def add_view(self, request, form_url='', extra_context=None):
    if request.method == 'POST':
      form = EvaluadorCreationForm(request.POST)
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
        Evaluador.objects.create(
            persona=persona,
            estadoEvaluador=form.cleaned_data['estadoEvaluador'],
            tipoEvaluador=form.cleaned_data['tipoEvaluador']
        )

        self.message_user(request, _('Evaluador creado exitosamente.'), messages.SUCCESS)
        return self.response_post_save_add(request, None)
    else:
      form = EvaluadorCreationForm()

    context = {
        **self.admin_site.each_context(request),
        'opts': self.model._meta,
        'form': form,
    }
    return TemplateResponse(request, "admin/evaluador_add_form.html", context)
