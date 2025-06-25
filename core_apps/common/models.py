# models.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.urls import reverse

from datetime import datetime, timedelta


class GeneroPersona(models.TextChoices):
  MASCULINO = "masculino", "Masculino"
  FEMENINO = "femenino", "Femenino"


class Persona(models.Model):
  nombre = models.CharField(max_length=128)
  apellidoPaterno = models.CharField(max_length=128)
  apellidoMaterno = models.CharField(max_length=128)
  dni = models.CharField(max_length=8, unique=True)
  correo = models.EmailField(max_length=64)
  telefono = models.CharField(max_length=9)
  genero = models.CharField(
    max_length=64,
    choices=GeneroPersona.choices,
  )

  def __str__(self):
    return f"{self.nombre} {self.apellidoPaterno}"

  class Meta:
    db_table = "persona"


class UserManager(BaseUserManager):
  def create_user(self, codigoUser, nombreUser, claveUser=None, facultad=None, persona=None, **extra_fields):
    """
    Método para crear un usuario normal, que también debe tener una relación con el modelo Persona.
    """
    if not codigoUser:
      raise ValueError("El código de usuario es obligatorio")
    if not persona:
      raise ValueError("El usuario debe estar asociado a una persona")
    if not facultad:
      raise ValueError("El superusuario debe pertenecer o a una facultad.")

    # Crear un usuario normal
    user = self.model(
        codigoUsuario=codigoUser,
        nombreUsuario=nombreUser,
        persona=persona,  # Asociamos al modelo Persona
        facultad=facultad,
        **extra_fields
    )
    user.set_password(claveUser)
    user.save(using=self._db)
    return user

  def create_superuser(self, codigoUser, nombreUser, claveUser=None, facultad=None, persona=None, **extra_fields):
    """
    Método para crear un superusuario, que también debe estar asociado a una persona.
    """
    extra_fields.setdefault('is_staff', True)
    extra_fields.setdefault('is_superuser', True)

    if persona is None:
      raise ValueError("El superusuario debe estar vinculado a una persona.")
    if facultad is None:
      raise ValueError("El superusuario debe pertenecer o a una facultad.")

    return self.create_user(codigoUser, nombreUser, claveUser, facultad, persona, **extra_fields)


class Facultad(models.TextChoices):
  FAUA = "faua", "Facultad de Arquitectura, Urbanismo y Artes"
  FIC = "fic", "Facultad de Ingeniería Civil"
  FIEECS = "fieecs", "Facultad de Ingeniería Económica, Estadística y Ciencias Sociales"
  FIGMM = "figmm", "Facultad de Ingeniería Geológica, Minera y Metalúrgica"
  FIEE = "fiee", "Facultad de Ingeniería Eléctrica y Electrónica"
  FIM = "fim", "Facultad de Ingeniería Mecánica"
  FC = "fc", "Facultad de Ciencias"
  FIPP = "fipp", "Facultad de Ingeniería de Petróleo, Gas Natural y Petroquímica"
  FIQT = "fiqt", "Facultad de Ingeniería Química y Textil"
  FIA = "fia", "Facultad de Ingeniería Ambiental"
  FIIS = "fiis", "Facultad de Ingeniería Industrial y de Sistemas"


class Usuario(AbstractBaseUser, PermissionsMixin):
  persona = models.OneToOneField(Persona, on_delete=models.CASCADE)
  codigoUsuario = models.CharField(max_length=64, unique=True)
  nombreUsuario = models.CharField(max_length=64)
  is_active = models.BooleanField(default=True)
  is_staff = models.BooleanField(default=False)
  facultad = models.CharField(
    max_length=128,
    choices=Facultad.choices,
  )  # CAMBIAR

  USERNAME_FIELD = 'codigoUsuario'
  REQUIRED_FIELDS = ['nombreUsuario', "facultad", "persona_id"]

  objects = UserManager()

  def __str__(self):
    return self.nombreUsuario

  class Meta:
    db_table = "usuario"


class EstadoDecano(models.TextChoices):
  ACTIVO = "activo", "Activo"
  INACTIVO = "inactivo", "Inactivo"


class Decano(models.Model):
  persona = models.OneToOneField(Persona, on_delete=models.CASCADE)
  estadoDecano = models.CharField(
    max_length=64,
    choices=EstadoDecano.choices,
  )

  class Meta:
    db_table = "decano"


class EstadoEncargadoConsejo(models.TextChoices):
  ACTIVO = "activo", "Activo"
  INACTIVO = "inactivo", "Inactivo"


class EncargadoConsejo(models.Model):
  persona = models.OneToOneField(Persona, on_delete=models.CASCADE)
  estadoEncargadoConsejo = models.CharField(
    max_length=64,
    choices=EstadoEncargadoConsejo.choices,
  )

  def __str__(self):
    return f"Encargado Consejo: {self.persona}"

  class Meta:
    db_table = "encargado_consejo"


class TipoConvocatoria(models.TextChoices):
  INTERNA = 'interna', 'Interna'
  EXTERNA = 'externa', 'Externa'


