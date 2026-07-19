# 🏗️ AWS Network Infrastructure Plan

> **Project:** Amazon ECS Fargate with Application Load Balancer and
> Amazon RDS PostgreSQL (Multi-AZ)

------------------------------------------------------------------------

# VPC

  -----------------------------------------------------------------------
  Resource          Name              CIDR Block        Purpose
  ----------------- ----------------- ----------------- -----------------
  **VPC**           **Project-VPC**   **10.0.0.0/16**   Provides an
                                                        isolated network
                                                        for ALB, ECS
                                                        Services, NAT
                                                        Gateways, and
                                                        Amazon RDS.

  -----------------------------------------------------------------------

------------------------------------------------------------------------

# Availability Zones

  -----------------------------------------------------------------------
  AZ                                  Purpose
  ----------------------------------- -----------------------------------
  **AZ-1**                            Primary deployment zone for public,
                                      application, and database
                                      resources.

  **AZ-2**                            Secondary deployment zone providing
                                      high availability and failover
                                      capability.
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# Subnets

  ----------------------------------------------------------------------------------------------
  Subnet                           AZ             CIDR            Type       Purpose
  -------------------------- --------------- --------------- --------------- -------------------
  **Public-Subnet-A**             AZ-1         10.0.1.0/24       Public      Hosts ALB and NAT
                                                                             Gateway-A.

  **Public-Subnet-B**             AZ-2         10.0.2.0/24       Public      Hosts ALB and NAT
                                                                             Gateway-B.

  **Private-App-Subnet-A**        AZ-1        10.0.11.0/24       Private     Hosts ECS Frontend
                                                                             and Backend tasks.

  **Private-App-Subnet-B**        AZ-2        10.0.12.0/24       Private     Hosts ECS Frontend
                                                                             and Backend tasks
                                                                             for HA.

  **Private-DB-Subnet-A**         AZ-1        10.0.21.0/24       Private     Hosts Amazon RDS
                                                                             PostgreSQL
                                                                             (Primary).

  **Private-DB-Subnet-B**         AZ-2        10.0.22.0/24       Private     Used for RDS
                                                                             Multi-AZ
                                                                             standby/failover.
  ----------------------------------------------------------------------------------------------

------------------------------------------------------------------------

# Internet Gateway

  -----------------------------------------------------------------------
  Resource          Name              Attached To       Purpose
  ----------------- ----------------- ----------------- -----------------
  **Internet        **Project-IGW**   Project-VPC       Enables Internet
  Gateway**                                             connectivity for
                                                        public subnets.

  -----------------------------------------------------------------------

------------------------------------------------------------------------

# NAT Gateways

  ------------------------------------------------------------------------------------
  NAT Gateway                AZ        Public Subnet        Elastic IP    Purpose
  ------------------- ---------------- ----------------- ---------------- ------------
  **NAT-Gateway-A**         AZ-1       Public-Subnet-A          ✅        Allows
                                                                          outbound
                                                                          Internet
                                                                          access for
                                                                          private
                                                                          resources in
                                                                          AZ-1.

  **NAT-Gateway-B**         AZ-2       Public-Subnet-B          ✅        Allows
                                                                          outbound
                                                                          Internet
                                                                          access for
                                                                          private
                                                                          resources in
                                                                          AZ-2.
  ------------------------------------------------------------------------------------

------------------------------------------------------------------------

# Route Tables

  ---------------------------------------------------------------------------------
  Route Table            Associated Subnets     Default Route     Purpose
  ---------------------- ---------------------- ----------------- -----------------
  **Public-RT**          Public-Subnet-A,       0.0.0.0/0 → IGW   Allows Internet
                         Public-Subnet-B                          access for public
                                                                  resources.

  **Private-App-RT-A**   Private-App-Subnet-A   0.0.0.0/0 →       Enables outbound
                                                NAT-Gateway-A     Internet access
                                                                  for ECS tasks in
                                                                  AZ-1.

  **Private-App-RT-B**   Private-App-Subnet-B   0.0.0.0/0 →       Enables outbound
                                                NAT-Gateway-B     Internet access
                                                                  for ECS tasks in
                                                                  AZ-2.

  **Private-DB-RT**      Private-DB-Subnet-A,   Local Only        Keeps database
                         Private-DB-Subnet-B                      isolated while
                                                                  allowing VPC
                                                                  communication.
  ---------------------------------------------------------------------------------

------------------------------------------------------------------------

# Architecture Summary

  Component                      Count  Notes
  ----------------------------- ------- ------------------------
  VPC                              1    10.0.0.0/16
  Availability Zones               2    High Availability
  Public Subnets                   2    ALB + NAT
  Private Application Subnets      2    ECS Services
  Private Database Subnets         2    Amazon RDS
  Internet Gateway                 1    Public Internet Access
  NAT Gateways                     2    One per AZ
  Public Route Tables              1    Shared
  Private Route Tables             3    App-A, App-B, Database

------------------------------------------------------------------------

# Design Benefits

-   ✅ High Availability across two Availability Zones.
-   ✅ Internet-facing ALB deployed in public subnets.
-   ✅ ECS services remain in private subnets.
-   ✅ PostgreSQL database is isolated from the Internet.
-   ✅ One NAT Gateway per AZ eliminates a single point of failure.
-   ✅ Architecture follows AWS Well-Architected Framework best
    practices.
