# User Service

This microservice is part of bigger project for SWA course at CTU. 
The goal of this service is to:
1. register user
1. authenticate and authorize user

The auth is using well known method of JWTs.
The passwords in the database are hashed using `bcrypt`.
For persistence, this service has its own PostgreSQL database.

## API
To test API, one can use pregenerated Swagger UI running on `localhost:8080`.

### Contract Tests
For contract tests refer to https://github.com/LukasForst/SWA-TP-user-service-contract-tests 

## Monitoring
The service contains `/metrics` endpoint for Prometheus scraping.
This endpoint is enabled only when the service uses `gunicorn` as its server (i.e. while running in production/docker).

It is possible to enable logging in JSON structure for simple usage with ELK stack.
To enable it, set env variable `JSON_LOGGING=true`.

To enable deployment to Kubernetes, service contains `/status` endpoint for L7 load balancers and Ingress checks.

This service also has complete monitoring of requests by utilizing request id generation and reading `X-Request-Id` 
headers (can be found in `RequestId.py` file) - these ids are then logged with every log record 
when using JSON logging.
Thus this service is ready to be deployed to production level K8S cluster.

## Versioning
The service contains `/version` endpoint which returns current build version - when using docker image from
docker hub `lukaswire/swa-user-service` it returns SHA of the commit it was built on.
When built locally, it returns `development` version.

## Deployment
The service is distributed as single docker image using multistage docker build based on the
`python:3.7-slim` - not `alpine`, because PostgreSQL drivers can not be currently installed on Alpine images.

## Configuration
By default, the service uses configuration from file `local_config.py`.
All configuration can be overriden by setting same named env variable to different value.

## Pipelines
This repo contains only simple pipelines - each commit to master is deployed to Docker Hub with `latest` tag
and `/version` endpoint set. 
This repo is using Github Actions.