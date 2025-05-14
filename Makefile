build:
	docker compose -f local.yml up --build -d --remove-orphans

up:
	docker compose -f local.yml up -d

down:
	docker compose -f local.yml down

down-v:
	docker compose -f local.yml down -v

banker-config:
	docker compose -f local.yml config

makemigration:
	docker compose -f local.yml run --rm seleccion-docente python manage.py makemigrations

migrate:
	docker compose -f local.yml run --rm seleccion-docente python manage.py migrate

collectstatic:
	docker compose -f local.yml run --rm seleccion-docente python manage.py collectstatic --no-input --clear

superuser:
	docker compose -f local.yml run --rm seleccion-docente python manage.py create_superuser

flush:
	docker compose -f local.yml run --rm seleccion-docente python manage.py flush

network-inspect:
	docker network inspect seleccion_docente_nw

banker-db:
	docker compose -f local.yml exec postgres psql --username=postgres --dbname=banker