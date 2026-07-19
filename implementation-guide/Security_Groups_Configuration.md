# Security Groups Configuration

  ------------------------------------------------------------------------------
  Security Group           Inbound Rule          Source           Purpose
  ------------------------ --------------------- ---------------- --------------
  **ALB-SG**               HTTP (TCP 80)         `0.0.0.0/0`      Allows users
                                                                  on the
                                                                  Internet to
                                                                  access the
                                                                  Application
                                                                  Load Balancer.

  **Frontend-SG**          HTTP (TCP 80)         **ALB-SG**       Allows only
                                                                  the ALB to
                                                                  forward
                                                                  requests to
                                                                  the Frontend
                                                                  application.

  **Backend-SG**           TCP 8000              **ALB-SG**       Allows only
                                                                  the ALB to
                                                                  forward API
                                                                  requests to
                                                                  the Backend
                                                                  application.

  **Database-SG**          PostgreSQL (TCP 5432) **Backend-SG**   Allows only
                                                                  the Backend
                                                                  application to
                                                                  connect to the
                                                                  PostgreSQL
                                                                  database.
  ------------------------------------------------------------------------------

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
