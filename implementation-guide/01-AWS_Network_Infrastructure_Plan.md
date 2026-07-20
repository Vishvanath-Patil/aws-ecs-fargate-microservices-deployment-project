# 01 AWS Network Infrastructure Plan

## 📌 VPC

| **Resource** | **Name** | **CIDR Block** | **Description / Purpose** |
|:-------------|:---------|:---------------|:--------------------------|
| VPC | Project-VPC | `10.0.0.0/16` | Provides an isolated virtual network for the ALB, ECS services, NAT Gateways, and Amazon RDS. |

---

## 🌍 Availability Zones

| **Availability Zone** | **Purpose** |
|:----------------------|:------------|
| AZ-1 | Hosts the first set of public and private subnets for high availability. |
| AZ-2 | Hosts the second set of public and private subnets for fault tolerance and failover. |

---

## 🗂️ Subnets

| **Subnet Name** | **AZ** | **CIDR Block** | **Type** | **Purpose** |
|:----------------|:------:|:--------------:|:--------:|:------------|
| Public-Subnet-A | AZ-1 | `10.0.1.0/24` | Public | Hosts the Application Load Balancer and NAT Gateway-A. |
| Public-Subnet-B | AZ-2 | `10.0.2.0/24` | Public | Hosts the Application Load Balancer and NAT Gateway-B. |
| Private-App-Subnet-A | AZ-1 | `10.0.11.0/24` | Private | Hosts ECS Frontend and Backend tasks. |
| Private-App-Subnet-B | AZ-2 | `10.0.12.0/24` | Private | Hosts ECS Frontend and Backend tasks for High Availability. |
| Private-DB-Subnet-A | AZ-1 | `10.0.21.0/24` | Private | Hosts the Amazon RDS PostgreSQL primary instance. |
| Private-DB-Subnet-B | AZ-2 | `10.0.22.0/24` | Private | Used by Amazon RDS Multi-AZ standby/failover. |

---

## 🌐 Internet Gateway

| **Resource** | **Name** | **Attached To** | **Purpose** |
|:-------------|:---------|:----------------|:------------|
| Internet Gateway | Project-IGW | Project-VPC | Enables Internet connectivity for public subnets hosting the ALB and NAT Gateways. |

---

## 🚪 NAT Gateways

| **NAT Gateway** | **AZ** | **Public Subnet** | **Elastic IP** | **Purpose** |
|:----------------|:------:|:------------------|:--------------:|:------------|
| NAT-Gateway-A | AZ-1 | Public-Subnet-A | Yes | Provides outbound Internet access for private resources in AZ-1. |
| NAT-Gateway-B | AZ-2 | Public-Subnet-B | Yes | Provides outbound Internet access for private resources in AZ-2. |

---

## 🛣️ Route Tables

| **Route Table** | **Associated Subnets** | **Default Route** | **Purpose** |
|:----------------|:-----------------------|:------------------|:------------|
| Public-Route-Table | Public-Subnet-A, Public-Subnet-B | `0.0.0.0/0 → Internet Gateway` | Allows public resources to communicate with the Internet. |
| Private-App-RT-A | Private-App-Subnet-A | `0.0.0.0/0 → NAT-Gateway-A` | Provides outbound Internet access for ECS tasks in AZ-1. |
| Private-App-RT-B | Private-App-Subnet-B | `0.0.0.0/0 → NAT-Gateway-B` | Provides outbound Internet access for ECS tasks in AZ-2. |
| Private-DB-RT | Private-DB-Subnet-A, Private-DB-Subnet-B | Local VPC Route Only | Keeps the database isolated from the Internet. |

---

## 📊 Infrastructure Summary

| **Component** | **Deployment** |
|:--------------|:---------------|
| VPC | 1 (`10.0.0.0/16`) |
| Availability Zones | 2 |
| Public Subnets | 2 |
| Private Application Subnets | 2 |
| Private Database Subnets | 2 |
| Internet Gateway | 1 |
| NAT Gateways | 2 (One per AZ) |
| Public Route Tables | 1 |
| Private Route Tables | 3 |
| Application Load Balancer | Across both public subnets |
| ECS Services | Across both private application subnets |
| Amazon RDS PostgreSQL | Multi-AZ in private database subnets |

---

## ✅ Design Benefits

- High Availability across two Availability Zones.
- Internet-facing Application Load Balancer.
- ECS services remain in private subnets.
- Amazon RDS is isolated from the Internet.
- One NAT Gateway per Availability Zone.

## Security Groups

| Security Group | Direction | Protocol | Port | Source/Destination | Description |
|----------------|-----------|----------|------|--------------------|-------------|
| **ALB-SG** | Inbound | TCP | 80 | `0.0.0.0/0` | Allow HTTP traffic from the Internet to the Application Load Balancer. |
| **Frontend-SG** | Inbound | TCP | 80 | **ALB-SG** | Allow HTTP requests only from the Application Load Balancer. |
| **Backend-SG** | Inbound | TCP | 8000 | **ALB-SG** | Allow API requests only from the Application Load Balancer. |
| **Database-SG** | Inbound | TCP | 5432 | **Backend-SG** | Allow PostgreSQL connections only from the Backend application. |

> **Note:** Outbound rules can remain as the default (**Allow All**) unless your organization's security policy requires restricting egress traffic.

## Traffic Flow

``` text
Internet
    |
    v
Application Load Balancer (ALB)
    |
    +-----------> Frontend (Port 80)
    |
    +-----------> Backend API (Port 8000)
                         |
                         v
                PostgreSQL Database (Port 5432)
```

## Security Principles

-   **ALB-SG** is the only security group exposed to the Internet.
-   **Frontend-SG** accepts traffic **only** from **ALB-SG**.
-   **Backend-SG** accepts traffic **only** from **ALB-SG**.
-   **Database-SG** accepts PostgreSQL connections **only** from
    **Backend-SG**.
-   No direct Internet access is allowed to the Frontend, Backend, or
    Database.

  
