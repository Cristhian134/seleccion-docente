class ROLES:
  DECANO = "Decano"
  ADMINISTRADOR = "Administrador"
  ENCARGADO_CONSEJO = "Encargado Consejo"
  EVALUADOR = "Evaluador"


MODULOS = [
  {
    "nombre": "Listar docentes",
    "icono": "fa fa-list",
    "url": "/listar-docentes/",
    "roles": [
      ROLES.ADMINISTRADOR,
      ROLES.DECANO,
      ROLES.ENCARGADO_CONSEJO
    ],
  },
  {
    "nombre": "Crear convocatoria",
    "icono": "fa fa-bullhorn",
    "url": "/crear-convocatoria/",
    "roles": [
      ROLES.ADMINISTRADOR,
      ROLES.DECANO,
      ROLES.ENCARGADO_CONSEJO
    ],
  },
  {
    "nombre": "Ver convocatorias",
    "icono": "fa fa-external-link",
    "url": "/ver_convocatorias/",
    "roles": [
      ROLES.ADMINISTRADOR,
      ROLES.ENCARGADO_CONSEJO,
      ROLES.EVALUADOR],
  },
]
