# 05-AWS Secrets Manager Setup for DevConnect (Production)

## Overview

This guide configures AWS Secrets Manager and a production-grade ECS Task Execution Role for the DevConnect Auth Service.

The application reads:

```python
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("JWT_SECRET")
```

---

# Secrets

| Secret Name | Type | Environment Variable |
|---|---|---|
| `devconnect/jwt-secret` | Plaintext | `JWT_SECRET` |
| `devconnect/database-url` | Plaintext | `DATABASE_URL` |

---

# Create JWT Secret

1. AWS Console → Secrets Manager → Store a new secret
2. Choose **Other type of secret**
3. Choose **Plaintext**
4. Disable **View as JSON**
5. Paste your JWT secret.
6. Name: `devconnect/jwt-secret`
7. Description: JWT signing secret for DevConnect Auth Service.
8. Store the secret.

---

# Create Database URL Secret

1. Store a new secret.
2. Other type of secret → Plaintext.
3. Paste:

```text
postgresql://postgres:<PASSWORD>@<RDS-ENDPOINT>:5432/devconnect
```

4. Name: `devconnect/database-url`
5. Description: PostgreSQL connection string for DevConnect Auth Service.
6. Store the secret.

---

# Create Production ECS Task Execution Role

## Why create a dedicated role?

Do not use the default **ecsTaskExecutionRole** in production projects.

Create a dedicated role:

```text
DevConnect-TaskExecutionRole
```

This isolates permissions for the DevConnect application and follows the principle of least privilege.

## Step 1

AWS Console

IAM

Roles

Create Role

## Step 2

Trusted Entity

- AWS Service

Service

- Elastic Container Service

Use Case

- Elastic Container Service Task

Click **Next**

## Step 3

Attach AWS Managed Policy

Attach:

```text
AmazonECSTaskExecutionRolePolicy
```

This allows ECS to:

- Pull Docker images from Amazon ECR
- Send logs to CloudWatch Logs
- Obtain ECR authorization tokens

Click **Next**

## Step 4

Role Name

```text
DevConnect-TaskExecutionRole
```

Description

Task Execution Role for DevConnect ECS Fargate services.

Create the role.

## Step 5

Open the newly created role.

Permissions tab

Add inline policy.

Select **JSON**.

Paste:

```json
{
  "Version":"2012-10-17",
  "Statement":[
    {
      "Sid":"ReadDevConnectSecrets",
      "Effect":"Allow",
      "Action":[
        "secretsmanager:GetSecretValue"
      ],
      "Resource":[
        "arn:aws:secretsmanager:<REGION>:<ACCOUNT_ID>:secret:devconnect/jwt-secret*",
        "arn:aws:secretsmanager:<REGION>:<ACCOUNT_ID>:secret:devconnect/database-url*"
      ]
    }
  ]
}
```

Policy Name

```text
DevConnect-SecretsManager-Access
```

Save the inline policy.

> If your Secrets Manager secrets use a customer-managed KMS key, also grant `kms:Decrypt` on that key.

---

# Configure ECS Task Definition

Amazon ECS

Task Definitions

Create (or create a new revision)

Under **Infrastructure requirements**:

Task Execution Role

Select:

```text
DevConnect-TaskExecutionRole
```

Open the auth-service container.

Scroll to **Environment variables → Secrets**.

Add:

| Environment Variable | Secret |
|---|---|
| JWT_SECRET | devconnect/jwt-secret |
| DATABASE_URL | devconnect/database-url |

Save the task definition revision.

---

# Deploy

Update the ECS service to use the latest task definition revision.

---

# Validation

- ECS task starts successfully.
- Images are pulled from ECR.
- Logs appear in CloudWatch.
- Secrets are retrieved from Secrets Manager.
- Auth service connects to PostgreSQL.
- Login API generates JWT tokens.

---

# Production IAM Summary

```
DevConnect-TaskExecutionRole
│
├── AmazonECSTaskExecutionRolePolicy
│
└── Inline Policy
      └── DevConnect-SecretsManager-Access
```

This is the recommended production configuration for the DevConnect project.
