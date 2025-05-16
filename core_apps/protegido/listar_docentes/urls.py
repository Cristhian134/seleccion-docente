from django.urls import path
from . import views

urlpatterns = [
  path('listar-docentes/', views.listar_docentes_view, name='listar-docentes'),
]
