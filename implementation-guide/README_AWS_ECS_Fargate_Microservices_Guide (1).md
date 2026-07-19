# Production-Ready Microservices on AWS ECS Fargate

## Overview

This guide explains how to deploy a production-ready microservices application on **AWS ECS Fargate** using a secure AWS architecture.

### Architecture

```text
Internet
    │
    ▼
Application Load Balancer (Public Subnets)
    │
    ├── /api/auth  ─► Auth Service
    ├── /api/user  ─► User Service
    ├── /api/post  ─► Post Service
    └── /api/like  ─► Like Service
                        │
                  ECS Fargate Tasks
                  (Private Subnets)
                        │
                 PostgreSQL RDS
                 (Private Subnets)

Supporting Services
- Amazon ECR
- AWS Secrets Manager
- CloudWatch Logs
- Amazon S3
- VPC Endpoints
```

# Prerequisites

- AWS Account
- AWS CLI configured
- Docker
- Git
- Basic knowledge of ECS, VPC and Docker

---

# Phase 1 – Application & Containerization

## Application Stack

Frontend
- React

Backend
- FastAPI
- Auth Service
- User Service
- Post Service
- Like Service

Database
- PostgreSQL

Each microservice is independently deployable.

## Dockerize Every Service

Create a Dockerfile for each service.

Recommended:
- Python 3.11 slim
- Uvicorn
- Multi-stage build where possible
- Non-root container user

Build images:

```bash
docker build -t auth-service .
docker build -t user-service .
docker build -t post-service .
docker build -t like-service .
```

Verify locally before deployment.

---

# Phase 2 – Amazon ECR

Create one private repository per service.

Example:

- auth-service
- user-service
- post-service
- like-service
- frontend

Login:

```bash
aws ecr get-login-password | docker login --username AWS --password-stdin <ACCOUNT>.dkr.ecr.<REGION>.amazonaws.com
```

Tag:

```bash
docker tag auth-service:latest <ECR_URI>:latest
```

Push:

```bash
docker push <ECR_URI>:latest
```

Repeat for every service.

---

# Phase 3 – Networking

## Create Custom VPC

Recommended CIDR

```
10.0.0.0/16
```

Create

- 2 Public Subnets
- 2 Private ECS Subnets
- 2 Private RDS Subnets

Attach Internet Gateway.

---

## NAT Gateway

Deploy NAT Gateway in Public Subnet.

Purpose

- Package updates
- Pull container images
- Internet access for private workloads

Configure

Public Route Table

```
0.0.0.0/0 → Internet Gateway
```

Private Route Table

```
0.0.0.0/0 → NAT Gateway
```

Associate correctly.

---

# Phase 4 – Security Groups

## ALB SG

Inbound

- 80
- 443

Outbound

- ECS SG

---

## ECS SG

Inbound

- Only from ALB SG

Outbound

- RDS
- AWS Services

---

## RDS SG

Inbound

5432 only from ECS SG

Never expose PostgreSQL publicly.

---

# Phase 5 – PostgreSQL RDS

Create

- PostgreSQL
- Private Subnets
- DB Subnet Group
- Multi-AZ (recommended)

Store

- Username
- Password
- Endpoint

Initialize database using temporary EC2 or AWS Systems Manager.

---

# Phase 6 – Application Load Balancer

Deploy ALB in Public Subnets.

Create Target Groups

- auth
- user
- post
- like
- frontend

Configure Listener Rules

```
/api/auth/*
/api/user/*
/api/post/*
/api/like/*
```

Frontend becomes default target.

---

# Phase 7 – AWS Secrets Manager

Store

- JWT Secret
- Database URL
- PostgreSQL Password
- API Keys

Reference secrets inside ECS Task Definitions.

Never hardcode secrets.

---

# Phase 8 – ECS Cluster

Launch Type

- AWS Fargate

Create Task Definitions

Specify

- CPU
- Memory
- Container Image
- Port Mapping
- Health Check
- IAM Role
- CloudWatch Logs
- Secrets

---

# Phase 9 – ECS Services

Create one service per microservice.

Example

- frontend
- auth
- user
- post
- like

Enable

- Desired Tasks
- Auto Recovery
- ALB Integration

---

# Phase 10 – Deployment

Deploy every ECS Service.

Verify

- Running Tasks
- Healthy Target Groups
- ALB Health Checks

Open ALB DNS.

Validate

- Login
- User APIs
- Posts
- Likes
- Database connectivity

---

# Phase 11 – Production Optimization

Replace NAT Gateway with VPC Endpoints.

Create Endpoints

Interface

- ECR API
- ECR DKR
- CloudWatch Logs
- Secrets Manager

Gateway

- Amazon S3

Benefits

- Lower Cost
- Private AWS Network
- Better Security
- Reduced Internet Exposure

---

# Monitoring

Enable

- CloudWatch Logs
- ECS Container Insights
- CloudWatch Alarms

Optional

- Prometheus
- Grafana

---

# Best Practices

- Use IAM Roles
- Least Privilege
- Private Subnets
- HTTPS
- Auto Scaling
- Health Checks
- Secrets Manager
- Image Scanning
- Multi-AZ
- CloudWatch Monitoring

---

# Validation Checklist

- VPC Created
- Public/Private Subnets
- Internet Gateway
- NAT Gateway or VPC Endpoints
- Security Groups
- RDS Running
- Secrets Created
- ECR Images Uploaded
- ECS Cluster Running
- ECS Services Healthy
- ALB Routing Working
- Application Accessible

---

# Learning Outcome

After completing this project you will understand:

- Docker
- Microservices
- Amazon ECR
- VPC Design
- Public vs Private Subnets
- Internet Gateway
- NAT Gateway
- Route Tables
- Security Groups
- PostgreSQL RDS
- Application Load Balancer
- Path-Based Routing
- AWS Secrets Manager
- ECS Fargate
- Task Definitions
- ECS Services
- CloudWatch
- VPC Endpoints
- Production Architecture

This guide is intended as a GitHub-friendly README that follows the deployment flow demonstrated in the reference video while expanding it into a structured learning document suitable for beginners and experienced AWS engineers.
