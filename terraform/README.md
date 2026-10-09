# Job Market Intelligence — AWS Infrastructure as Code (Terraform)

This directory contains production-grade, reproducible Terraform configurations for deploying the Job Market Intelligence platform backend to AWS.

---

## 1. Architecture Overview

The infrastructure provisions a scalable, serverless containerized backend decoupled from local machines:
- **Compute:** AWS ECS Fargate task running the FastAPI container (0.5 vCPU, 1 GB RAM, non-root user `appuser:1000`).
- **Load Balancing:** AWS Application Load Balancer (ALB) across 2 Availability Zones with health probes targeting `/api/ready`.
- **Registry:** Private Amazon ECR repository with automated vulnerability scanning and image retention lifecycle rules.
- **Storage:** Private AWS S3 bucket with **100% Block Public Access**, SSE-S3 encryption at rest, and TLS-only transport enforcement.
- **Security & IAM:** 
  - Application Task Role with least-privilege read-only S3 access to approved bucket prefixes.
  - GitHub Actions OIDC role (`sts:AssumeRoleWithWebIdentity`) strictly scoped to `Vansh1412/Job-Market-Intelligence` and the `production` environment.
  - Zero permanent AWS access keys stored in GitHub Secrets or configuration files.
- **Observability:** AWS CloudWatch Logs with 14-day retention and Container Insights.

---

## 2. Cost Analysis & Resource Sizing

Estimated baseline running costs on AWS (US East `us-east-1`):

| Resource | Configuration | Estimated Cost |
|---|---|---|
| **ECS Fargate** | 1 Task: 0.5 vCPU, 1.0 GB RAM (24/7) | ~$18.15 / month |
| **Application Load Balancer** | 1 ALB (24/7) + 1 LCU | ~$16.43 – $22.25 / month |
| **Amazon S3** | ~20 MB storage + ~1,000 requests | < $0.05 / month |
| **Amazon ECR** | ~1 GB stored compressed images | < $0.10 / month |
| **CloudWatch Logs** | ~2 GB ingestion/month (14-day retention) | ~$1.00 / month |
| **Total Baseline AWS Cost** | | **~$35.65 – $41.50 / month** |

### Budget Alert Guardrail
Before provisioning, set up an AWS Budget alert:
1. Open the **AWS Billing Console** > **Budgets**.
2. Create a budget of **$45.00/month**.
3. Configure alerts at 80% ($36) and 100% ($45) to send an email notification. Note that a budget alert is a monitoring tool and does not shut down resources automatically.

---

## 3. Prerequisites

1. **Terraform CLI:** `>= 1.5.0` installed.
2. **AWS CLI v2:** Configured with permissions to provision VPC, ALB, ECS, ECR, S3, and IAM resources.
3. **Domain & TLS (Optional):** An existing AWS Certificate Manager (ACM) certificate ARN if using a custom HTTPS domain.

---

## 4. Configuration & Deployment Steps

> [!IMPORTANT]
> **GOVERNANCE RULE:** Do NOT execute `terraform apply` without explicit user confirmation.

### Step 1: Initialize Variables
Copy `terraform.tfvars.example` to `terraform.tfvars`:
```bash
cp terraform.tfvars.example terraform.tfvars
```
Edit `terraform.tfvars` with your specific values:
- `s3_bucket_name`: A globally unique S3 bucket name (e.g. `jobintel-artifacts-<your-account-id>-prod`).
- `frontend_cors_origin`: The Vercel URL of your deployed frontend (e.g. `https://jobintel.vercel.app`).
- `certificate_arn`: Optional ACM TLS certificate ARN.

### Step 2: Initialize Terraform
```bash
terraform init
```

### Step 3: Inspect Planned Changes
```bash
terraform plan
```
Carefully review the proposed resources to verify resource names and security group ingress rules.

### Step 4: Apply (Requires Approval)
```bash
terraform apply
```

### Step 5: Upload Initial Certified Artifacts to S3
Once the S3 bucket is created, run the artifact sync helper to upload the certified frozen model artifacts and runtime Parquet files to the private bucket:
```bash
# Set your target bucket
$bucket = (terraform output -raw s3_bucket_name)

# Upload the certified datasets
aws s3 cp data/processed/modeling_dataset.parquet "s3://$bucket/data/processed/modeling_dataset.parquet"
aws s3 cp data/processed/india/india_modeling_cohort.parquet "s3://$bucket/data/processed/india/india_modeling_cohort.parquet"
aws s3 cp data/processed/skill_matrix_technical.parquet "s3://$bucket/data/processed/skill_matrix_technical.parquet"
aws s3 cp data/processed/job_archetype_assignments.parquet "s3://$bucket/data/processed/job_archetype_assignments.parquet"
aws s3 cp data/processed/india/india_skill_analytics.json "s3://$bucket/data/processed/india/india_skill_analytics.json"
```

---

## 5. Teardown / Safe Resource Destruction

To eliminate all AWS charges when the deployment is no longer needed:

```bash
# 1. Empty the S3 bucket (Terraform cannot delete a non-empty bucket)
aws s3 rm "s3://$(terraform output -raw s3_bucket_name)" --recursive

# 2. Destroy all managed resources
terraform destroy
```
Review the list of resources to be destroyed and enter `yes` when prompted.
