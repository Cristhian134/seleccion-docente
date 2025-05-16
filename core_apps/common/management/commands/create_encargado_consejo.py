from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core_apps.common.models import Persona
from core_apps.common.models import EncargadoConsejo
from dotenv import load_dotenv
import os


class Command(BaseCommand):
  help = 'Crea un usuario tipo EncargadoConsejo y su Persona asociada'

  def handle(self, *args, **options):
    load_dotenv()

    # Datos de Persona
    nombre = os.getenv('ENCARGADO_NOMBRE')
    apellido_pat = os.getenv('ENCARGADO_APELLIDO_PAT')
    apellido_mat = os.getenv('ENCARGADO_APELLIDO_MAT')
    dni = os.getenv('ENCARGADO_DNI')
    correo = os.getenv('ENCARGADO_CORREO')
    telefono = os.getenv('ENCARGADO_TELEFONO')
    genero = os.getenv('ENCARGADO_GENERO')

    # Datos de Usuario
    codigo_user = os.getenv('ENCARGADO_CODIGO')
    username = os.getenv('ENCARGADO_USERNAME')
    password = os.getenv('ENCARGADO_PASSWORD')
    facultad = os.getenv('ENCARGADO_FACULTAD')

    # Validaciones básicas
    missing_vars = [var for var in [
        ('ENCARGADO_NOMBRE', nombre),
        ('ENCARGADO_APELLIDO_PAT', apellido_pat),
        ('ENCARGADO_DNI', dni),
        ('ENCARGADO_CORREO', correo),
        ('ENCARGADO_CODIGO', codigo_user),
        ('ENCARGADO_USERNAME', username),
        ('ENCARGADO_PASSWORD', password)
    ] if not var[1]]

    if missing_vars:
      self.stderr.write(self.style.ERROR(f'Faltan variables de entorno: {", ".join([v[0] for v in missing_vars])}'))
      return

    # Crear o recuperar Persona
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

    if User.objects.filter(codigoUsuario=codigo_user).exists():
      self.stdout.write(self.style.WARNING(f'Usuario con código {codigo_user} ya existe.'))
      return

    if User.objects.filter(nombreUsuario=username).exists():
      self.stdout.write(self.style.WARNING(f'Usuario con username {username} ya existe.'))
      return

    # Crear usuario sin permisos (is_staff=True para login, pero sin visibilidad)
    try:
      user = User.objects.create_user(
        codigoUser=codigo_user,
        nombreUser=username,
        claveUser=password,
        persona=persona,
        facultad=facultad,
        is_staff=True,     # Puede iniciar sesión
        is_superuser=False  # No es superusuario
      )
      self.stdout.write(self.style.SUCCESS(f'Usuario Encargado creado: {user}'))
    except Exception as e:
      self.stderr.write(self.style.ERROR(f'Error creando usuario: {e}'))
      return

    # Crear EncargadoConsejo
    try:
      encargado = EncargadoConsejo.objects.create(
        persona=persona,
        estadoEncargadoConsejo='activo'
      )
      self.stdout.write(self.style.SUCCESS(f'EncargadoConsejo creado: {encargado}'))
    except Exception as e:
      self.stderr.write(self.style.ERROR(f'Error creando EncargadoConsejo: {e}'))


class Command(BaseCommand):
  help = 'Crea un usuario tipo EncargadoConsejo y su Persona asociada'

  def handle(self, *args, **options):
    load_dotenv()

    # Datos de Persona
    nombre = os.getenv('ENCARGADO_NOMBRE')
    apellido_pat = os.getenv('ENCARGADO_APELLIDO_PAT')
    apellido_mat = os.getenv('ENCARGADO_APELLIDO_MAT')
    dni = os.getenv('ENCARGADO_DNI')
    correo = os.getenv('ENCARGADO_CORREO')
    telefono = os.getenv('ENCARGADO_TELEFONO')
    genero = os.getenv('ENCARGADO_GENERO')

    # Datos de Usuario
    codigo_user = os.getenv('ENCARGADO_CODIGO')
    username = os.getenv('ENCARGADO_USERNAME')
    password = os.getenv('ENCARGADO_PASSWORD')
    facultad = os.getenv('ENCARGADO_FACULTAD')

    # Validaciones básicas
    missing_vars = [var for var in [
        ('ENCARGADO_NOMBRE', nombre),
        ('ENCARGADO_APELLIDO_PAT', apellido_pat),
        ('ENCARGADO_DNI', dni),
        ('ENCARGADO_CORREO', correo),
        ('ENCARGADO_CODIGO', codigo_user),
        ('ENCARGADO_USERNAME', username),
        ('ENCARGADO_PASSWORD', password)
    ] if not var[1]]

    if missing_vars:
      self.stderr.write(self.style.ERROR(f'Faltan variables de entorno: {", ".join([v[0] for v in missing_vars])}'))
      return

    # Crear o recuperar Persona
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

    if User.objects.filter(codigoUsuario=codigo_user).exists():
      self.stdout.write(self.style.WARNING(f'Usuario con código {codigo_user} ya existe.'))
      return

    if User.objects.filter(nombreUsuario=username).exists():
      self.stdout.write(self.style.WARNING(f'Usuario con username {username} ya existe.'))
      return

    # Crear usuario sin permisos (is_staff=True para login, pero sin visibilidad)
    try:
      user = User.objects.create_user(
        codigoUser=codigo_user,
        nombreUser=username,
        claveUser=password,
        persona=persona,
        facultad=facultad,
        is_staff=True,     # Puede iniciar sesión
        is_superuser=False  # No es superusuario
      )
      self.stdout.write(self.style.SUCCESS(f'Usuario Encargado creado: {user}'))
    except Exception as e:
      self.stderr.write(self.style.ERROR(f'Error creando usuario: {e}'))
      return

    # Crear EncargadoConsejo
    try:
      encargado = EncargadoConsejo.objects.create(
        persona=persona,
        estadoEncargadoConsejo='activo'
      )
      self.stdout.write(self.style.SUCCESS(f'EncargadoConsejo creado: {encargado}'))
    except Exception as e:
      self.stderr.write(self.style.ERROR(f'Error creando EncargadoConsejo: {e}'))
