from django.urls import path
from . import views

urlpatterns = [
    path('ver_convocatorias/', views.ver_convocatorias, name='ver_convocatorias'),
    path('ver_convocatorias/gestionar_documentos/<int:convocatoria_id>/', views.convocatoria_gestionar_documentos, name='gestionar_documentos'),
    path('ver_convocatorias/gestionar_documentos/<int:convocatoria_id>/agregar/', views.agregar_postulante, name='agregar_postulante'),
    #path('ver_convocatorias/documentos/<int:postulante_id>/', views.ver_documentos_postulante, name='ver_documentos_postulante'),
    #path('ver_convocatorias/<int:convocatoria_id>/aptos/', views.postulantes_aptos, name='postulantes_aptos'),
    path('ver_convocatorias/dirigir_calificacion/<int:convocatoria_id>/', views.convocatoria_dirigir_calificacion, name='dirigir_calificacion'),
    path('ver_convocatorias/dirigir_calificacion/mostrar_documentos/<int:postulante_id>/', views.convocatoria_mostrar_documentos, name='mostrar_documentos'),
    path('ver_convocatorias/dirigir_calificacion/calificar_documentos/<int:postulante_id>/', views.convocatoria_calificar_documentos, name='calificar_documentos'),
    path('ver_convocatorias/dirigir_calificacion/evaluar_clase_magistral/<int:postulante_id>/', views.convocatoria_evaluar_clase_magistral, name='evaluar_clase_magistral'),
    path('ver_convocatorias/dirigir_calificacion/generar_informe/<int:convocatoria_id>/', views.convocatoria_generar_informe, name='generar_informe'),

    
]




