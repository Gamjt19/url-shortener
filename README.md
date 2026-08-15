Containerized URL Shortener Platform

A production-style, containerized URL Shortener platform built using Python, FastAPI, PostgreSQL, Redis, Docker, Docker Compose, and Nginx, with CI/CD automation using GitHub Actions and Docker Hub.

The project demonstrates practical DevOps concepts including containerization, multi-stage Docker builds, container networking, persistent storage, health checks, reverse proxying, security, image scanning, and CI/CD.

⸻

📌 Project Objective

Build and deploy a scalable URL Shortener platform that can:

* Accept a long URL
* Generate a unique short URL
* Redirect users using the short URL
* Track the number of clicks
* Display URL statistics
* Store persistent data in PostgreSQL
* Use Redis for caching
* Run the entire platform using Docker
* Automate build, testing, security scanning, and Docker image publishing through GitHub Actions

⸻

🏗️ Architecture

                         Internet
                            │
                            ▼
                     ┌─────────────┐
                     │    Nginx    │
                     │     :80     │
                     └──────┬──────┘
                            │
                         app:8000
                            │
                            ▼
                     ┌─────────────┐
                     │   FastAPI   │
                     │ Application │
                     └──────┬──────┘
                            │
                 ┌──────────┴──────────┐
                 │                     │
                 ▼                     ▼
          ┌─────────────┐       ┌─────────────┐
          │ PostgreSQL  │       │    Redis    │
          │    :5432    │       │    :6379    │
          └──────┬──────┘       └──────┬──────┘
                 │                     │
                 ▼                     ▼
          postgres-data          redis-data

Request Flow

Client
  │
  ▼
Nginx :80
  │
  ▼
FastAPI :8000
  │
  ├── PostgreSQL → Persistent URL data
  │
  └── Redis → Cached URL mapping

PostgreSQL and Redis are not directly exposed to the host machine.

⸻

🛠️ Technology Stack

Technology	Purpose
Python	Application development
FastAPI	REST API
PostgreSQL	Persistent database
Redis	Caching
Docker	Containerization
Docker Compose	Multi-container orchestration
Nginx	Reverse proxy
GitHub Actions	CI/CD
Docker Hub	Container registry
Trivy	Container image security scanning

⸻

📁 Project Structure

url-shortener/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   └── redis_client.py
│
├── tests/
│   └── test_main.py
│
├── nginx/
│   └── nginx.conf
│
├── .github/
│   └── workflows/
│       └── ci-cd.yml
│
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
├── README.md
└── requirements.txt

.env is intentionally excluded from version control because it contains environment-specific configuration and credentials.

⸻

🚀 Application Features

Create Short URL

POST /shorten

Example request:

{
  "original_url": "https://www.google.com"
}

Example response:

{
  "original_url": "https://www.google.com",
  "short_url": "/Ab12Cd"
}

⸻

Redirect

GET /{short_code}

Example:

http://localhost/Ab12Cd

The application retrieves the original URL and redirects the user.

⸻

URL Statistics

GET /stats/{short_code}

Example response:

{
  "original_url": "https://www.google.com",
  "short_url": "/Ab12Cd",
  "created_at": "2026-08-15T12:00:00",
  "click_count": 5
}

⸻

Health Check

GET /health

Response:

{
  "status": "healthy"
}

The endpoint is also used by Docker health checks.

⸻

🐳 Dockerization

The application uses a multi-stage Docker build.

Docker build stages

Builder Stage
     │
     ├── Install Python dependencies
     │
     ▼
Production Stage
     │
     ├── Copy virtual environment
     ├── Copy application
     ├── Create non-root user
     ├── Configure health check
     └── Start FastAPI

Docker security features

* Multi-stage build
* Python slim base image
* Non-root application user
* .dockerignore
* No secrets baked into the image
* Docker health check
* Minimal runtime environment

⸻

🔧 Environment Variables

Create the environment file:

cp .env.example .env

Example configuration:

POSTGRES_DB=urlshortener
POSTGRES_USER=urluser
POSTGRES_PASSWORD=strongpassword123
DATABASE_URL=postgresql://urluser:strongpassword123@postgres:5432/urlshortener
REDIS_URL=redis://redis:6379/0
BASE_URL=http://localhost

Important

Do not commit .env to GitHub.

The repository should contain:

.env.example

but not:

.env

⸻

🐳 Docker Compose

The application consists of four containers:

nginx
app
postgres
redis

Start the complete platform:

sudo docker compose up -d

Check container status:

sudo docker compose ps

Stop the platform:

sudo docker compose down

View logs:

sudo docker compose logs

View application logs:

sudo docker compose logs app

⸻

💾 Persistent Storage

Two Docker volumes are used.

PostgreSQL

postgres-data

Stores persistent database data.

Redis

redis-data

Stores Redis data using Redis AOF persistence.

Check volumes:

sudo docker volume ls

⸻

🌐 Docker Networking

A custom Docker bridge network is used:

url-network

All application containers communicate through this network.

Docker service names are used for internal communication.

nginx → app:8000
app → postgres:5432
app → redis:6379

The host does not directly expose PostgreSQL or Redis.

⸻

Network Inspection

Inspect the Docker network:

sudo docker network ls

Then:

