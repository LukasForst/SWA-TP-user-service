docker-build:
	docker build -t lukaswire/swa-user-service .

docker-run: docker-build
	docker run --rm -p 8080:8080 lukaswire/swa-user-service

publish: docker-build
	docker push lukaswire/swa-user-service

db:
	docker-compose up -d user-service-db

up:
	docker-compose up