# 09 - Verify Amazon ECS Fargate Deployment for DevConnect

# Overview

This guide explains how to verify that every DevConnect service has been deployed successfully and how to troubleshoot common issues.

Services:

- frontend-service
- auth-service
- user-service
- post-service
- like-service

---

# Step 1 - Verify ECS Cluster

AWS Console

Amazon ECS

Clusters

Select:

```text
devconnect-cluster
```

Verify:

- Cluster Status = Active
- Running Tasks > 0
- Services = 5
- Container Insights = Enabled

---

# Step 2 - Verify ECS Services

Open

Amazon ECS

Clusters

devconnect-cluster

Services

Verify each service:

| Service | Desired | Running | Status |
|----------|---------|---------|--------|
| frontend-service | 2 | 2 | Active |
| auth-service | 2 | 2 | Active |
| user-service | 2 | 2 | Active |
| post-service | 2 | 2 | Active |
| like-service | 2 | 2 | Active |

If Running != Desired, investigate the service events.

---

# Step 3 - Verify Service Events

Open:

Amazon ECS

Cluster

Service

Events Tab

A healthy deployment shows messages similar to:

- service reached a steady state
- registered targets in target group
- started new task
- deployment completed

Common error messages:

| Error | Possible Cause |
|--------|----------------|
| CannotPullContainerError | Incorrect ECR image or permissions |
| ResourceInitializationError | Secrets Manager or IAM issue |
| AccessDeniedException | Task Execution Role missing permissions |
| Health checks failed | Application not listening on expected port/path |
| Essential container exited | Application startup failure |

---

# Step 4 - Verify Running Tasks

Open:

Service

Tasks

Verify:

- Task Status = RUNNING
- Health Status = HEALTHY
- CPU and Memory utilization appear normal

Open each task and verify:

- Task Definition revision
- Task Execution Role
- ENI attached
- Private IP assigned

---

# Step 5 - Verify Target Groups

AWS Console

EC2

Target Groups

Verify each target group:

- frontend-tg
- auth-tg
- user-tg
- post-tg
- like-tg

Targets should display:

Healthy

Health Check:

| Target Group | Health Check Path |
|--------------|-------------------|
| frontend-tg | / |
| auth-tg | /api/auth/health |
| user-tg | /api/users/health |
| post-tg | /api/posts/health |
| like-tg | /api/likes/health |

If targets remain unhealthy:

- Verify Security Groups
- Verify container port
- Verify health check path
- Verify application startup

---

# Step 6 - Verify CloudWatch Logs

AWS Console

CloudWatch

Log Groups

Verify:

- /ecs/devconnect-frontend
- /ecs/devconnect-auth
- /ecs/devconnect-user
- /ecs/devconnect-post
- /ecs/devconnect-like

Check for:

- Application startup logs
- Database connection messages
- Errors or exceptions

---

# Step 7 - Verify Secrets

Open Task Definition

Container

Environment

Secrets

Verify:

JWT_SECRET

maps to

devconnect/jwt-secret

DATABASE_URL

maps to

devconnect/database-url

---

# Step 8 - Verify Application Load Balancer

EC2

Load Balancers

Select ALB

Verify:

Status = Active

DNS Name available

Listener Rules:

- /api/auth/*
- /api/users/*
- /api/posts/*
- /api/likes/*
- Default -> frontend

---

# Step 9 - Verify Application

Open browser:

http://<ALB-DNS>

Expected:

Frontend application loads successfully.

Verify APIs:

GET

/api/auth/health

Expected

200 OK

GET

/api/users/health

Expected

200 OK

GET

/api/posts/health

Expected

200 OK

GET

/api/likes/health

Expected

200 OK

---

# Step 10 - Functional Testing

Register a new user.

Login.

Expected:

JWT token returned.

Create a post.

Like a post.

Verify database updates successfully.

---

# Step 11 - Verify Database Connectivity

CloudWatch logs should not contain:

- Connection refused
- Authentication failed
- Timeout

Application should connect successfully to Amazon RDS.

---

# Step 12 - Verify Networking

Confirm:

- ECS Tasks are in Private App Subnets.
- RDS is in Private DB Subnets.
- ALB is in Public Subnets.
- Security Groups allow required traffic only.

---

# Common Troubleshooting

| Issue | Resolution |
|--------|------------|
| Task stops immediately | Check CloudWatch logs |
| Image pull fails | Verify ECR URI and Task Execution Role |
| Secrets unavailable | Verify IAM permissions and secret names |
| Health checks fail | Verify health endpoint and port |
| Target unhealthy | Verify SGs, ALB rules and application startup |
| Database connection fails | Verify DATABASE_URL and Database-SG |

---

# Deployment Success Checklist

- Cluster Active
- Five ECS Services Active
- Desired Tasks = Running Tasks
- Tasks Healthy
- Target Groups Healthy
- ALB Active
- Listener Rules Configured
- CloudWatch Logs Available
- Secrets Loaded
- PostgreSQL Connected
- Frontend Accessible
- Authentication Working
- APIs Responding
- Posts Created Successfully
- Likes Working

Congratulations! Your DevConnect application is successfully deployed on Amazon ECS Fargate.
