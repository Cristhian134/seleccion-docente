from django.urls import path
from . import views

urlpatterns = [
    path('ver_convocatorias/', views.ver_convocatorias, name='ver_convocatorias'),

    # Gestión de documentos por convocatoria
    path('ver_convocatorias/gestionar_documentos/<int:convocatoria_id>/',
         views.convocatoria_gestionar_documentos, name='gestionar_documentos'),
    path('ver_convocatorias/gestionar_documentos/<int:convocatoria_id>/agregar/', views.agregar_postulante, name='agregar_postulante'),

    # Visualizar y calificar documentos por postulante (ajustado a funciones propuestas)
    path('ver_convocatorias/dirigir_calificacion/mostrar_documentos/<int:postulante_id>/', views.ver_documentos, name='mostrar_documentos'),
    path('ver_convocatorias/dirigir_calificacion/calificar_documentos/<int:postulante_id>/',
         views.calificar_documentos, name='calificar_documentos'),

    # Evaluar clase magistral por postulante
    path('ver_convocatorias/dirigir_calificacion/evaluar_clase_magistral/<int:postulante_id>/',
         views.clase_magistral, name='evaluar_clase_magistral'),

    # Generar informe PDF para convocatoria (sin id porque genera todos, pero si quieres que sea por convocatoria pasa id y filtras)
    path('ver_convocatorias/dirigir_calificacion/generar_informe/', views.generar_informe_pdf, name='generar_informe'),

    # Ver documento (ya tienes dos rutas para lo mismo, está bien)
    path('ver_documento/<int:documento_id>/', views.ver_documento, name='ver_documento'),
    path('documento/<int:documento_id>/', views.ver_documento, name='ver_documento'),
]