sudo docker network inspect url-shortener_url-network

This shows the containers connected to the custom network.

⸻

🔍 Docker Troubleshooting

Inspect a container

sudo docker inspect url-shortener-app

Check the application user:

sudo docker inspect url-shortener-app \
  --format '{{.Config.User}}'

Check health:

sudo docker inspect url-shortener-app \
  --format '{{.State.Health.Status}}'

⸻

Execute commands inside containers

Nginx → Application:

sudo docker exec url-shortener-nginx \
  wget -qO- http://app:8000/health

Application → PostgreSQL:

sudo docker exec url-shortener-app \
  python -c "import socket; print(socket.create_connection(('postgres',5432,5)) is not None)"

Application → Redis:

sudo docker exec url-shortener-app \
  python -c "import socket; print(socket.create_connection(('redis',6379,5)) is not None)"

⸻

🔐 Network Security

The architecture intentionally does not publish PostgreSQL or Redis ports to the host.

The expected exposure is:

Host
 │
 └── :80 → Nginx

Internal services:

Nginx → App
App → PostgreSQL
App → Redis

PostgreSQL:

Host → PostgreSQL ❌

Redis:

Host → Redis ❌

This reduces unnecessary external exposure.

⸻

🧪 Testing

Run the health check:

curl http://localhost/health

Create a short URL:

curl -X POST http://localhost/shorten \
  -H "Content-Type: application/json" \
  -d '{"original_url":"https://www.google.com"}'

Test the generated short URL:

curl -I http://localhost/<short_code>

Check statistics:

curl http://localhost/stats/<short_code>

⸻

🐘 PostgreSQL Verification

Access PostgreSQL:

sudo docker exec -it url-shortener-postgres \
  psql -U urluser -d urlshortener

Check stored URLs:

SELECT * FROM urls;

Exit:

\q

⸻

⚡ Redis Verification

List cached keys:

sudo docker exec url-shortener-redis \
  redis-cli KEYS '*'

Retrieve a cached URL:

sudo docker exec url-shortener-redis \
  redis-cli GET <short_code>

⸻

🔄 CI/CD Pipeline

GitHub Actions automates the following workflow:

Git Push
   │
   ▼
Checkout
   │
   ▼
Lint
   │
   ▼
Unit Tests
   │
   ▼
Docker Build
   │
   ▼
Security Scan
   │
   ▼
Docker Hub Login
   │
   ▼
Push Docker Image

The pipeline uses:

* GitHub Actions
* Python
* Ruff
* Pytest
* Docker
* Trivy
* Docker Hub

⸻

🛡️ Container Security Scanning

The Docker image is scanned using Trivy.

The CI pipeline checks for:

CRITICAL
HIGH

vulnerabilities.

Unfixed vulnerabilities can be ignored according to the CI configuration.

⸻

📦 Docker Hub

The final Docker image is published to Docker Hub.

Required tags:

username/url-shortener:v1.0
username/url-shortener:latest

Pull the image from another machine:

docker pull username/url-shortener:v1.0

Run the image:

docker run -p 8000:8000 username/url-shortener:v1.0

⸻

🔑 GitHub Actions Secrets

The following GitHub repository secrets are required:

DOCKERHUB_USERNAME
DOCKERHUB_TOKEN

The Docker Hub access token should never be hardcoded into the workflow or source code.

⸻

📊 DevOps Concepts Demonstrated

This project demonstrates practical knowledge of:

* Docker containerization
* Dockerfile
* Multi-stage builds
* Docker image optimization
* Non-root containers
* Docker Compose
* Custom Docker networks
* Container DNS
* Container-to-container communication
* Persistent volumes
* PostgreSQL
* Redis
* Nginx reverse proxy
* Environment variables
* Health checks
* Container restart policies
* Docker security
* Image vulnerability scanning
* GitHub Actions
* CI/CD
* Docker Hub
* Linux troubleshooting
* Container debugging

⸻

🧑‍💻 Useful Docker Commands

List containers

sudo docker ps

List all containers

sudo docker ps -a

View logs

sudo docker logs <container>

Follow logs

sudo docker logs -f <container>

Inspect container

sudo docker inspect <container>

Execute command inside container

sudo docker exec -it <container> bash

List images

sudo docker images

List networks

sudo docker network ls

Inspect network

sudo docker network inspect <network>

List volumes

sudo docker volume ls

Compose status

sudo docker compose ps

Compose logs

sudo docker compose logs

Restart services

sudo docker compose restart

⸻

🎯 Project Outcome

The completed platform provides a containerized URL Shortener with:

                  Internet
                     │
                     ▼
                  Nginx
                     │
                     ▼
                FastAPI App
                 │       │
                 ▼       ▼
             PostgreSQL  Redis

The infrastructure is isolated using a custom Docker network, persistent data is stored using Docker volumes, services are monitored using health checks, and the application is exposed through Nginx rather than directly exposing internal services.

The CI/CD pipeline automates testing, Docker image building, security scanning, and publishing to Docker Hub.

⸻

👨‍💻 Author

Gamil Jacob Thomas

B.Tech Computer Science Engineering

Focus Areas:

* DevOps
* Cloud Computing
* Linux
* Docker
* CI/CD
* Networking
* Python
* Infrastructure Automation
