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
