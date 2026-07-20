# 06-Amazon ECS Cluster Creation, Task Definition, ECS Service

# Overview

This document provides a complete deployment guide for the DevConnect microservices application on Amazon ECS Fargate.

## Services

| Service | Port | Target Group | Security Group |
|---|---:|---|---|
| Frontend | 80 | frontend-tg | Frontend-SG |
| Auth Service | 8000 | auth-tg | Backend-SG |
| User Service | 8000 | user-tg | Backend-SG |
| Post Service | 8000 | post-tg | Backend-SG |
| Like Service | 8000 | like-tg | Backend-SG |

## Prerequisites

- Project-VPC
- Public Subnet A & B (ALB)
- Private App Subnet A & B (ECS)
- Private DB Subnet A & B (RDS)
- Internet Gateway
- NAT Gateway
- Application Load Balancer
- Target Groups
- Amazon ECR repositories
- CloudWatch Log Groups
- Secrets:
  - devconnect/jwt-secret
  - devconnect/database-url
- IAM Role:
  - DevConnect-TaskExecutionRole

---

# Step 1 - Create ECS Cluster

AWS Console → Amazon ECS → Clusters → Create Cluster

| Setting | Value |
|---|---|
| Cluster Name | devconnect-cluster |
| Infrastructure | AWS Fargate |
| Container Insights | Enabled |

Create the cluster.

---

# Step 2 - Create CloudWatch Log Groups

Create:

- /ecs/devconnect-frontend
- /ecs/devconnect-auth
- /ecs/devconnect-user
- /ecs/devconnect-post
- /ecs/devconnect-like

---

# Step 3 - Create Task Definitions

Repeat for each service.

## Common Settings

| Field | Value |
|---|---|
| Launch Type | Fargate |
| Network Mode | awsvpc |
| Runtime | Linux/X86_64 |
| Task Execution Role | DevConnect-TaskExecutionRole |
| Task Role | None |
| Ephemeral Storage | 20 GB |

### Frontend Task Definition

Family: devconnect-frontend

CPU: 0.25 vCPU

Memory: 512 MiB

Container

- Name: frontend
- Image: <frontend-ecr-uri>
- Port: 80

Logs

- awslogs
- /ecs/devconnect-frontend

Environment Variables

API_BASE_URL=http://<ALB-DNS>

### Auth Task Definition

Family: devconnect-auth

CPU: 0.5 vCPU

Memory: 1 GB

Container

- Name: auth-service
- Image: <auth-ecr-uri>
- Port: 8000

CloudWatch Log Group

- /ecs/devconnect-auth

Secrets

JWT_SECRET -> devconnect/jwt-secret

DATABASE_URL -> devconnect/database-url

Health Check Path

/api/auth/health

### User Task Definition

Family: devconnect-user

CPU: 0.5 vCPU

Memory: 1 GB

Container

- Name: user-service
- Image: <user-ecr-uri>
- Port: 8000

CloudWatch Logs

- /ecs/devconnect-user

Secrets

DATABASE_URL -> devconnect/database-url

Health Check

/api/users/health

### Post Task Definition

Family: devconnect-post

CPU: 0.5 vCPU

Memory: 1 GB

Container

- Name: post-service
- Image: <post-ecr-uri>
- Port: 8000

Logs

- /ecs/devconnect-post

Secrets

DATABASE_URL -> devconnect/database-url

Health Check

/api/posts/health

### Like Task Definition

Family: devconnect-like

CPU: 0.5 vCPU

Memory: 1 GB

Container

- Name: like-service
- Image: <like-ecr-uri>
- Port: 8000

Logs

- /ecs/devconnect-like

Secrets

DATABASE_URL -> devconnect/database-url

Health Check

/api/likes/health

---

# Step 4 - Create ECS Services

Repeat for every task definition.

## Frontend Service

| Field | Value |
|---|---|
| Service Name | frontend-service |
| Cluster | devconnect-cluster |
| Desired Tasks | 2 |
| VPC | Project-VPC |
| Subnets | Private App Subnet A & B |
| Security Group | Frontend-SG |
| Public IP | Disabled |
| Load Balancer | Existing ALB |
| Target Group | frontend-tg |

## Auth Service

| Field | Value |
|---|---|
| Service Name | auth-service |
| Cluster | devconnect-cluster |
| Desired Tasks | 2 |
| VPC | Project-VPC |
| Subnets | Private App Subnet A & B |
| Security Group | Backend-SG |
| Public IP | Disabled |
| Target Group | auth-tg |

## User Service

Use the same settings as Auth Service.

Target Group: user-tg

## Post Service

Use the same settings as Auth Service.

Target Group: post-tg

## Like Service

Use the same settings as Auth Service.

Target Group: like-tg

---

# Step 5 - Listener Rules

| Path | Target Group |
|---|---|
| /api/auth/* | auth-tg |
| /api/users/* | user-tg |
| /api/posts/* | post-tg |
| /api/likes/* | like-tg |
| Default | frontend-tg |

---

# Step 6 - Deployment Verification

Verify:

- All five services are RUNNING.
- All tasks pass health checks.
- Target Groups show Healthy.
- CloudWatch Logs receive application logs.
- Frontend loads through ALB DNS.
- Login returns JWT token.
- User, Post and Like APIs are reachable.
- PostgreSQL connections succeed.

---

# Production Best Practices

- Deploy at least two tasks per service.
- Use private app subnets for ECS tasks.
- Keep RDS in private DB subnets.
- Use DevConnect-TaskExecutionRole with least-privilege permissions.
- Store secrets only in AWS Secrets Manager.
- Enable Container Insights.
- Configure Auto Scaling and health checks before production rollout.
