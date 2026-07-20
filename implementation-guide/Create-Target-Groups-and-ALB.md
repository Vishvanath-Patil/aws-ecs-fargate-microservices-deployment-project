# Create Target Groups and Application Load Balancer (ALB)

## Overview

This guide explains how to create Target Groups and an internet-facing ALB for the DevConnect project.

## Target Groups

Create one Target Group per microservice.

| Target Group | Target Type | Protocol | Port | VPC | Health Check Path |
|---|---|---:|---:|---|---|
| auth-service-tg | IP addresses | HTTP | 8000 | Project-VPC | `/api/auth/health` |
| frontend-tg | IP addresses | HTTP | 80 | Project-VPC | `/` |
| like-service-tg | IP addresses | HTTP | 8000 | Project-VPC | `/api/likes/health` |
| post-service-tg | IP addresses | HTTP | 8000 | Project-VPC | `/api/posts/health` |
| user-service-tg | IP addresses | HTTP | 8000 | Project-VPC | `/api/users/health` |

### Steps

1. EC2 Console → Target Groups → Create target group.
2. Select **IP addresses**.
3. Choose **HTTP** and the service port.
4. Select **Project-VPC**.
5. Configure the health check path from the table.
6. Keep default health thresholds or adjust as needed.
7. Do **not** register targets manually. ECS will register tasks automatically.
8. Repeat for all services.

---

## Create Application Load Balancer

EC2 Console → Load Balancers → Create Load Balancer → Application Load Balancer.

### Basic Configuration

| Setting | Value |
|---|---|
| Name | devconnect-alb |
| Scheme | Internet-facing |
| IP address type | IPv4 |
| VPC | Project-VPC |

### Network Mapping

| Availability Zone | Subnet |
|---|---|
| AZ-1 | Public-Subnet-A |
| AZ-2 | Public-Subnet-B |

### Security Group

| Security Group | Rule |
|---|---|
| ALB-SG | Allow HTTP (TCP 80) from `0.0.0.0/0` |

### Listener

| Protocol | Port | Default Action |
|---|---:|---|
| HTTP | 80 | Forward to `frontend-tg` |

### Listener Rules

| Priority | Path Pattern | Target Group |
|---:|---|---|
| 1 | `/api/auth/*` | auth-service-tg |
| 2 | `/api/users/*` | user-service-tg |
| 3 | `/api/posts/*` | post-service-tg |
| 4 | `/api/likes/*` | like-service-tg |
| Default | `/*` | frontend-tg |

## Validation

- ALB is Active.
- All target groups show **Healthy** after ECS services are deployed.
- ALB DNS opens the frontend application.
- API requests route to the correct backend service.
