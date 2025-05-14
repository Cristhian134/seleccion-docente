from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import render

from core_apps.common.models import Documento

# Create your views here.


@login_required
def descargar_pdf(request, documento_id):
  try:
    doc = Documento.objects.get(pk=documento_id)
    response = HttpResponse(doc.archivo, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{doc.tipoDocumento}.pdf"'
    return response
  except Documento.DoesNotExist:
    raise Http404("Documento no encontrado")
