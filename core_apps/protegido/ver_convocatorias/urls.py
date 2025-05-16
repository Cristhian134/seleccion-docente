from django.urls import path
from . import views

urlpatterns = [
    path('ver_convocatorias/', views.ver_convocatorias, name='ver_convocatorias'),
    path('ver_convocatorias/gestionar_documentos/<int:convocatoria_id>/', views.convocatoria_gestionar_documentos, name='gestionar_documentos'),
    path('ver_convocatorias/dirigir_calificacion/<int:convocatoria_id>/', views.convocatoria_dirigir_calificacion, name='dirigir_calificacion'),
]


