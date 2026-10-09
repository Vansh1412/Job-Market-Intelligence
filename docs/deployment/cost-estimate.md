# Cloud Cost Modeling & Budget Architecture — Job Market Intelligence

**Platform:** Job Market Intelligence (JobIntel)  
**Document:** `docs/deployment/cost-estimate.md`  
**Active Production Architecture:** **Vercel Hobby + Render Free Tier ($0/Month)**  
**Status:** Certified Zero-Cost Architecture  

---

## 1. Active Architecture: Genuinely Free Tier ($0.00 / Month)

The approved production deployment architecture requires **$0.00 / month**, with no paid upgrades, no credit card billing risk, and no paid resource provisioning:

| Service / Resource | Provider & Tier | Quota / Allocation | Measured Usage | Actual Monthly Cost |
|---|---|---|---|:---:|
| **Frontend SPA Hosting** | Vercel Hobby | Unlimited builds, Global Edge CDN, Custom Domain, TLS | ~1.5 MB build bundle | **$0.00** |
| **Backend API Service** | Render Free Web Service | 0.1 CPU, 512 MB RAM, 750 free hrs/mo, 100 GB bandwidth | 309.80 MB Peak RAM | **$0.00** |
| **Private Datasets Storage** | Cloudflare R2 Free Tier *(or AWS S3 Free)* | 10 GB storage free, 10M read ops/mo, $0 egress fees | 10.56 MB storage, ~50 reads/mo | **$0.00** |
| **CI/CD Build Automation** | GitHub Actions (Hosted Ubuntu) | 2,000 free minutes/month for standard pipelines | ~2 min per push | **$0.00** |
| **Domain & SSL/TLS** | Vercel & Render Automatic SSL | Automated Let's Encrypt certificates | Managed automatically | **$0.00** |
| **TOTAL RUNNING COST** | | | | **$0.00 / month** |

### Free-Tier Operating Characteristics
1. **Cold Starts:** When inactive for > 15 minutes, Render Free spins down the container. The first inbound request takes approximately 50 seconds to boot. Subsequent requests respond in sub-100ms.
2. **Memory Ceiling:** Render enforces a 512 MB RAM limit. The single-worker ASGI configuration (`--workers 1`) maintains peak memory at **309.80 MB**, leaving **202 MB of safety headroom**.
3. **Storage Quota:** The 5 certified private runtime datasets require only **10.56 MB** out of Cloudflare R2's 10,000 MB free allocation (>99.9% free buffer).

---

## 2. Archived / Optional Future Enterprise Path (Paid AWS Infrastructure)

> [!NOTE]
> The paid AWS Fargate / ALB infrastructure detailed below was evaluated during Phase 0 and archived as an optional future enterprise path. It is **NOT** provisioned or active.

For reference, if an enterprise deployment requiring zero cold starts and dedicated cloud VPC isolation is desired in the future:

| Resource | Sizing & Allocation | Basis | Estimated Cost |
|---|---|---|---|
| **ECS Fargate Compute** | 1 Task: 0.5 vCPU, 1.0 GB RAM (24/7) | $0.04048/vCPU-hr + $0.004445/GB-hr | $18.02 / month |
| **Application Load Balancer** | 1 ALB (24/7) + 1 LCU | $0.0225/ALB-hr + $0.008/LCU-hr | $16.43 – $22.27 / month |
| **Amazon S3 Storage** | ~20 MB storage + ~100 requests | $0.023/GB-mo | < $0.05 / month |
| **Amazon ECR** | ~1 GB stored compressed image | $0.10/GB-mo | < $0.10 / month |
| **CloudWatch Logs** | ~2 GB ingestion/month | $0.50/GB ingested | ~$1.03 / month |
| **Total Enterprise AWS Baseline** | | | **~$35.65 – $41.50 / month** |
