# Launch an EC2 Docker Build Server for Amazon ECR

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

  Setting          Recommended Value
  ---------------- -----------------------------------------
  AMI              Amazon Linux 2023 (Preferred)
  Instance Type    t3.medium
  Root Volume      20 GB gp3
  VPC              Your project VPC
  Public Subnet    Yes (or Private + SSM)
  Public IP        Enabled (if using SSH)
  Security Group   Allow SSH (22) only from **Your IP**
  IAM Role         `iam-role-grant-ec2-ssm-and-ecr-access`

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

# Login to Amazon ECR

Replace placeholders:

``` bash
AWS_REGION=ap-southeast-1
ACCOUNT_ID=<AWS_ACCOUNT_ID>
REPOSITORY=<ECR_REPOSITORY_NAME>
```

Login:

``` bash
aws ecr get-login-password --region $AWS_REGION \
| docker login \
--username AWS \
--password-stdin $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
```

Expected:

``` text
Login Succeeded
```

------------------------------------------------------------------------

# Clone Your Application

``` bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd <PROJECT_DIRECTORY>
```

------------------------------------------------------------------------

# Build Docker Image

``` bash
docker build -t $REPOSITORY:latest .
```

Verify:

``` bash
docker images
```

------------------------------------------------------------------------

# Tag Image

``` bash
docker tag $REPOSITORY:latest \
$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPOSITORY:latest
```

------------------------------------------------------------------------

# Push Image to Amazon ECR

``` bash
docker push \
$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPOSITORY:latest
```

Verify:

AWS Console → Amazon ECR → Repository → Images

------------------------------------------------------------------------