class EstadoConvocatoria(models.TextChoices):
  PUBLICADO = 'publicado', 'Publicado'
  EN_PROCESO = 'en_proceso', "En proceso"
  FINALIZADO = 'finalizado', 'Finalizado'


class Convocatoria(models.Model):
  descripcionConvocatoria = models.CharField(max_length=512)
  tipoConvocatoria = models.CharField(
    max_length=64,
    choices=TipoConvocatoria.choices,
  )
  fechaPublicacion = models.DateTimeField()
  fechaCierre = models.DateTimeField()
  fechaAsignacionTema = models.DateTimeField()
  fechaClaseMagistral = models.DateTimeField()
  estadoConvocatoria = models.CharField(
    max_length=64,
    choices=EstadoConvocatoria.choices,
  )

  class Meta:
    db_table = "convocatoria"


class EstadoPostulante(models.TextChoices):
  REGISTRADO = "registrado", "Registrado"
  ACEPTADO = "aceptado", "Aceptado"
  CALIFICADO = "calificado", "Calificado"
  APROBADO = "aprobado", "Desaprobado"
  DESAPROBADO = "desaprobado", "Desaprobado"
  RECHAZADO = "rechazado", "Rechazado"


class Postulante(models.Model):
  persona = models.ForeignKey(Persona, on_delete=models.CASCADE)
  convocatoria = models.ForeignKey(Convocatoria, on_delete=models.CASCADE)
  estadoPostulante = models.CharField(
    max_length=64,
    choices=EstadoPostulante.choices,
  )

  class Meta:
    db_table = "postulante"


class Curso(models.Model):
  nombreCurso = models.CharField(max_length=64)
  codigoCurso = models.CharField(max_length=20)
  creditosCurso = models.IntegerField()
  facultad = models.CharField(
    max_length=64,
    choices=Facultad.choices
  )

  class Meta:
    db_table = "curso"


class EstadoSeccion(models.TextChoices):
  ACTIVO = "activo", "Activo"
  INACTIVO = "inactivo", "Inactivo"


class Seccion(models.Model):
  curso = models.ForeignKey(
    Curso,
    on_delete=models.CASCADE,
  )
  codigoSeccion = models.CharField(max_length=20)
  estadoSeccion = models.CharField(
    max_length=20,
    choices=EstadoSeccion.choices,
  )

  class Meta:
    db_table = "seccion"

  @property
  def total_horas(self):
    total = timedelta()
    for horario in self.horario_set.all():
      inicio = datetime.combine(datetime.min, horario.horaInicio)
      fin = datetime.combine(datetime.min, horario.horaFin)
      duracion = fin - inicio
      total += duracion
    return round(total.total_seconds() / 3600, 0)
# Actualizar


class TipoPlaza(models.TextChoices):
  LABORATORIO = "laboratorio", "Laboratorio"
  PRACTICA = "practica", "Practica"
  TEORIA = "teoria", "Teoria"


class EstadoPlaza(models.TextChoices):
  ACTIVO = "activo", "Activo"
  INACTIVO = "inactivo", "Inactivo"


class Plaza(models.Model):
  convocatoria = models.ForeignKey(
    Convocatoria,
    on_delete=models.CASCADE,
  )
  seccion = models.ForeignKey(
    Seccion,
    on_delete=models.CASCADE
  )
  estadoPlaza = models.CharField(
    max_length=64,
    choices=EstadoPlaza.choices,
  )
  tipoPlaza = models.CharField(
    max_length=64,
    choices=TipoPlaza.choices,
  )

  class Meta:
    db_table = "plaza"


class Requisito(models.Model):
  plaza = models.ForeignKey(
    Plaza,
    on_delete=models.CASCADE
  )
  descripcion = models.CharField(max_length=128)
  vigencia = models.CharField(max_length=64)

  class Meta:
    db_table = "requisito"


class EstadoDocente(models.TextChoices):
  ACTIVO = "activo", "Activo"
  INACTIVO = "inactivo", "Inactivo"


class Docente(models.Model):
  persona = models.ForeignKey(
    Persona,
    on_delete=models.CASCADE,
  )
  estadoDocente = models.CharField(
    max_length=64,
    choices=EstadoDocente.choices,
  )

  class Meta:
    db_table = "docente"


class EvaluacionDocente(models.Model):
  seccion = models.ForeignKey(
    Seccion,
    on_delete=models.CASCADE
  )
  docente = models.ForeignKey(
    Docente,
    on_delete=models.CASCADE
  )
  notaEvaluacion = models.FloatField(null=True, blank=True)
  cicloAcademico = models.CharField(max_length=10)
  cantidadAlumnos = models.CharField(max_length=64)

  class Meta:
    db_table = "evaluacion_docente"


class DiaSemana(models.TextChoices):
  LUNES = "lunes", "Lunes"
  MARTES = "martes", "Martes"
  MIERCOLES = "miercoles", "Miércoles"
  JUEVES = "jueves", "Jueves"
  VIERNES = "viernes", "Viernes"
  SABADO = "sabado", "Sábado"


