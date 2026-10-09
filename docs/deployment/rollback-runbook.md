# Production Rollback Runbook — Job Market Intelligence

**Platform:** Job Market Intelligence (JobIntel)  
**Document:** `docs/deployment/rollback-runbook.md`  
**SLA:** RTO < 5 minutes, Zero Data Loss  

---

## 1. Rollback Strategy & Mechanisms

The Job Market Intelligence architecture provides two independent layers of rollback protection:

1. **ECS Deployment Circuit Breaker (Automatic):** Configured with `rollback = true`. If a new task fails container health checks (`/api/ready`) 3 consecutive times during startup, AWS ECS automatically cancels the deployment and reinstates the previously healthy task definition revision.
2. **Workflow Post-Deployment Rollback (Automatic):** If the deployment succeeds at the ECS level but fails live API smoke tests (e.g. inference schema error), Step `Automatic Rollback on Smoke Test Failure` in `.github/workflows/deploy-aws.yml` instantly executes `aws ecs update-service` targeting `$PREVIOUS_TASK_DEF`.
3. **Emergency Manual Rollback (Operator):** If an unexpected regression is discovered post-release, the operator can manually restore the previous revision in seconds.

---

## 2. Emergency Manual Rollback Procedure

### Method A: AWS CLI (Fastest)

1. Find the previous stable Task Definition revision:
```bash
aws ecs list-task-definitions --family-prefix jobintel-task-production --sort DESC --max-items 5
```
*(Example output: `jobintel-task-production:12` was current, `jobintel-task-production:11` was previous stable).*

2. Roll back the service to the previous stable revision:
```bash
aws ecs update-service \
  --cluster jobintel-cluster-production \
  --service jobintel-service-production \
  --task-definition jobintel-task-production:11
```

3. Wait for rollback stabilization:
```bash
aws ecs wait services-stable \
  --cluster jobintel-cluster-production \
  --service jobintel-service-production
```

4. Confirm health:
```bash
curl -i "https://api.jobintel.com/api/ready"
```

---

### Method B: AWS Management Console

1. Navigate to **Amazon ECS** > **Clusters** > `jobintel-cluster-production`.
2. Click the **Services** tab and select `jobintel-service-production`.
3. Click **Update service**.
4. In **Task definition revision**, select the previous revision number from the dropdown.
5. Click **Update** at the bottom of the page.
6. Monitor the **Deployments** tab until the rollback deployment status shows **COMPLETED**.

---

### Method C: Vercel Frontend Rollback

If a frontend bug is discovered on Vercel:
1. Open the **Vercel Dashboard** > select `jobintel` project.
2. Navigate to the **Deployments** tab.
3. Locate the previous production deployment.
4. Click the **...** menu on that deployment and select **Instant Rollback**.
5. The global edge network will switch traffic to the previous bundle within 3 seconds.

---

## 3. Post-Rollback Verification & RCA

Following any rollback:
1. Confirm `/api/ready` returns HTTP 200 with `artifacts_verified_count: 10`.
2. Inspect CloudWatch logs for the failing container tasks:
   ```bash
   aws logs filter-log-events \
     --log-group-name /ecs/jobintel-production \
     --filter-pattern "CRITICAL"
   ```
3. Document root cause analysis (RCA) in `reports/incidents/`.
