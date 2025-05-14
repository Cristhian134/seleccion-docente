from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core_apps.common.models import Persona
from dotenv import load_dotenv
import os


class Command(BaseCommand):
    help = 'Crea un superusuario y su Persona asociada'

    def handle(self, *args, **options):
        # Cargar las variables de entorno desde el archivo .env
        load_dotenv()

        # 1. Crear Persona
        persona = Persona.objects.create(
            nombre=os.getenv('SUPERUSER_NOMBRE'),
            apellidoPaterno=os.getenv('SUPERUSER_APELLIDO_PAT'),
            apellidoMaterno=os.getenv('SUPERUSER_APELLIDO_MAT'),
            dni=os.getenv('SUPERUSER_DNI'),
            correo=os.getenv('SUPERUSER_CORREO'),
            telefono=os.getenv('SUPERUSER_TELEFONO'),
            genero=os.getenv('SUPERUSER_GENERO')
        )

        # 2. Crear Usuario
        User = get_user_model()
        user = User.objects.create_superuser(
            codigoUser=os.getenv('SUPERUSER_CODIGO'),
            nombreUser=os.getenv('SUPERUSER_USERNAME'),
            claveUser=os.getenv('SUPERUSER_PASSWORD'),
            persona=persona,
            facultad=os.getenv('SUPERUSER_FACULTAD')
        )

        self.stdout.write(self.style.SUCCESS(f'Superusuario creado: {user}'))