class Horario(models.Model):
  seccion = models.ForeignKey(
    Seccion,
    on_delete=models.CASCADE,
  )
  dia = models.CharField(
    max_length=15,
    choices=DiaSemana.choices,
  )
  horaInicio = models.TimeField()
  horaFin = models.TimeField()

  class Meta:
    db_table = "horario"


class Silabus(models.Model):
  curso = models.ForeignKey(
    Curso,
    on_delete=models.CASCADE
  )
  codigoSilabus = models.CharField(max_length=20)
  sistemaEvaluacion = models.CharField(max_length=32)
  fechaSilabus = models.DateField()

  class Meta:
    db_table = "silabus"


class Temas(models.Model):
  silabus = models.ForeignKey(
    Silabus,
    on_delete=models.CASCADE
  )
  codigoTema = models.CharField(max_length=20)
  nombreTema = models.CharField(max_length=32)
  duracionTema = models.IntegerField()

  class Meta:
    db_table = "temas"


class EstadoClaseMagistral(models.TextChoices):
  SOLICITADO = "solicitado", "Solicitado"
  PROGRAMADO = "programado", "Programado"
  INICIADA = "iniciada", "Iniciada"
  EN_PROCESO = "en_proceso", "En proceso"
  CALIFICADO = "calificado", "Calificado"
  FINALIZADO = "finalizado", "Finalizado"
  DOCUMENTADO = "documentado", "Documentado"


class ClaseMagistral(models.Model):
  postulante = models.OneToOneField(
    Postulante,
    on_delete=models.CASCADE
  )
  fechaProgramacion = models.DateField()
  horaProgramada = models.TimeField()
  temaAsignado = models.CharField(max_length=64)
  estadoClaseMagistral = models.CharField(
    max_length=64,
    choices=EstadoClaseMagistral.choices,
  )

  class Meta:
    db_table = "clase_magistral"


class TipoEvaluador(models.TextChoices):
  ALUMNO = "alumno", "Alumno"
  DOCENTE = "docente", "Docente"


class EstadoEvaluador(models.TextChoices):
  CONVOCADO = "convocado", "Convocado"
  CONFIRMADO = "confirmado", "Confirmado"
  PRESENTE = "presente", "Presente"
  AUSENTE = "ausente", "Ausente"


class JerarquiaEvaluador(models.TextChoices):
  PRINCIPAL = "alumno", "Alumno"
  SECUNDARIO = "docente", "Docente"


class Evaluador(models.Model):
  persona = models.ForeignKey(Persona, on_delete=models.CASCADE, null=True)
  tipoEvaluador = models.CharField(
    max_length=64,
    choices=TipoEvaluador.choices,
  )
  estadoEvaluador = models.CharField(
    max_length=64,
    choices=EstadoEvaluador.choices,
  )

  def __str__(self):
    return f"{self.persona.nombre} ({self.tipoEvaluador})"

  class Meta:
    db_table = "evaluador"


class EstadoDocumento(models.TextChoices):
  REGISTRADO = "registrado", "Registrado"
  EN_REVISION = "en_revision", "En revisión"
  RECHAZADO = "rechazado", "Rechazado"
  ACEPTADO = "aceptado", "Aceptado"
  CALIFICADO = "calificado", "Calificado"


class Documento(models.Model):
  postulante = models.ForeignKey(
    Postulante,
    on_delete=models.CASCADE
  )
  tipoDocumento = models.CharField(max_length=64)
  archivo = models.BinaryField(editable=True)
  fechaRecepcion = models.DateField()
  estadoDocumento = models.CharField(
    max_length=64,
    choices=EstadoDocumento.choices,
  )

  class Meta:
    db_table = "documento"

  def descargar_url(self):
    return reverse('descargar_pdf', args=[str(self.id)])

  def __str__(self):
    return f"{self.tipoDocumento} - {self.fechaRecepcion}"


class EstadoNotaPostulante(models.TextChoices):
  POR_CALIFICAR = "por_calificar", "Por Calificar"
  REVISADO_PARCIALMENTE = "revisado_parcialmente", "Revisado Parcialmente"
  COMPLETO = "completo", "Completo"


class NotaPostulante(models.Model):
  evaluador = models.ForeignKey(
    Evaluador,
    on_delete=models.CASCADE
  )
  postulante = models.ForeignKey(
    Postulante,
    on_delete=models.CASCADE
  )
  notaClaseCriterio1 = models.IntegerField(default=0)
  notaClaseCriterio2 = models.IntegerField(default=0)
  notaClaseCriterio3 = models.IntegerField(default=0)
  notaClaseCriterio4 = models.IntegerField(default=0)
  notaDocumentoCriterio1 = models.IntegerField()
  notaDocumentoCriterio2 = models.IntegerField()
  notaDocumentoCriterio3 = models.IntegerField()
  notaDocumentoCriterio4 = models.IntegerField()
  notaDocumentoCriterio5 = models.IntegerField()
  notaDocumentoCriterio6 = models.IntegerField()
  estadoNotaPostulante = models.CharField(
    max_length=64,
    choices=EstadoNotaPostulante.choices,
    default=EstadoNotaPostulante.POR_CALIFICAR
      )

  class Meta:
    db_table = "nota_postulante"
