# Security & Data Governance Specification — Job Market Intelligence

**Platform:** Job Market Intelligence (JobIntel)  
**Document:** `docs/deployment/security-and-data-governance.md`  
**Classification:** Proprietary Research Application  
**Compliance Mandate:** Zero Drift, Zero Retraining, Zero Unauthorized Data Exposure  

---

## 1. Non-Negotiable Scientific & Research Governance Rules

The deployment architecture enforces the following mandatory research contracts:

1. **Zero Retraining Mandate:** Under no circumstances may any model be retrained, refitted, fine-tuned, or regenerated during build, deployment, or runtime operations. All models are frozen historical artifacts.
2. **Feature Dimension Invariance:**
   - USA Feature Vector: **Exactly 123 predictors** (41 preprocessed metadata features + 82 binary skill indicators).
   - India Feature Vector: **Exactly 290 predictors** (6 preprocessed categorical/numerical features + 284 binary skill indicators).
3. **Dual-Market Currency Independence:** USA predictions ($ USD) and India predictions (₹ INR / LPA) remain strictly independent. Foreign exchange (FX) conversion or currency mixing is strictly prohibited to prevent macroeconomic distortions.
4. **Cryptographic Integrity Verification:** The backend singleton `ModelRegistry` verifies the SHA-256 hash of all 10 frozen artifacts before serving inference in memory. If any file checksum differs or is missing, the service fails closed (HTTP 503).
5. **Archetype Clustering Preservation:** Exactly 7 USA archetypes (k=7) and 6 India archetypes (k=6) are maintained with frozen centroid mappings.

---

## 2. Cloud Data Privacy & Access Controls

### 2.1 Private S3 Storage Architecture
- **100% Block Public Access:** All 4 S3 public access block flags (`BlockPublicAcls`, `IgnorePublicAcls`, `BlockPublicPolicy`, `RestrictPublicBuckets`) are active.
- **No Public URLs:** Direct public access or presigned URL generation for model artifacts or Parquet datasets is strictly disabled.
- **Bucket Policy:** Denies all insecure HTTP requests (`aws:SecureTransport = false`).
- **Encryption at Rest:** All objects are encrypted using AES256 server-side encryption.

### 2.2 Least-Privilege IAM Scoping
- **ECS Task Execution Role:** Can only pull container images from private ECR and write log events to CloudWatch.
- **ECS Application Task Role:** Granted read-only permissions (`s3:GetObject`, `s3:ListBucket`) scoped exclusively to the certified bucket ARN. Has zero permissions to write, delete, or alter S3 objects or other AWS resources.
- **GitHub Actions OIDC Role:** Scoped strictly to the specific repository (`Vansh1412/Job-Market-Intelligence`) and the approved branch/environment. Credentials are ephemeral and expire after each run.

---

## 3. Container & Network Security Hardening

| Safeguard | Implementation | Verification Method |
|---|---|---|
| **Non-Root Execution** | Dedicated Linux user `appuser:1000` created in Dockerfile | `USER appuser` directive in Dockerfile |
| **Network Boundary** | ECS Security Group accepts traffic **only** from the ALB Security Group on port 8000 | Security Group Ingress CIDR inspection |
| **TLS Enforcement** | ALB terminates TLS using modern security policy `ELBSecurityPolicy-TLS13-1-2-2021-06` | SSL Labs audit / ALB listener rule |
| **CORS Restriction** | `CORSMiddleware` restricts allowed origins to the production Vercel domain and localhost | Verified via OPTIONS preflight response |
| **Container Vulnerabilities** | Amazon ECR automated scanning (`scan_on_push = true`) | ECR scan results inspection |

---

## 4. Secret Management & Log Sanitization

1. **Zero Committed Secrets:** Git repositories and container images contain no API keys, private passwords, AWS credentials, or `.env` files.
2. **Log Redaction:**
   - FastAPI loggers log request metadata and high-level outcomes.
   - Sensitive prediction payloads, internal local paths (`E:\Job Market`), and stack traces are suppressed in production error responses.
   - All client error responses return sanitized JSON error messages (e.g., `{"detail": "Invalid input format"}`) rather than internal Python tracebacks.
