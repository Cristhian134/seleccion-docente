from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core_apps.common.models import EstadoEvaluador, Evaluador, Persona, TipoEvaluador
from dotenv import load_dotenv
import os


class Command(BaseCommand):
  help = 'Crea un superusuario y su Persona asociada'

  def handle(self, *args, **options):
    load_dotenv()

    # Obtener datos de entorno
    nombre = os.getenv('SUPERUSER_NOMBRE')
    apellido_pat = os.getenv('SUPERUSER_APELLIDO_PAT')
    apellido_mat = os.getenv('SUPERUSER_APELLIDO_MAT')
    dni = os.getenv('SUPERUSER_DNI')
    correo = os.getenv('SUPERUSER_CORREO')
    telefono = os.getenv('SUPERUSER_TELEFONO')
    genero = os.getenv('SUPERUSER_GENERO')

    codigo_user = os.getenv('SUPERUSER_CODIGO')
    username = os.getenv('SUPERUSER_USERNAME')
    password = os.getenv('SUPERUSER_PASSWORD')
    facultad = os.getenv('SUPERUSER_FACULTAD')

    # Validar que los campos obligatorios existan
    missing_vars = [var for var in [
        ('SUPERUSER_NOMBRE', nombre),
        ('SUPERUSER_APELLIDO_PAT', apellido_pat),
        ('SUPERUSER_DNI', dni),
        ('SUPERUSER_CORREO', correo),
        ('SUPERUSER_CODIGO', codigo_user),
        ('SUPERUSER_USERNAME', username),
        ('SUPERUSER_PASSWORD', password)
    ] if not var[1]]

    if missing_vars:
      self.stderr.write(self.style.ERROR(f'Faltan variables de entorno: {", ".join([v[0] for v in missing_vars])}'))
      return

    # Evitar duplicados: buscar Persona existente por DNI o correo
    persona, created_persona = Persona.objects.get_or_create(
        dni=dni,
        defaults={
            'nombre': nombre,
            'apellidoPaterno': apellido_pat,
            'apellidoMaterno': apellido_mat,
            'correo': correo,
            'telefono': telefono,
            'genero': genero,
        }
    )

    if created_persona:
      self.stdout.write(self.style.SUCCESS(f'Persona creada: {persona}'))
    else:
      self.stdout.write(self.style.WARNING(f'Persona con DNI {dni} ya existe: {persona}'))

    User = get_user_model()

    # Verificar si usuario con ese código o username ya existe
    if User.objects.filter(codigoUsuario=codigo_user).exists():
      self.stdout.write(self.style.WARNING(f'Usuario con código {codigo_user} ya existe. No se creó nuevo usuario.'))
      return
    if User.objects.filter(nombreUsuario=username).exists():
      self.stdout.write(self.style.WARNING(f'Usuario con username {username} ya existe. No se creó nuevo usuario.'))
      return

    # Crear superusuario
    try:
      user = User.objects.create_superuser(
          codigoUser=codigo_user,
          nombreUser=username,
          claveUser=password,
          persona=persona,
          facultad=facultad,
          is_staff=True,     # Puede iniciar sesión
          is_superuser=True  # No es superusuario
      )

      Evaluador.objects.create(
        persona=persona,
        tipoEvaluador=TipoEvaluador.DOCENTE,
        estadoEvaluador=EstadoEvaluador.CONFIRMADO,
      )
      self.stdout.write(self.style.SUCCESS(f'Superusuario creado: {user}'))
    except Exception as e:
      self.stderr.write(self.style.ERROR(f'Error creando superusuario: {e}'))
