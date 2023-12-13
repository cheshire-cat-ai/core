normal=docker-compose.yml
full=docker-compose-full.yml

env=normal

compose=$(if $(filter normal,${env}),${normal},${full})

build:
	docker compose -f ${compose} build --no-cache

up:
	docker compose -f ${compose} up -d

down:
	docker compose -f ${compose} down

stop:
	docker compose -f ${compose} stop