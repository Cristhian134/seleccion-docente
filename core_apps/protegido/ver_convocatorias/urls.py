from django.urls import path
from . import views

urlpatterns = [
     path('ver_convocatorias/', views.ver_convocatorias, name='ver_convocatorias'),

     path('ver_convocatorias/gestionar_documentos/<int:convocatoria_id>/',
         views.convocatoria_gestionar_documentos, name='gestionar_documentos'),
     path('ver_convocatorias/gestionar_documentos/<int:convocatoria_id>/agregar/', views.agregar_postulante, name='agregar_postulante'),
     path('convocatoria/<int:convocatoria_id>/postulantes_aptos/', views.postulantes_aptos, name='postulantes_aptos'),
     path("convocatoria/<int:convocatoria_id>/consolidado_pdf/", views.enviar_consolidado_pdf, name="enviar_consolidado_pdf"),
     path('buscar_persona_por_dni/', views.buscar_persona_por_dni, name='buscar_persona_por_dni'),

    # path('convocatoria/<int:convocatoria_id>/generar-pdf/', views.generar_consolidado_pdf, name='generar_consolidado_pdf'),

     path('ver_convocatorias/dirigir_calificacion/<int:convocatoria_id>/', views.dirigir_calificacion, name='dirigir_calificacion'),
     path('ver_convocatorias/dirigir_calificacion/mostrar_documentos/<int:postulante_id>/', views.mostrar_documentos, name='mostrar_documentos'),
     path('ver_convocatorias/dirigir_calificacion/calificar_documentos/<int:postulante_id>/',
         views.calificar_documentos, name='calificar_documentos'),

     path('ver_convocatorias/elegir_modulo/<int:postulante_id>/',
         views.seleccionar_modulo, name='seleccionar_modulo'),

     path('ver_convocatorias/dirigir_calificacion/evaluar_clase_magistral/<int:postulante_id>/<str:tipo>/',
         views.evaluar_clase_magistral, name='evaluar_clase_magistral'),
     path('ver_convocatorias/dirigir_calificacion/generar_informe/<int:convocatoria_id>/',
         views.generar_informe_notas, name='generar_informe_notas'),


     path('ver_documento/<int:documento_id>/', views.ver_documento, name='ver_documento'),
     path('documento/<int:documento_id>/', views.ver_documento, name='ver_documento'),
]
