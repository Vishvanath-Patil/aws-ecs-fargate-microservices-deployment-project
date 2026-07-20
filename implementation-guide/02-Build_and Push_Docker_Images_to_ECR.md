# 02-Launch an EC2 Docker Build Server for Amazon ECR

## Objective

Provision an EC2 instance that can: - Build Docker images - Authenticate
to Amazon ECR - Push images to Amazon ECR - Be managed securely using
AWS Systems Manager (SSM)

------------------------------------------------------------------------
# Create IAM Role

Create an IAM Role named:

``` text
iam-role-grant-ec2-ssm-and-ecr-access
```

Attach these AWS managed policies:

-   AmazonSSMManagedInstanceCore
-   EC2InstanceProfileForImageBuilderECRContainerBuilds

Attach the IAM Role to the EC2 instance.

Verify:

``` bash
aws sts get-caller-identity
```

Expected output:

``` json
{
  "Account": "123456789012",
  "Arn": "arn:aws:sts::123456789012:assumed-role/iam-role-grant-ec2-ssm-and-ecr-access/i-xxxxxxxx",
  "UserId": "..."
}
```
------------------------------------------------------------------------

# Launch an EC2 Instance

Launch an Amazon EC2 instance that will be used as a dedicated Docker build server for building container images and pushing them to Amazon Elastic Container Registry (Amazon ECR).

| **Setting** | **Recommended Value** |
|-------------|-----------------------|
| **AMI** | Amazon Linux 2023 (Recommended) |
| **Instance Type** | t3.medium |
| **Root Volume** | 20 GB gp3 |
| **VPC** | Your project VPC |
| **Subnet** | Public Subnet (or Private Subnet with AWS Systems Manager) |
| **Auto-assign Public IP** | Enabled (only if connecting through SSH) |
| **Security Group** | Allow SSH (TCP 22) only from **Your Public IP** |
| **IAM Role** | `iam-role-grant-ec2-ssm-and-ecr-access` |
------------------------------------------------------------------------

# Connect to EC2

## AWS Systems Manager

AWS Console

EC2 → Instance → Connect → Session Manager

------------------------------------------------------------------------

# Update Packages

## Amazon Linux 2023

``` bash
sudo dnf update -y
```

------------------------------------------------------------------------

# Install Git

Amazon Linux 2023

``` bash
sudo dnf install git -y
```

Verify:

``` bash
git --version
```

------------------------------------------------------------------------

# Install Docker

Amazon Linux 2023

``` bash
sudo dnf install docker -y
```

Verify:

``` bash
docker --version
```

------------------------------------------------------------------------

# Start Docker

``` bash
sudo systemctl enable docker
sudo systemctl start docker
sudo systemctl status docker
```

------------------------------------------------------------------------

# Configure Docker for ec2-user

``` bash
sudo usermod -aG docker ec2-user
newgrp docker
```

Verify:

``` bash
docker ps
```

------------------------------------------------------------------------
# Build and Push Docker Images to Amazon ECR

## Overview

This guide explains how to:

- Clone the **DevConnect** source code
- Verify all microservices locally using Docker Compose
- Build Docker images for each microservice
- Create Amazon ECR repositories
- Authenticate Docker with Amazon ECR
- Tag and push images
- Verify uploaded images in AWS

---

# Services

| Service | Amazon ECR Repository |
|----------|-----------------------|
| auth-service | devconnect-auth-service |
| frontend | devconnect-frontend |
| like-service | devconnect-like-service |
| post-service | devconnect-post-service |
| user-service | devconnect-user-service |

---

# Step 1 – Log in to the Docker Build Server

Connect to your EC2 instance (Docker build server).

Verify Docker:

```bash
docker --version

sudo mkdir -p /usr/local/lib/docker/cli-plugins

sudo curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 \
-o /usr/local/lib/docker/cli-plugins/docker-compose

sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

docker compose version
```

---

# Step 2 – Clone the Repository

```bash
git clone https://github.com/Vishvanath-Patil/aws-ecs-fargate-microservices-deployment-project.git
```

Navigate to the project:

```bash
cd aws-ecs-fargate-microservices-deployment-project
```

---

# Step 3 – Verify the Application Locally

Start all services:

```bash
docker compose up -d
```

Open your browser and verify the application is running correctly.

Once verified, stop the application:

```bash
docker compose down
```

---

# Step 4 – Create Amazon ECR Repositories for Each Service

Create the following **Private** repositories in Amazon ECR.

| Repository Name |
|-----------------|
| devconnect-auth-service |
| devconnect-frontend |
| devconnect-like-service |
| devconnect-post-service |
| devconnect-user-service |

Enable:

- Scan on Push
- AES-256 Encryption
- Mutable Tags

---

# Step 5 – Authenticate Docker to Amazon ECR

Replace `<ACCOUNT_ID>` and `<REGION>`.

```bash
aws ecr get-login-password --region <REGION> \
| docker login \
--username AWS \
--password-stdin <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com
```

Expected Output:

```text
Login Succeeded
```

---

# Step 6 – Build Docker Images

## 1. auth-service

```bash
cd auth-service

docker build -t devconnect-auth-service:latest .
```

---

## 2. frontend

```bash
cd ../frontend

docker build -t devconnect-frontend:latest .
```

---

## 3. like-service

```bash
cd ../like-service

docker build -t devconnect-like-service:latest .
```

---

## 4. post-service

```bash
cd ../post-service

docker build -t devconnect-post-service:latest .
```

---

## 5. user-service

```bash
cd ../user-service

docker build -t devconnect-user-service:latest .
```

---

# Step 7 – Tag Docker Images

Replace `<ACCOUNT_ID>` and `<REGION>`.

```bash
docker tag devconnect-auth-service:latest <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/devconnect-auth-service:latest

docker tag devconnect-frontend:latest <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/devconnect-frontend:latest

docker tag devconnect-like-service:latest <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/devconnect-like-service:latest

docker tag devconnect-post-service:latest <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/devconnect-post-service:latest

docker tag devconnect-user-service:latest <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/devconnect-user-service:latest
```

---

# Step 8 – Push Images to Amazon ECR

```bash
docker push <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/devconnect-auth-service:latest

docker push <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/devconnect-frontend:latest

docker push <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/devconnect-like-service:latest

docker push <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/devconnect-post-service:latest

docker push <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/devconnect-user-service:latest
```

---

# Step 9 – Verify Images in Amazon ECR

Open:

**AWS Console → Amazon ECR → Repositories**

Verify that each repository contains the `latest` image.

| Repository | Expected Image Tag |
|------------|--------------------|
| devconnect-auth-service | latest |
| devconnect-frontend | latest |
| devconnect-like-service | latest |
| devconnect-post-service | latest |
| devconnect-user-service | latest |

---


