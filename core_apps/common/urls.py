from django.urls import path
from . import views

urlpatterns = [
  path('descargar-pdf/<int:documento_id>/', views.descargar_pdf, name='descargar_pdf'),
]
