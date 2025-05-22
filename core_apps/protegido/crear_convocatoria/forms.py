from django import forms
from core_apps.common.models import Convocatoria


class ConvocatoriaExternaForm(forms.ModelForm):
  class Meta:
    model = Convocatoria
    fields = '__all__'
    exclude = ['tipoConvocatoria', 'fechaPublicacion', 'estadoConvocatoria']
