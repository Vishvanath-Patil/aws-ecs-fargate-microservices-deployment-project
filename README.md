# ConnectHub Lite

A local microservices web app with one frontend, four backend services, and Postgres. It is designed so you can test it locally with Docker Compose and then push the same containers to AWS ECS Fargate.

## Services

- `frontend`: static web UI served by Nginx on `http://localhost:3000`
- `auth-service`: register, login, and JWT identity on `http://localhost:8001` or `http://localhost:3000/api/auth`
- `user-service`: user profile APIs on `http://localhost:8002` or `http://localhost:3000/api/user`
- `post-service`: feed APIs on `http://localhost:8003` or `http://localhost:3000/api/post`
- `like-service`: post like counters/toggles on `http://localhost:8004` or `http://localhost:3000/api/like`
- `database`: Postgres 16 on `localhost:5432`

## Run Locally

```powershell
Copy-Item .env.example .env
docker compose up --build -d
```

Open `http://localhost:3000`, register a user, save a profile, create a post, and like it.

Check that everything is running:

```powershell
docker compose ps
```

If containers show `Created` instead of `Up`, start them:

```powershell
docker compose up -d
```

Useful health checks:

```powershell
Invoke-RestMethod http://localhost:8001/health
Invoke-RestMethod http://localhost:8002/health
Invoke-RestMethod http://localhost:8003/health
Invoke-RestMethod http://localhost:8004/health
```

## AWS ECS Deployment

The app includes `deploy/ecs-cloudformation.yml` for ECS Fargate plus RDS Postgres. A practical deployment flow is:

1. Create five ECR repositories: `devconnect-frontend`, `devconnect-auth`, `devconnect-user`, `devconnect-post`, `devconnect-like`.
2. Build and push the images.
3. Deploy the CloudFormation stack with your VPC, public subnet IDs, private subnet IDs, image URIs, database password, and JWT secret.

Example image push commands:

```powershell
$region="ap-south-1"
$account="<your-account-id>"
aws ecr get-login-password --region $region | docker login --username AWS --password-stdin "$account.dkr.ecr.$region.amazonaws.com"

docker build -t devconnect-frontend ./frontend
docker tag devconnect-frontend "$account.dkr.ecr.$region.amazonaws.com/devconnect-frontend:latest"
docker push "$account.dkr.ecr.$region.amazonaws.com/devconnect-frontend:latest"

docker build -t devconnect-auth ./auth-service
docker tag devconnect-auth "$account.dkr.ecr.$region.amazonaws.com/devconnect-auth:latest"
docker push "$account.dkr.ecr.$region.amazonaws.com/devconnect-auth:latest"
```

Repeat the same build/tag/push pattern for `user-service`, `post-service`, and `like-service`.

Deploy stack:

```powershell
aws cloudformation deploy `
  --region ap-south-1 `
  --stack-name devconnect-lite `
  --template-file deploy/ecs-cloudformation.yml `
  --capabilities CAPABILITY_NAMED_IAM `
  --parameter-overrides `
    VpcId=vpc-xxxx `
    PublicSubnetIds=subnet-public1,subnet-public2 `
    PrivateSubnetIds=subnet-private1,subnet-private2 `
    FrontendImage=<frontend-ecr-uri>:latest `
    AuthImage=<auth-ecr-uri>:latest `
    UserImage=<user-ecr-uri>:latest `
    PostImage=<post-ecr-uri>:latest `
    LikeImage=<like-ecr-uri>:latest `
    JwtSecret=<long-random-secret> `
    DbPassword=<strong-db-password>
```

The CloudFormation template exposes the frontend at `/` and routes API traffic through the same public load balancer at `/api/auth/*`, `/api/user/*`, `/api/post/*`, and `/api/like/*`.
