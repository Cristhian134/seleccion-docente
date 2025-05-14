# Sistema de Selección Docente

# 1. Frontend

# 1.1. Iconos

Usados de fontawesome https://fontawesome.com/v4/icons/

Ejemplo:
```html
<i class="fa fa-calendar" aria-hidden="true"></i>
```

# 2. Backend

# 2.1. Acceso a pdfs

Para acceder a un documento, es necesario estar logueado y utilizar la URL:
```
http://localhost:8080/descargar-pdf/<documento_id>
```

# 2. Ejecución

# 2.1. Virtualenv

1. Ejecutar en CMD
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

4. Desactivar entorno virtual
```
venv\Scripts\deactivate
```

# 2.2. Pipenv

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
4. Salir del entorno virtual de Pipenv
```
exit
```

# 2.3. Docker
1. Windows
```
docker compose -f local.yml up --build -d --remove-orphans
``` 
2. Linux
```
make build
``` 