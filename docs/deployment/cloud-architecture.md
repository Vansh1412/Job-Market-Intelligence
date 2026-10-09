# Cloud Architecture Specification — Job Market Intelligence

**Platform:** Job Market Intelligence (JobIntel)  
**Document:** `docs/deployment/cloud-architecture.md`  
**Version:** 2.0.0 (Cloud Native)  
**Status:** Approved Target Architecture  

---

## 1. High-Level Architectural Topology

The Job Market Intelligence platform is architected as an independently scalable, decoupled, serverless cloud application. The frontend Single Page Application (SPA) and backend REST API are separated across modern cloud platforms to eliminate any dependency on personal local workstations, local filesystems, Docker Desktop, or self-hosted GitHub Actions runners.

```mermaid
flowchart TB
    subgraph ClientLayer["Edge / Client Layer"]
        User["Browser Client\n(Desktop & Mobile)"]
    end

    subgraph FrontendHosting["Frontend Hosting (Vercel)"]
        VercelCDN["Vercel Global Edge CDN\n(TLS 1.3, DDoS Shield)"]
        SPA["React 19 + TypeScript + Vite SPA\n(Client-Side Routing, Motion Tokens)"]
        VercelCDN --> SPA
    end

    subgraph AWSCloud["AWS Production Environment (us-east-1)"]
        subgraph Ingress["Public Ingress (Dual AZ)"]
            ALB["Application Load Balancer (ALB)\nManaged HTTPS (Port 443) -> HTTP :8000\nHealth Checks on /api/ready"]
        end

        subgraph VPC["Dedicated VPC (10.0.0.0/16)"]
            subgraph SecurityBoundary["Security Group Isolation"]
                ECS["AWS ECS Fargate Task\n(0.5 vCPU / 1.0 GB RAM)\nNon-root appuser:1000\nFastAPI ASGI Server"]
            end
            
            S3Endpoint["VPC Gateway Endpoint (S3)\nInternal Zero-Cost AWS Route"]
        end

        subgraph PrivateStorage["Private Cloud Storage & Registry"]
            S3["Private Amazon S3 Bucket\n(100% Block Public Access)\nSSE-S3 Encryption\nCertified Parquets & Artifacts"]
            ECR["Amazon ECR\nPrivate Docker Registry\n(Vulnerability Scanning)"]
        end

        subgraph Observability["Monitoring & Observability"]
            CW["CloudWatch Log Group\n(/ecs/jobintel-production)\n14-Day Retention, PII Redaction"]
            Metrics["Container Insights & CloudWatch Alarms"]
        end
    end

    subgraph CICD["Automated CI/CD (GitHub Actions)"]
        PR_CI["PR CI Pipeline\n(GitHub-Hosted ubuntu-latest)"]
        ReleaseWorkflow["Protected Release Workflow\n(Environment Approval Gate)"]
        OIDC["AWS IAM OIDC Provider\n(Repo-Scoped Trust Role)"]
    end

    User -->|HTTPS :443| VercelCDN
    User -->|REST API Calls HTTPS :443| ALB
    ALB -->|Forward :8000| ECS
    ECS -->|Startup Sync\nTask Role IAM| S3Endpoint
    S3Endpoint --> S3
    ECS -->|Stdout/Stderr| CW
    ECS -.-> Metrics

    ReleaseWorkflow -->|OIDC AssumeRole| OIDC
    OIDC -->|Push Image| ECR
    OIDC -->|Update Service| ECS
```

---

## 2. Component Specifications

### 2.1 Frontend: React 19 + Vite + TypeScript (Vercel)
- **Role:** Delivers the interactive user interface, exploration dashboards, cross-market comparisons, and real-time salary estimator.
- **Hosting:** Vercel Global Edge Network with automatic Brotli/Gzip compression and immutable asset caching.
- **Configuration:** 
  - `VITE_API_BASE_URL`: Injected during Vercel build time pointing to the deployed AWS ALB URL (e.g. `https://api.jobintel.com` or `https://<alb-dns-name>`).
  - Client-side routing: Handled via `frontend/vercel.json` rewrites to prevent 404s on browser refresh.
- **Security:** Zero cloud credentials or private datasets are ever exposed to the client bundle.

