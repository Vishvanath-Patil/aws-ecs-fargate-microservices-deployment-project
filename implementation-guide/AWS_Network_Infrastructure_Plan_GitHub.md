# AWS Network Infrastructure Plan

## VPC

| Resource | Name | CIDR Block | Description / Purpose |
| --- | --- | --- | --- |
| VPC | Project-VPC | `10.0.0.0/16` | Provides an isolated virtual network for hosting all application resources, including the ALB, ECS services, NAT Gateways, and RDS database. |

---

## Availability Zones

| Availability Zone | Purpose |
| --- | --- |
| AZ-1 | Hosts the first set of public and private subnets to provide high availability. |
| AZ-2 | Hosts the second set of public and private subnets for fault tolerance and disaster resilience. |

---

## Subnets

| Subnet Name | Availability Zone | CIDR Block | Type | Purpose |
| --- | --- | --- | --- | --- |
| Public-Subnet-A | AZ-1 | `10.0.1.0/24` | Public | Hosts the internet-facing Application Load Balancer and NAT Gateway. |
| Public-Subnet-B | AZ-2 | `10.0.2.0/24` | Public | Hosts the internet-facing Application Load Balancer and NAT Gateway for high availability. |
| Private-App-Subnet-A | AZ-1 | `10.0.11.0/24` | Private | Hosts ECS Frontend and Backend tasks. No direct Internet access. |
| Private-App-Subnet-B | AZ-2 | `10.0.12.0/24` | Private | Hosts ECS Frontend and Backend tasks for high availability. |
| Private-DB-Subnet-A | AZ-1 | `10.0.21.0/24` | Private | Hosts the PostgreSQL RDS primary instance. |
| Private-DB-Subnet-B | AZ-2 | `10.0.22.0/24` | Private | Used by the RDS DB Subnet Group for Multi-AZ deployment and failover. |

---

## Internet Gateway

| Resource | Name | Attached To | Purpose |
| --- | --- | --- | --- |
| Internet Gateway | Project-IGW | Project-VPC | Enables inbound and outbound Internet connectivity for resources in public subnets, such as the Application Load Balancer and NAT Gateways. |

---

## NAT Gateways

| NAT Gateway | Availability Zone | Public Subnet | Elastic IP | Purpose |
| --- | --- | --- | --- | --- |
| NAT-Gateway-A | AZ-1 | Public-Subnet-A | Yes | Provides outbound Internet access for private resources in AZ-1 without exposing them to inbound Internet traffic. |
| NAT-Gateway-B | AZ-2 | Public-Subnet-B | Yes | Provides outbound Internet access for private resources in AZ-2, ensuring high availability if one AZ becomes unavailable. |

---

## Route Tables

| Route Table | Associated Subnets | Routes | Purpose |
| --- | --- | --- | --- |
| Public-Route-Table | Public-Subnet-A, Public-Subnet-B | `0.0.0.0/0 → Internet Gateway` | Allows public subnets to communicate directly with the Internet. |
| Private-App-RT-A | Private-App-Subnet-A | `0.0.0.0/0 → NAT-Gateway-A` | Allows ECS tasks in AZ-1 to access the Internet for updates, package downloads, and AWS services while remaining private. |
| Private-App-RT-B | Private-App-Subnet-B | `0.0.0.0/0 → NAT-Gateway-B` | Allows ECS tasks in AZ-2 to securely access the Internet through the NAT Gateway. |
| Private-DB-RT | Private-DB-Subnet-A, Private-DB-Subnet-B | Local VPC Route Only | Keeps the database isolated from the Internet while allowing communication within the VPC. |

---

## High-Level Network Architecture

| Component | Deployment |
| --- | --- |
| VPC | Single VPC (`10.0.0.0/16`) |
| Availability Zones | 2 |
| Public Subnets | 2 |
| Private Application Subnets | 2 |
| Private Database Subnets | 2 |
| Internet Gateway | 1 |
| NAT Gateways | 2 (One per AZ) |
| Public Route Tables | 1 |
| Private Route Tables | 3 |
| Application Load Balancer | Deployed across both public subnets |
| ECS Frontend Service | Deployed across both private application subnets |
| ECS Backend Service | Deployed across both private application subnets |
| Amazon RDS PostgreSQL | Multi-AZ deployment using both private database subnets |
