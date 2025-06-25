from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core_apps.common.models import (
    Curso, DiaSemana, EstadoEvaluador, EvaluacionDocente, Evaluador, Horario, Persona, Decano, EncargadoConsejo, Docente,
    Facultad, EstadoDecano, EstadoEncargadoConsejo, EstadoDocente, Seccion, Silabus, Temas, TipoEvaluador
)

from datetime import datetime, timedelta
from faker import Faker
import random
import string


def generar_codigo():
  # Parte fija del año
  año = "2025"

  # Generar número secuencial de 4 dígitos (0000-9999)
  numero = f"{random.randint(0, 9999):04d}"

  # Generar letra mayúscula aleatoria (A-Z)
  letra = random.choice(string.ascii_uppercase)

  # Combinar todo en el formato deseado
  codigo = f"{año}{numero}{letra}"

  return codigo


def generar_nota_evaluacion():
  # 14 x 3 = 42
  return


def generar_horario_aleatorio():
  # Definir las horas base: desde las 06:00 hasta las 22:00
  hora_min = datetime.strptime("06:00", "%H:%M")
  hora_max = datetime.strptime("22:00", "%H:%M")

  # Generar bloques posibles de inicio (cada 30 min)
  bloques = []
  actual = hora_min
  while actual <= hora_max - timedelta(hours=1):  # al menos 1 hora de duración
    bloques.append(actual)
    actual += timedelta(minutes=30)

  # Escoger hora de inicio aleatoriamente
  hora_inicio = random.choice(bloques)

  # Duración aleatoria entre 1h y 4h (en pasos de 30 min)
  duraciones_min = [60, 90, 120, 150, 180, 210, 240]
  duracion = timedelta(minutes=random.choice(duraciones_min))

  hora_fin = hora_inicio + duracion

  # Asegurar que no se pase de las 23:59
  if hora_fin > datetime.strptime("23:59", "%H:%M"):
    hora_fin = datetime.strptime("23:59", "%H:%M")

  return {
      "horaInicio": hora_inicio.strftime("%H:%M"),
      "horaFin": hora_fin.strftime("%H:%M")
  }