### 2.2 Ingress: Application Load Balancer (AWS ALB)
- **Role:** High-availability reverse proxy and HTTPS termination.
- **Placement:** Spans 2 Availability Zones (`us-east-1a`, `us-east-1b`) in public subnets.
- **Health Monitoring:** Probes `/api/ready` every 30 seconds. Returns healthy only when all 10 frozen artifacts have been cryptographically verified.
- **TLS Policy:** `ELBSecurityPolicy-TLS13-1-2-2021-06` enforcing modern TLS 1.2 and TLS 1.3 ciphers.

### 2.3 Backend Compute: AWS ECS Fargate
- **Role:** Runs the containerized FastAPI production application (`src.backend.main:app`).
- **Resource Sizing:** 0.5 vCPU (512 CPU units), 1.0 GB RAM (1024 MB).
- **Execution Security:** Runs as non-root user `appuser` (UID 1000).
- **Network Security:** Task security group restricts inbound traffic strictly to the ALB security group on port 8000. No direct internet ingress is permitted.
- **Concurrency & Workers:** Uvicorn single/dual worker model with asyncio event loop. Singleton `ModelRegistry` ensures in-memory ML models are shared without duplicate allocations.

### 2.4 Cloud Storage: Private Amazon S3 Bucket
- **Role:** Serves as the authoritative, tamper-proof repository for frozen model files and certified runtime Parquet datasets (`modeling_dataset.parquet`, `india_modeling_cohort.parquet`, `skill_matrix_technical.parquet`, etc.).
- **Security:**
  - **100% Block Public Access** enabled across all 4 AWS controls.
  - Encryption at rest via AES256 (SSE-S3).
  - Bucket policy strictly denies unencrypted transport (`aws:SecureTransport = "false"`).
  - Access is granted exclusively to the ECS Task Role via least-privilege IAM policy.

---

## 3. Dual-Market Isolation Contract

A core scientific requirement of the Job Market Intelligence system is the absolute isolation of the USA and India analytical pipelines:

| Dimension | USA Pipeline | India Pipeline |
|---|---|---|
| **Cohort Size** | 34,036 tech postings | 5,859 tech postings |
| **Model Algorithm** | Tuned XGBoost Regressor | HistGradientBoostingRegressor |
| **Feature Dimension** | **Exactly 123 features** | **Exactly 290 features** |
| **Target Currency** | Native **USD ($)** Annual Salary | Native **INR (₹)** / LPA Midpoint |
| **Exchange Rate Conversion** | **ZERO (Forbidden)** | **ZERO (Forbidden)** |
| **Discovered Archetypes** | 7 Distinct Archetypes (k=7) | 6 Distinct Archetypes (k=6) |
| **Holdout Evaluation MAE** | $36,380.64 | ₹3.71 LPA (₹371,472) |

---

## 4. Cold Startup & Dynamic Synchronization Sequence

When an ECS task starts up on Fargate, the following sequence occurs before taking traffic:

```mermaid
sequenceDiagram
    participant ECS as ECS Fargate Container
    participant S3 as Private AWS S3
    participant Reg as In-Memory ModelRegistry
    participant ALB as Application Load Balancer

    Note over ECS: Container boots up (non-root appuser)
    ECS->>ECS: Execute src/backend/main.py (FastAPI lifespan)
    ECS->>ECS: Load src/backend/config/artifact_manifest.json
    
    alt Artifact missing or hash invalid
        ECS->>S3: Download certified artifact via ECS Task Role (boto3)
        S3-->>ECS: Stream artifact bytes to .download.tmp
        ECS->>ECS: Compute SHA-256 of downloaded file
        alt SHA-256 matches manifest exactly
            ECS->>ECS: Atomically move into target path (/app/data/processed)
        else SHA-256 mismatch (tampered/corrupted)
            ECS->>ECS: Delete .tmp and raise ModelIntegrityError
            Note over ECS: Task crashes / fails closed (Healthcheck 503)
        end
    else Artifact exists locally and hash matches
        ECS->>ECS: Skip S3 download (idempotent cache hit)
    end

    ECS->>Reg: Initialize ModelRegistry singleton
    Reg->>Reg: Verify 10/10 frozen artifacts SHA-256
    Reg->>Reg: Load XGBoost & HistGradientBoosting models into RAM
    Note over Reg: Registry Status: GREEN (10/10 Verified)
    
    ALB->>ECS: Probe GET /api/ready
    ECS-->>ALB: HTTP 200 OK {"status": "ready", "artifacts_verified_count": 10}
    ALB->>ECS: Forward live traffic
```
