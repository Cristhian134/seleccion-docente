# forms.py
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from core_apps.common.models import Decano, EncargadoConsejo, EstadoDecano, Evaluador, Facultad, Persona, Postulante, Usuario, Documento


class UsuarioCreationForm(forms.ModelForm):
  password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
  password2 = forms.CharField(label="Confirmar contraseña", widget=forms.PasswordInput)

  class Meta:
    model = Usuario
    fields = ('codigoUsuario', 'nombreUsuario', 'facultad', 'persona')

  def clean_password2(self):
    pw1 = self.cleaned_data.get("password1")
    pw2 = self.cleaned_data.get("password2")
    if pw1 and pw2 and pw1 != pw2:
      raise forms.ValidationError("Las contraseñas no coinciden.")
    return pw2

  def save(self, commit=True):
    user = super().save(commit=False)
    user.set_password(self.cleaned_data["password1"])
    if commit:
      user.save()
    return user


class UsuarioChangeForm(forms.ModelForm):
  password = ReadOnlyPasswordHashField()

  class Meta:
    model = Usuario
    fields = ('codigoUsuario', 'nombreUsuario', 'facultad', 'persona', 'is_active', 'is_staff', 'is_superuser')

  def clean_password(self):
    return self.initial["password"]


class DocumentoAdminForm(forms.ModelForm):
  archivo = forms.FileField(label="Archivo PDF")

  class Meta:
    model = Documento
    fields = ['postulante', 'tipoDocumento', 'fechaRecepcion', 'estadoDocumento']  # Agregamos postulante

  def clean_archivo(self):
    file = self.cleaned_data['archivo']
    if file.content_type != 'application/pdf':
      raise forms.ValidationError("Solo se permiten archivos PDF.")
    return file.read()

  def save(self, commit=True):
    instance = super().save(commit=False)
    instance.archivo = self.cleaned_data['archivo']
    if commit:
      instance.save()
    return instance


class DecanoCreationForm(forms.ModelForm):
  # Datos de la persona
  nombre = forms.CharField(max_length=128)
  apellidoPaterno = forms.CharField(max_length=128)
  apellidoMaterno = forms.CharField(max_length=128)
  dni = forms.CharField(max_length=8)
  correo = forms.EmailField()
  telefono = forms.CharField(max_length=9)
  genero = forms.ChoiceField(choices=Persona._meta.get_field('genero').choices)

  codigoUsuario = forms.CharField(max_length=64)
  nombreUsuario = forms.CharField(max_length=64)
  password = forms.CharField(widget=forms.PasswordInput)
  facultad = forms.ChoiceField(choices=Usuario._meta.get_field('facultad').choices)

  class Meta:
    model = Decano
    fields = ['estadoDecano']


class EncargadoConsejoCreationForm(forms.ModelForm):
  # Datos de la persona
  nombre = forms.CharField(max_length=128)
  apellidoPaterno = forms.CharField(max_length=128)
  apellidoMaterno = forms.CharField(max_length=128)
  dni = forms.CharField(max_length=8)
  correo = forms.EmailField()
  telefono = forms.CharField(max_length=9)
  genero = forms.ChoiceField(choices=Persona._meta.get_field('genero').choices)

  codigoUsuario = forms.CharField(max_length=64)
  nombreUsuario = forms.CharField(max_length=64)
  password = forms.CharField(widget=forms.PasswordInput)
  facultad = forms.ChoiceField(choices=Usuario._meta.get_field('facultad').choices)

  class Meta:
    model = EncargadoConsejo
    fields = ['estadoEncargadoConsejo']


class EvaluadorCreationForm(forms.ModelForm):
  # Datos de la persona
  nombre = forms.CharField(max_length=128)
  apellidoPaterno = forms.CharField(max_length=128)
  apellidoMaterno = forms.CharField(max_length=128)
  dni = forms.CharField(max_length=8)
  correo = forms.EmailField()
  telefono = forms.CharField(max_length=9)
  genero = forms.ChoiceField(choices=Persona._meta.get_field('genero').choices)

  codigoUsuario = forms.CharField(max_length=64)
  nombreUsuario = forms.CharField(max_length=64)
  password = forms.CharField(widget=forms.PasswordInput)
  facultad = forms.ChoiceField(choices=Usuario._meta.get_field('facultad').choices)

  class Meta:
    model = Evaluador
    fields = ['estadoEvaluador', 'tipoEvaluador']
