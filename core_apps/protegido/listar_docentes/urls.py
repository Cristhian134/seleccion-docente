from django.urls import path
from . import views

urlpatterns = [
  path('listar-docentes/', views.listar_docentes_view, name='listar-docentes'),
  path('listar-docentes/exportar/pdf/', views.exportar_docentes_pdf, name='exportar_pdf'),
  path('listar-docentes/exportar/excel/', views.exportar_docentes_excel, name='exportar_excel'),
]
