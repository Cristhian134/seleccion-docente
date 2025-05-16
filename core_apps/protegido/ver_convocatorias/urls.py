from django.urls import path
from . import views

urlpatterns = [
    path('ver_convocatorias/', views.ver_convocatorias, name='ver_convocatorias'),
    path('ver_convocatorias/gestionar_documentos/<int:convocatoria_id>/', views.convocatoria_gestionar_documentos, name='gestionar_documentos'),
    path('ver_convocatorias/gestionar_documentos/<int:convocatoria_id>/agregar/', views.agregar_postulante, name='agregar_postulante'),
    #path('ver_convocatorias/documentos/<int:postulante_id>/', views.ver_documentos_postulante, name='ver_documentos_postulante'),
    #path('ver_convocatorias/<int:convocatoria_id>/aptos/', views.postulantes_aptos, name='postulantes_aptos'),
    path('ver_convocatorias/dirigir_calificacion/<int:convocatoria_id>/', views.convocatoria_dirigir_calificacion, name='dirigir_calificacion'),
    
]




