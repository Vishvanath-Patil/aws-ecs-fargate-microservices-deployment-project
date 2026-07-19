# Amazon RDS PostgreSQL Setup Guide (Private Subnets)

## Architecture

| Component | Configuration |
|-----------|---------------|
| VPC | `10.0.0.0/16` |
| Availability Zones | 2 |
| DB Subnets | Private-DB-Subnet-A (`10.0.21.0/24`), Private-DB-Subnet-B (`10.0.22.0/24`) |
| Database | Amazon RDS PostgreSQL |
| Security Group | Database-SG |
| Database Port | 5432 |
| Public Access | Disabled |
| Multi-AZ | Enabled |

---

# Step 1: Create a DB Subnet Group

1. Open **Amazon RDS Console**
2. Navigate to **Subnet groups**
3. Click **Create DB subnet group**

| Setting | Value |
|---------|-------|
| Name | `project-db-subnet-group` |
| Description | DB subnet group for PostgreSQL |
| VPC | Project-VPC |
| Availability Zones | AZ-1, AZ-2 |
| Subnets | Private-DB-Subnet-A, Private-DB-Subnet-B |

Click **Create**.

---

# Step 2: Create Database Security Group

| Rule | Value |
|------|-------|
| Security Group | Database-SG |
| Inbound | PostgreSQL (TCP 5432) |
| Source | Backend-SG |
| Outbound | Allow All (Default) |

This allows only backend ECS tasks/EC2 to connect.

---

# Step 3: Create Amazon RDS PostgreSQL

Go to **RDS → Databases → Create database**

## Engine

| Setting | Value |
|---------|-------|
| Engine | PostgreSQL |
| Template | Free Tier / Dev-Test (or Production) |

## Settings

| Setting | Example |
|---------|----------|
| DB Identifier | `project-postgres-db` |
| Master Username | `postgres` |
| Password | Create a strong password |

## Instance

| Setting | Value |
|---------|-------|
| Instance Class | db.t3.micro (Lab) |
| Storage | 20 GB gp3 |
| Storage Autoscaling | Optional |

## Connectivity

| Setting | Value |
|---------|-------|
| VPC | Project-VPC |
| DB Subnet Group | project-db-subnet-group |
| Public Access | No |
| VPC Security Group | Database-SG |
| Availability | Multi-AZ |

Click **Create Database**.

---

# Step 4: Verify Connectivity

After the database becomes **Available**, note:

- Endpoint
- Port (5432)

Example:

```text
Endpoint:
project-postgres-db.xxxxxxxxx.ap-south-1.rds.amazonaws.com

Port:
5432
```

---

# Step 5: Launch a Bastion EC2 (Temporary)

Since the database is in private subnets, launch an EC2 instance in **Public-Subnet-A**.

| Setting | Value |
|---------|-------|
| Subnet | Public-Subnet-A |
| Public IP | Enabled |
| Security Group | Bastion-SG |

Add the following rule to **Database-SG** temporarily:

| Type | Port | Source |
|------|------|--------|
| PostgreSQL | 5432 | Bastion-SG |

---

# Step 6: Install PostgreSQL Client

Amazon Linux 2023

```bash
sudo dnf install postgresql15 -y
```

Ubuntu

```bash
sudo apt update
sudo apt install postgresql-client -y
```

---

# Step 7: Connect to Database

```bash
psql \
-h project-postgres-db.xxxxxxxxx.ap-south-1.rds.amazonaws.com \
-U postgres \
-p 5432
```

Enter the password.

---

# Step 8: Create Database

```sql
CREATE DATABASE ecommerce;
```

Verify

```sql
\l
```

Switch

```sql
\c ecommerce
```

---

# Step 9: Create Application User

```sql
CREATE USER appuser WITH PASSWORD 'StrongPassword123!';
GRANT ALL PRIVILEGES ON DATABASE ecommerce TO appuser;
```

---

# Step 10: Create Sample Table

```sql
CREATE TABLE products(
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    price NUMERIC(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Insert data

```sql
INSERT INTO products(name,price)
VALUES
('Laptop',55000),
('Keyboard',1200),
('Mouse',800);
```

Verify

```sql
SELECT * FROM products;
```

---

# Step 11: Update Backend Configuration

Example connection string

```text
Host=project-postgres-db.xxxxxxxxx.ap-south-1.rds.amazonaws.com
Port=5432
Database=ecommerce
Username=appuser
Password=<password>
```

---

# Security Best Practices

- Use private database subnets only.
- Disable Public Access.
- Allow inbound 5432 only from Backend-SG.
- Remove Bastion-SG rule after testing.
- Enable automated backups.
- Enable deletion protection for production.
- Store credentials in AWS Secrets Manager.
- Enable Multi-AZ for production.
