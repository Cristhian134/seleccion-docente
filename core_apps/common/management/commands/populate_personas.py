from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core_apps.common.models import (
    EvaluacionDocente, Persona, Decano, EncargadoConsejo, Docente,
    Facultad, EstadoDecano, EstadoEncargadoConsejo, EstadoDocente
)

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


class Command(BaseCommand):
  help = 'Crea personas: 1 decano, 2 encargados de consejo y 10 docentes por facultad.'

  def handle(self, *args, **options):
    fake = Faker(locale='es_ES')
    facultades = [choice[1] for choice in Facultad.choices]
    User = get_user_model()
    CICLO_ACADEMICO = "2025-1"
    contador_nota_evaluacion = 1

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
          is_staff=True,     # Puede iniciar sesión
          is_superuser=False  # No es superusuario
      )

      self.stdout.write(self.style.SUCCESS(
        f'Decano creado para {facultad}: Usuario {codigoDecano} | Password {codigoDecano} | Persona {persona_decano}'))

      # Encargados de consejo
      for i in range(2):
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
          is_staff=True,     # Puede iniciar sesión
          is_superuser=False  # No es superusuario
        )

        self.stdout.write(self.style.SUCCESS(
          f'Encargado consejo {i+1} creado para {facultad}: Usuario {codigoEncargado} | Password {codigoEncargado} | Persona {persona_enc}'))

      # Docentes
      for i in range(10):
        persona_doc = Persona.objects.create(
            nombre=fake.first_name(),
            apellidoPaterno=fake.last_name(),
            apellidoMaterno=fake.last_name(),
            dni=str(fake.unique.random_number(digits=8)),  # Asegurar 8 dígitos
            correo=fake.unique.email(),
            telefono=str(fake.random_number(digits=9)),  # Ajustar longitud
            genero=random.choice([g[0] for g in Persona._meta.get_field('genero').choices])
        )
        docente = Docente.objects.create(
            persona=persona_doc,
            estadoDocente=EstadoDocente.ACTIVO
        )

        if contador_nota_evaluacion < 15:

          EvaluacionDocente.objects.create(
            seccion_id=contador_nota_evaluacion,
            docente=docente,
            notaEvaluacion=round(random.uniform(8, 20), 2),
            cicloAcademico=CICLO_ACADEMICO,
            cantidadAlumnos=random.randint(25, 35),
          )

        contador_nota_evaluacion += 1

        self.stdout.write(self.style.SUCCESS(f'Docente {i+1} creado para {facultad}: {persona_doc}'))

      self.stdout.write("\n")

    self.stdout.write(self.style.SUCCESS('Proceso de creación de personas completado.'))
