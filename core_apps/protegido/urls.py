from django.urls import include, path

urlpatterns = [
  path("", include("core_apps.protegido.home.urls")),
  path("", include("core_apps.protegido.listar_docentes.urls")),
  path("", include("core_apps.protegido.crear_convocatoria.urls")),
  path("", include("core_apps.protegido.ver_convocatorias.urls")),
]