class Command(BaseCommand):
  help = 'Crea personas: 1 decano, 2 encargados de consejo y 10 docentes por facultad.'

  def handle(self, *args, **options):
    fake = Faker(locale='es_ES')
    facultades = [choice[1] for choice in Facultad.choices]
    # facultades = [
    #   Facultad.FAUA,
    #   Facultad.FC,
    #   Facultad.FIA,
    #   Facultad.FIC,
    #   Facultad.FIEE,
    #   Facultad.FIEECS,
    #   Facultad.FIGMM,
    #   Facultad.FIM,
    #   Facultad.FIPP,
    #   Facultad.FIQT,
    #   Facultad.FIIS,
    # ]
    User = get_user_model()
    CICLO_ACADEMICO = "2025-1"
    TOTAL_SECCIONES = 28

    TOTAL_ENCARGADOS_CONSEJO = 2
    TOTAL_DOCENTES_POR_FACULTAD = 10
    TOTAL_EVALUADOR_DOCENTE_POR_FACULTAD = 1
    TOTAL_EVALUADOR_ALUMNO_POR_DOCENTE = 2
    TOTAL_TEMAS_POR_CURSO = 20

    contador_nota_evaluacion = 1

    # Crear horarios para cada seccion
    secciones = Seccion.objects.all()

    for k, seccion in enumerate(secciones):
      # Elegir 2 días al azar sin repetir
      dias_disponibles = [
        ("lunes", DiaSemana.LUNES),
        ("martes", DiaSemana.MARTES),
        ("miércoles", DiaSemana.MIERCOLES),
        ("jueves", DiaSemana.JUEVES),
        ("viernes", DiaSemana.VIERNES),
        ("sábado", DiaSemana.SABADO),
      ]
      dias_elegidos = random.sample(dias_disponibles, 2)

      for _, dia_const in dias_elegidos:
        horario_dic = generar_horario_aleatorio()
        Horario.objects.create(
          seccion=seccion,
          dia=dia_const,
          horaInicio=horario_dic["horaInicio"],
          horaFin=horario_dic["horaFin"],
        )

    # Crear silabos y temas
    cursos = Curso.objects.all()
    sistemas_evaluacion = ["F", "G", "H", "I", "J"]
    fecha_silabus = "2018-06-10"
    for curso in cursos:
      silabus = Silabus.objects.create(
        curso=curso,
        fechaSilabus=fecha_silabus,
        sistemaEvaluacion=random.choice(sistemas_evaluacion),
        codigoSilabus=curso.codigoCurso,
      )

      for i in range(TOTAL_TEMAS_POR_CURSO):
        Temas.objects.create(
          silabus=silabus,
          codigoTema=f'{curso.codigoCurso}-TEM{str(i+1).zfill(2)}',
          nombreTema=f'Tema {i+1} - {curso.codigoCurso}',
          duracionTema=2,
        )

    # Crear usuarios decano, encargado consejo, evaluador (acceso al sistema) y docente
    for facultad in facultades:
      # Decano
      persona_decano = Persona.objects.create(
          nombre=fake.first_name(),
          apellidoPaterno=fake.last_name(),
          apellidoMaterno=fake.last_name(),
          dni=str(fake.unique.random_number(digits=8)),  # Asegurar 8 dígitos para DNI
          correo=fake.unique.email(),
          telefono=str(fake.random_number(digits=9)),  # Ajustar longitud del teléfono
          genero=random.choice([g[0] for g in Persona._meta.get_field('genero').choices])
      )
      Decano.objects.create(
          persona=persona_decano,
          estadoDecano=EstadoDecano.ACTIVO
      )

      codigoDecano = generar_codigo()

      User.objects.create_superuser(
          codigoUser=codigoDecano,
          nombreUser=codigoDecano,
          claveUser=codigoDecano,
          persona=persona_decano,
          facultad=facultad,
          is_staff=False,     # Puede iniciar sesión
          is_superuser=False  # No es superusuario
      )

      self.stdout.write(self.style.SUCCESS(
        f'Decano creado para {facultad}: Usuario {codigoDecano} | Password {codigoDecano} | Persona {persona_decano}'))

      # Encargados de consejo
      for i in range(TOTAL_ENCARGADOS_CONSEJO):
        persona_enc = Persona.objects.create(
            nombre=fake.first_name(),
            apellidoPaterno=fake.last_name(),
            apellidoMaterno=fake.last_name(),
            dni=str(fake.unique.random_number(digits=8)),  # Asegurar 8 dígitos
            correo=fake.unique.email(),
            telefono=str(fake.random_number(digits=9)),  # Ajustar longitud
            genero=random.choice([g[0] for g in Persona._meta.get_field('genero').choices])
        )
        EncargadoConsejo.objects.create(
            persona=persona_enc,
            estadoEncargadoConsejo=EstadoEncargadoConsejo.ACTIVO
        )

        codigoEncargado = generar_codigo()

        User.objects.create_superuser(
          codigoUser=codigoEncargado,
          nombreUser=codigoEncargado,
          claveUser=codigoEncargado,
          persona=persona_enc,
          facultad=facultad,
          is_staff=False,     # Puede iniciar sesión
          is_superuser=False  # No es superusuario
        )

        self.stdout.write(self.style.SUCCESS(
          f'Encargado consejo {i+1} creado para {facultad}: Usuario {codigoEncargado} | Password {codigoEncargado} | Persona {persona_enc}'))

      # Docentes
      for i in range(TOTAL_DOCENTES_POR_FACULTAD):
        persona_doc_dni = str(fake.unique.random_number(digits=8))
        persona_doc = Persona.objects.create(
            nombre=fake.first_name(),
            apellidoPaterno=fake.last_name(),
            apellidoMaterno=fake.last_name(),
            dni=persona_doc_dni,  # Asegurar 8 dígitos
            correo=fake.unique.email(),
            telefono=str(fake.random_number(digits=9)),  # Ajustar longitud
            genero=random.choice([g[0] for g in Persona._meta.get_field('genero').choices])
        )
        docente = Docente.objects.create(
            persona=persona_doc,
            estadoDocente=EstadoDocente.ACTIVO
        )

        if i < TOTAL_EVALUADOR_DOCENTE_POR_FACULTAD:
          Evaluador.objects.create(
            persona=persona_doc,
            tipoEvaluador=TipoEvaluador.DOCENTE,
            estadoEvaluador=EstadoEvaluador.CONFIRMADO,
          )

          codigoDocenteEval = generar_codigo()

          User.objects.create_superuser(
            codigoUser=codigoDocenteEval,
            nombreUser=codigoDocenteEval,
            claveUser=codigoDocenteEval,
            persona=persona_doc,
            facultad=facultad,
            is_staff=False,     # Puede iniciar sesión
            is_superuser=False  # No es superusuario
          )

          self.stdout.write(self.style.SUCCESS(
            f'  Evaluador Docente {i+1} creado para {facultad}: Usuario {codigoDocenteEval} | Password {codigoDocenteEval} | Persona {persona_doc}'))

          for j in range(TOTAL_EVALUADOR_ALUMNO_POR_DOCENTE):
            persona_alumno_eval = Persona.objects.create(
                nombre=fake.first_name(),
                apellidoPaterno=fake.last_name(),
                apellidoMaterno=fake.last_name(),
                dni=str(fake.unique.random_number(digits=8)),  # Asegurar 8 dígitos
                correo=fake.unique.email(),
                telefono=str(fake.random_number(digits=9)),  # Ajustar longitud
                genero=random.choice([g[0] for g in Persona._meta.get_field('genero').choices])
            )

            Evaluador.objects.create(
              persona=persona_alumno_eval,
              tipoEvaluador=TipoEvaluador.ALUMNO,
              estadoEvaluador=EstadoEvaluador.CONFIRMADO,
            )

            codigoAlumno = generar_codigo()

            User.objects.create_superuser(
              codigoUser=codigoAlumno,
              nombreUser=codigoAlumno,
              claveUser=codigoAlumno,
              persona=persona_alumno_eval,
              facultad=facultad,
              is_staff=False,     # Puede iniciar sesión
              is_superuser=False  # No es superusuario
            )

            self.stdout.write(self.style.SUCCESS(
              f'  Evaluador Alumno {j+1} creado para {facultad}: Usuario {codigoAlumno} | Password {codigoAlumno} | Persona {persona_alumno_eval}'))

        if contador_nota_evaluacion < TOTAL_SECCIONES:

          if i == 0 or contador_nota_evaluacion == 10:
            EvaluacionDocente.objects.create(
              seccion_id=contador_nota_evaluacion,
              docente=docente,
              cicloAcademico=CICLO_ACADEMICO,
              cantidadAlumnos=random.randint(25, 35),
            )
          else:
            EvaluacionDocente.objects.create(
              seccion_id=contador_nota_evaluacion,
              docente=docente,
              notaEvaluacion=round(random.uniform(8, 20), 2),
              cicloAcademico=CICLO_ACADEMICO,
              cantidadAlumnos=random.randint(25, 35),
            )

        contador_nota_evaluacion += 1

        self.stdout.write(self.style.SUCCESS(f'Docente {i+1} creado para {facultad}: {persona_doc} {persona_doc_dni}'))

      self.stdout.write("\n")

    self.stdout.write(self.style.SUCCESS('Proceso de creación de personas completado.'))
