# Containerized Flask API — Docker + AWS EC2 + RDS

A production-style containerized application deployed on AWS — Flask REST API behind Nginx reverse proxy, PostgreSQL database on AWS RDS, Docker image stored in ECR, all infrastructure provisioned via Terraform.

## What This Project Does

A Todo REST API running inside Docker containers on AWS EC2, with a managed PostgreSQL database on RDS. The entire setup mirrors how real applications are containerized and deployed in production environments.

## Architecture

```
User Request
      ↓
EC2 Instance (t2.micro)
      ↓
┌─────────────────────────────┐
│  Nginx Container (Port 80)  │
│  Reverse Proxy              │
└──────────┬──────────────────┘
           ↓
┌─────────────────────────────┐
│  Flask Container (Port 5000)│
│  Gunicorn WSGI Server       │
└──────────┬──────────────────┘
           ↓
AWS RDS PostgreSQL (db.t3.micro)
```

## Tech Stack

| Tool/Service | Purpose |
|---|---|
| **Docker** | Containerize Flask application |
| **Docker Compose** | Multi-container orchestration |
| **Python Flask** | REST API |
| **Gunicorn** | Production WSGI server |
| **Nginx** | Reverse proxy |
| **PostgreSQL** | Database |
| **AWS ECR** | Private Docker image registry |
| **AWS EC2** | Host containers (t2.micro) |
| **AWS RDS** | Managed PostgreSQL database |
| **Terraform** | All infrastructure as code |

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/todos` | Get all todos |
| POST | `/todos` | Create a todo |
| PUT | `/todos/<id>` | Update a todo |
| DELETE | `/todos/<id>` | Delete a todo |

## Docker Setup

**Multi-stage Dockerfile** — keeps production image small and secure:
- Stage 1: Install dependencies
- Stage 2: Copy only what's needed into final image

**docker-compose.yml** (local development):
- 3 services: postgres, flask, nginx
- Health checks on postgres before flask starts
- Named volumes for data persistence

## Infrastructure as Code (Terraform)

All AWS resources provisioned via Terraform — zero manual console clicks:
- VPC + public subnets (2 AZs for RDS requirement)
- Security groups (EC2: ports 22/80, RDS: port 5432 from EC2 only)
- EC2 instance with IAM role for ECR access
- RDS PostgreSQL with subnet group
- ECR repository for Docker images
- Auto-generated SSH key pair

## Problems I Ran Into

**`user_data` script didn't run**
Terraform config had Amazon Linux commands (`yum`) but AMI was Ubuntu — script silently failed. Installed Docker manually via `apt-get` after connecting via EC2 Instance Connect.

**`todos` table didn't exist on first request**
`init_db()` wasn't called on container startup. Fixed by running it manually via `docker exec` — permanent fix would be adding it to the container entrypoint.

**ECR repository wouldn't delete**
`terraform destroy` failed because Docker images were still in ECR. Had to manually delete images first with `aws ecr batch-delete-image`, then force delete the repository before Terraform could clean up.

**SSH key permissions on Windows**
`icacls` commands needed to properly restrict `.pem` file permissions — Windows doesn't use Unix-style `chmod`.

## Key Things I Learned

- How multi-stage Docker builds reduce image size and attack surface
- The difference between `docker-compose` for local dev vs manual container orchestration on a server
- Why ECR exists — private registry vs public Docker Hub, IAM-controlled access
- RDS requires subnets in at least 2 availability zones — even for a single instance
- `user_data` scripts are OS-specific — Amazon Linux vs Ubuntu use different package managers

## Local Development

```bash
# Clone repo
git clone https://github.com/aamirchanna/docker-flask-app

# Start all services
docker-compose up --build


# Stop
docker-compose down
```

## Screenshots



---

**Note:** AWS credentials, `.pem` key files, and Terraform state are excluded via `.gitignore` and should never be committed to version control.
