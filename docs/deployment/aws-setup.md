# AWS Setup & Provisioning Guide — Job Market Intelligence

**Platform:** Job Market Intelligence (JobIntel)  
**Document:** `docs/deployment/aws-setup.md`  
**Audience:** Cloud Architects, DevSecOps Engineers  
**Prerequisites:** AWS CLI v2, Terraform `>= 1.5.0`  

---

## 1. Initial AWS Account Setup & Permissions

Ensure your local AWS CLI is authenticated with sufficient administrative privileges to provision VPCs, ECS clusters, ECR repositories, S3 buckets, and IAM roles:

```bash
aws sts get-caller-identity
```
Verify that the output displays your valid AWS Account ID and IAM Principal.

---

## 2. Infrastructure as Code (Terraform) Provisioning

> [!IMPORTANT]
> **GOVERNANCE RULE:** Do NOT provision infrastructure or execute `terraform apply` without explicit project approval.

### Step 2.1: Configure Variables
Navigate to the `terraform/` directory and create `terraform.tfvars`:

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:
- `s3_bucket_name`: Provide a unique bucket name, e.g., `jobintel-artifacts-prod-12345`.
- `frontend_cors_origin`: Set to your Vercel deployment URL (e.g. `https://jobintel.vercel.app`).
- `aws_region`: Defaults to `us-east-1`.

### Step 2.2: Initialize and Plan
```bash
terraform init
terraform plan -out=tfplan
```
Review the execution plan. Ensure that:
- 1 S3 Bucket with Public Access Block is created.
- 1 ECR Repository with vulnerability scanning is created.
- 1 ECS Cluster and Service with Fargate launch type is created.
- 1 Application Load Balancer with target group probing `/api/ready` is created.
- 1 GitHub Actions OIDC provider and scoped IAM role is created.

### Step 2.3: Apply Infrastructure
```bash
terraform apply tfplan
```

### Step 2.4: Save Outputs
Capture the generated infrastructure outputs:
```bash
$ECR_REPO = terraform output -raw ecr_repository_url
$ALB_DNS  = terraform output -raw alb_dns_name
$S3_BUCKET = terraform output -raw s3_bucket_name
$OIDC_ROLE = terraform output -raw github_actions_role_arn
```

---

## 3. Upload Certified Artifacts to S3

Once the private S3 bucket is created, upload the certified private datasets from your secure workstation into the bucket:

```bash
# S3 Destination Prefix
$BUCKET = "<your-s3-bucket-name>"

# Upload private runtime datasets
aws s3 cp data/processed/modeling_dataset.parquet "s3://$BUCKET/data/processed/modeling_dataset.parquet"
aws s3 cp data/processed/india/india_modeling_cohort.parquet "s3://$BUCKET/data/processed/india/india_modeling_cohort.parquet"
aws s3 cp data/processed/skill_matrix_technical.parquet "s3://$BUCKET/data/processed/skill_matrix_technical.parquet"
aws s3 cp data/processed/job_archetype_assignments.parquet "s3://$BUCKET/data/processed/job_archetype_assignments.parquet"
aws s3 cp data/processed/india/india_skill_analytics.json "s3://$BUCKET/data/processed/india/india_skill_analytics.json"
```

Verify that all 5 files are present in the S3 bucket:
```bash
aws s3 ls "s3://$BUCKET/data/processed/" --recursive
```

---

## 4. Initial Container Image Build & ECR Push

Authenticate Docker to your private Amazon ECR repository:

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_REPO
```

Build the multi-stage production image:
```bash
docker build -t jobintel-backend:latest .
```

Tag and push the image to ECR:
```bash
docker tag jobintel-backend:latest "$ECR_REPO:latest"
docker push "$ECR_REPO:latest"
```

---

## 5. Verify ECS Service Health

Force a new deployment of the ECS service so the tasks pull the freshly pushed ECR image:

```bash
aws ecs update-service --cluster jobintel-cluster-production --service jobintel-service-production --force-new-deployment
```

Wait for the service to stabilize:
```bash
aws ecs wait services-stable --cluster jobintel-cluster-production --service jobintel-service-production
```

Test the live Application Load Balancer health endpoint:
```bash
curl -i "http://$ALB_DNS/api/ready"
```
**Expected Output:**
```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "ready",
  "ready": true,
  "artifacts_verified_count": 10,
  "markets": ["USA", "India"]
}
```

---

## 6. Configuring Custom Domain & Managed TLS (Optional)

1. **Request Certificate:** In AWS Certificate Manager (ACM), request a public certificate for your backend domain (e.g., `api.jobintel.com`).
2. **DNS Validation:** Add the CNAME validation records to your DNS provider (e.g. Route 53 or Cloudflare).
3. **Update Terraform:** Set `certificate_arn` in `terraform.tfvars` and run `terraform apply`.
4. **Point CNAME:** Create a CNAME record pointing `api.jobintel.com` to the ALB DNS name.
