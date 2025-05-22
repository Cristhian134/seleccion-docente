# Sistema de Selección Docente

## Login:
```
http://localhost:8000/login/
```

## Admin:
```
http://localhost:8000/admin/
```

# Módulos
```
http://localhost:8000/ver-convocatorias/
```
```
http://localhost:8000/descargar-pdf/<documento-id>/
```
## Listar Docentes
```
http://localhost:8000/listar-docentes/
```
## Crear Convocatoria
```
http://localhost:8000/crear-convocatoria/
```
```
http://localhost:8000/crear-convocatoria/convocatoria-externa/
```
```
http://localhost:8000/crear-convocatoria/convocatoria-interna/
```
## Ver Convocatorias
```
http://localhost:8000/ver_convocatorias/
```
```
http://localhost:8000/ver_convocatorias/gestionar_documentos/<convocatoria-id>/
```

# 1. Puertos

|Servicio|Puerto Host|Puerto Contenedor|
|--------|-----------|-----------------|
|Django|No expuesto|8000|
|Nginx|8080|80|
|Postgres|5432|5432|

# 2. Frontend

# 2.1. Iconos

Usados de fontawesome https://fontawesome.com/v4/icons/

Ejemplo:
```html
<i class="fa fa-calendar" aria-hidden="true"></i>
```

# 3. Backend

# 3.1. Acceso a pdfs

Para acceder a un documento, es necesario estar logueado y utilizar la URL:
```
http://localhost:8000/descargar-pdf/<documento_id>
```

# 4. Ejecución

# 4.1. Virtualenv

Cambiar en .env.local la variable POSTGRES_HOST a localhost
```
POSTGRES_HOST="localhost"
``` 

1. Ejecutar en CMD (verificar, vs utiliza PS por defecto)
```
python -m venv venv
```

2. Activar entorno virtual
```
venv\Scripts\activate
```

3. Instalar dependencias
```
pip install -r requirements/local.txt
```

4. Ejecutar setup.py
```
python setup.py
```

5. Desactivar entorno virtual
```
venv\Scripts\deactivate
```

# 4.2. Pipenv

Cambiar en .env.local la variable POSTGRES_HOST a localhost
```
POSTGRES_HOST="localhost"
``` 

1. Instalar pipenv
```
pip install pipenv
```

2. Instalar dependencias con pipenv
```
pipenv install
```

3. Activar entorno virtual de Pipenv
```
pipenv Shell
```

4. Ejecutar setup.py
```
python setup.py
```

5. Salir del entorno virtual de Pipenv
```
exit
```

# 4.3. Docker

En ambos casos cambiar en .env.local la variable POSTGRES_HOST a postgres
```
POSTGRES_HOST="postgres"
``` 

1. Windows
```
docker compose -f local.yml up --build -d --remove-orphans
``` 
2. Linux
```
make build
``` 

# 4.4. Python

1. Instalar dependencias
```
pip install -r requirements/local.txt
```

2. Ejecutar python setup.py
```
python setup.py
```

# 5. Usuarios en produccion

Superuser

```
bQi4kn_b83kJo_9SfiVDCUfKrg4
```
Contraseña
```
bQi4kn_b83kJo_9SfiVDCUfKrg4
```

Encargado consejo

Usuario
```
juanp
```
Contraseña
```
juanp
```