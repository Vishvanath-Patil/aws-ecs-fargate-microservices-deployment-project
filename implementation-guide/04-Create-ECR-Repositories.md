# Create Amazon ECR Repositories for DevConnect

## Overview

Amazon Elastic Container Registry (Amazon ECR) is a fully managed container image registry used to securely store Docker images for Amazon ECS.

In the **DevConnect** project, each microservice has its own dedicated ECR repository.

---

## Repository Architecture

| Service | Docker Image | Amazon ECR Repository | Purpose |
|---------|--------------|-----------------------|---------|
| Frontend | `frontend` | `devconnect-frontend` | Stores the Frontend Docker image used by the ECS Frontend Service. |
| Backend | `backend` | `devconnect-backend` | Stores the Backend Docker image used by the ECS Backend Service. |

> **Why separate repositories?**
>
> - Independent deployments
> - Easier version management
> - Faster rollbacks
> - Separate CI/CD pipelines
> - AWS best practice for microservices

---

# Prerequisites

| Requirement | Status |
|------------|--------|
| AWS Account | Required |
| IAM User with ECR Permissions | Required |
| AWS CLI Installed | Required |
| Docker Desktop Installed | Required |
| AWS CLI Configured | Required |

Verify AWS CLI

```bash
aws sts get-caller-identity
```

---

# Step 1 – Open Amazon ECR

AWS Console → **Amazon ECR** → **Create Repository**

---

# Step 2 – Create Frontend Repository

| Setting | Value |
|---------|-------|
| Repository Name | `devconnect-frontend` |
| Visibility | Private |
| Tag Mutability | Mutable |
| Encryption | AES-256 |
| Scan on Push | Enabled |

Click **Create Repository**.

---

# Step 3 – Create Backend Repository

| Setting | Value |
|---------|-------|
| Repository Name | `devconnect-backend` |
| Visibility | Private |
| Tag Mutability | Mutable |
| Encryption | AES-256 |
| Scan on Push | Enabled |

Click **Create Repository**.

---

# Step 4 – Verify Repositories

| Repository | Status |
|------------|--------|
| devconnect-frontend | Created |
| devconnect-backend | Created |

---

# Step 5 – Copy Repository URI

Example:

```text
Frontend
123456789012.dkr.ecr.ap-south-1.amazonaws.com/devconnect-frontend

Backend
123456789012.dkr.ecr.ap-south-1.amazonaws.com/devconnect-backend
```

---

# Step 6 – Authenticate Docker with Amazon ECR

```bash
aws ecr get-login-password \
--region ap-south-1 \
| docker login \
--username AWS \
--password-stdin 123456789012.dkr.ecr.ap-south-1.amazonaws.com
```

Expected Output

```text
Login Succeeded
```

---

# Step 7 – Verify Using AWS CLI

```bash
aws ecr describe-repositories
```

Example Output

```text
devconnect-frontend
devconnect-backend
```
---

# Best Practices

- Create one repository per microservice.
- Enable image scan on push.
- Keep repositories private.
- Use semantic version tags (`v1.0.0`, `v1.1.0`) instead of `latest` in production.
- Configure lifecycle policies to delete old images.
- Grant least-privilege IAM permissions.

---

# Next Step

Build Docker images for both services and push them to Amazon ECR before creating Amazon ECS Task Definitions.
