# Cloud Cost Modeling & Budget Architecture — Job Market Intelligence

**Platform:** Job Market Intelligence (JobIntel)  
**Document:** `docs/deployment/cost-estimate.md`  
**Pricing Region:** AWS US East (N. Virginia `us-east-1`)  
**Pricing Basis:** Official AWS On-Demand Pricing (October 2026)  

---

## 1. Detailed AWS Cost Breakdown (24/7 Operational Availability)

The following estimate models continuous 24/7/365 production operation:

### 1.1 AWS ECS Fargate Compute
- **Sizing:** 1 Container Task: 0.5 vCPU (512 units), 1.0 GB RAM (1024 MB).
- **Hours per Month:** 730 hours.
- **vCPU Rate:** $0.04048 per vCPU-hour.
  - Cost: `0.5 vCPU * 730 hours * $0.04048 = $14.78 / month`.
- **Memory Rate:** $0.004445 per GB-hour.
  - Cost: `1.0 GB * 730 hours * $0.004445 = $3.24 / month`.
- **Subtotal Fargate Compute:** **$18.02 / month**.

### 1.2 AWS Application Load Balancer (ALB)
- **ALB Base Rate:** $0.0225 per hour.
  - Base Cost: `730 hours * $0.0225 = $16.43 / month`.
- **Load Balancer Capacity Units (LCU):** 1 LCU assumed for low-to-medium traffic (new connections, active connections, bandwidth).
  - Rate: $0.008 per LCU-hour.
  - LCU Cost: `730 hours * $0.008 = $5.84 / month` (maximum baseline).
- **Subtotal Application Load Balancer:** **$16.43 – $22.27 / month**.

### 1.3 Amazon S3 Storage & API Requests
- **Storage Volume:** ~20 MB (frozen models + runtime Parquet datasets).
  - Rate: $0.023 per GB-month.
  - Cost: `0.02 GB * $0.023 = $0.00046 / month` (negligible).
- **Requests:** ~100 GET requests on container restarts.
  - Rate: $0.0004 per 1,000 GET requests.
  - Cost: `< $0.01 / month`.
- **Subtotal Amazon S3:** **< $0.05 / month**.

### 1.4 Amazon Elastic Container Registry (ECR)
- **Storage Volume:** 1 active compressed Docker image (~600 MB). Lifecycle policy expires old images past 5 revisions.
- **Rate:** $0.10 per GB-month.
- **Subtotal Amazon ECR:** **~$0.06 – $0.10 / month**.

### 1.5 AWS CloudWatch Logs & Monitoring
- **Ingestion:** ~2 GB log events per month (FastAPI request logs, health probes).
  - Rate: $0.50 per GB ingested = $1.00 / month.
- **Storage:** 14-day retention (~1 GB average stored).
  - Rate: $0.03 per GB-month = $0.03 / month.
- **Subtotal CloudWatch:** **~$1.03 / month**.

### 1.6 Network Data Transfer Out
- **AWS Data Transfer Out to Internet:** First 100 GB per month is free under AWS Free Tier / standard allowance. Beyond 100 GB: $0.09/GB.
- **Subtotal Data Transfer:** **$0.00 / month**.

### 1.7 Frontend Hosting (Vercel)
- **Tier:** Vercel Hobby Plan (Personal/Project tier).
- **Includes:** Global Edge Network, automated SSL/TLS certificates, Git deployments, analytics.
- **Subtotal Vercel:** **$0.00 / month**.

---

## 2. Summary Monthly Cost Estimate

| Resource Category | Minimum Monthly | Expected Monthly | Maximum Baseline |
|---|---|---|---|
| **ECS Fargate Compute** | $18.02 | $18.02 | $18.02 |
| **Application Load Balancer** | $16.43 | $18.50 | $22.27 |
| **Amazon S3 Storage** | $0.01 | $0.02 | $0.05 |
| **Amazon ECR Storage** | $0.05 | $0.08 | $0.10 |
| **CloudWatch Logs** | $0.50 | $1.03 | $2.00 |
| **Data Transfer** | $0.00 | $0.00 | $0.50 |
| **Vercel Frontend** | $0.00 | $0.00 | $0.00 |
| **TOTAL ESTIMATED MONTHLY COST** | **$35.01** | **$37.65** | **$42.94** |

---

## 3. Cost Control & Spending Guardrails

### 3.1 AWS Budget Alert Setup
To prevent surprise charges or billing spikes:
1. Open the **AWS Billing and Cost Management Console**.
2. Go to **Budgets** > **Create budget**.
3. Choose **Cost budget** and name it `JobIntel-Monthly-Budget`.
4. Set the budget amount to **$45.00 / month**.
5. Configure alerts:
   - Alert 1: When forecasted spend exceeds **80% ($36.00)**.
   - Alert 2: When actual spend exceeds **100% ($45.00)**.
   - Add your email address to receive immediate notifications.

> [!NOTE]
> A budget alert notifies you via email. AWS does not provide a native hard kill-switch by default, so immediate manual inspection is recommended if an alert triggers.

### 3.2 Optional Cost-Reduction Architectures
If the ~$37/month ALB baseline is higher than desired:
1. **Fargate Spot:** Switching the ECS capacity provider to Fargate Spot reduces the Fargate compute cost by up to 70% (from $18.02 down to ~$5.40/month), reducing total cost to ~$23/month.
2. **API Gateway HTTP API + Cloud Map:** Replacing the ALB with an Amazon API Gateway HTTP API ($1.00 per million requests, zero hourly base fee) and VPC Private Link would reduce the fixed cost to ~$19/month total.
