from django.urls import path
from . import views

urlpatterns = [
    path('ver_convocatorias/', views.ver_convocatorias, name='ver_convocatorias'),
    path('gestionar_documentos/', views.gestionar_documentos, name='gestionar_documentos'),
    path('dirigir_calificacion/', views.dirigir_calificacion, name='dirigir_calificacion'),
]

