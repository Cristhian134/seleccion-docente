from django.urls import path
from . import views

urlpatterns = [
  path('crear-convocatoria/', views.crear_convocatoria_view, name='crear-convocatoria'),
  path('crear-convocatoria/convocatoria-interna/', views.crear_convocatoria_interna_view, name='convocatoria-interna'),
  path('crear-convocatoria/convocatoria-externa/', views.crear_convocatoria_externa_view, name='convocatoria-externa'),
]
