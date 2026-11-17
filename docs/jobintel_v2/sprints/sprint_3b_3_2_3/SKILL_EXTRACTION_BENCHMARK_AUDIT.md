# SKILL EXTRACTION BENCHMARK AUDIT
## Independent Verification of `SYS_SKILL_EXTRACTOR` Adversarial Filtering

**Sprint ID:** 3B.3.2.3  
**Audited Artifacts:**
- Evaluator: `docs/jobintel_v2/sprints/sprint_3b_3_2/SKILL_EXTRACTION_EVALUATION.md`
- Audit Record: `docs/jobintel_v2/sprints/sprint_3b_3_2_2/SKILL_EXTRACTION_RELIABILITY_AUDIT.md`
- Reconciled Data: `docs/jobintel_v2/sprints/sprint_3b_3_2_3/skill_extraction_benchmark.csv`
- Standard: `JOBINTEL-STD-PRED-001`

---

## 1. Objective & Challenge Specification

Extracting single-letter and short-acronym technical skills (`Go`, `C`, `R`, `ML`, `AI`, `AWS`) from unstructured natural language job requisitions presents severe false-positive risks:
- `"Go"` frequently appears as a common verb (*"We go to great lengths"*).
- `"C"` appears in licensing (*"Class C driver license"*), grading (*"Grade C"*), and vitamins (*"Vitamin C"*).
- `"R"` appears in regulatory clauses (*"Section R"*, *"Paragraph R"*).
- `"AWS"` can match substring overlaps (*"as well as"*).
- `"ML"` matches metric liquid volumes (*"50 ml"*).
- `"AI"` matches proper names (*"Ai Weiwei"*).

Sprint 3B.3.2 introduced a 5-token contextual co-occurrence guard in `SYS_SKILL_EXTRACTOR` and asserted **"100% precision on skill extraction."** This audit examines the empirical evidence supporting this assertion.

---

## 2. Adversarial Benchmark Evaluation (20 Cases)

The benchmark evaluated 20 targeted, hand-crafted adversarial phrases designed to probe boundary conditions:

| ID | Token | Test Sentence | Target Nature | Guard Action | Outcome | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **SK-001** | `Go` | *"We need a Go developer with 4 years experience"* | Technical | Extracted (`Go developer`) | PASS | Exact |
| **SK-002** | `Go` | *"Let us go to the market tomorrow"* | Colloquial | Suppressed (Verb) | PASS | Exact |
| **SK-003** | `Go` | *"Looking for Golang software engineers"* | Technical | Extracted (`Golang` $\to$ `Go`) | PASS | Exact |
| **SK-004** | `C` | *"Proficient in C programming and embedded systems"* | Technical | Extracted (`C programming`) | PASS | Exact |
| **SK-005** | `C` | *"Applicants must possess a valid Class C driver license"* | Colloquial | Suppressed (`Class C`) | PASS | Exact |
| **SK-006** | `C` | *"Expertise in C++ and C# required"* | Technical | Extracted (`C++`, `C#`) | PASS | Exact |
| **SK-007** | `R` | *"Data scientist skilled in R programming and stats"* | Technical | Extracted (`R programming`) | PASS | Exact |
| **SK-008** | `R` | *"Please see Section R of the employee handbook"* | Colloquial | Suppressed (`Section R`) | PASS | Exact |
| **SK-009** | `R` | *"Candidates should know Python and R for data science"* | Technical | Extracted (`Python and R`) | PASS | Exact |
| **SK-010** | `SQL`| *"Must write complex SQL queries and stored procedures"* | Technical | Extracted (`SQL queries`) | PASS | Exact |
| **SK-011** | `SQL`| *"NoSQL database experience with MongoDB or Cassandra"* | Technical | Extracted (`NoSQL`, `MongoDB`)| PASS | Exact |
| **SK-012** | `AWS`| *"Architect cloud workloads on AWS cloud platform"* | Technical | Extracted (`AWS cloud`) | PASS | Exact |
| **SK-013** | `AWS`| *"Candidate must pass drug test as well as background"*| Colloquial | Suppressed (`as well as`) | PASS | Exact |
| **SK-014** | `ML` | *"Senior ML engineer building LLM applications"* | Technical | Extracted (`ML engineer`) | PASS | Exact |
| **SK-015** | `ML` | *"Apply 50 ml of solution during manufacturing"* | Colloquial | Suppressed (`50 ml`) | PASS | Exact |
| **SK-016** | `AI` | *"Deploying AI models to production environments"* | Technical | Extracted (`AI models`) | PASS | Exact |
| **SK-017** | `AI` | *"Ai Weiwei modern art museum design curator"* | Colloquial | Suppressed (Proper Name) | PASS | Exact |
| **SK-018** | `Java`| *"Core Java backend development with Spring Boot"* | Technical | Extracted (`Java backend`) | PASS | Exact |
| **SK-019** | `Java`| *"Travel to Java island for offshore customer site"* | Colloquial | Suppressed (`Java island`) | PASS | Exact |
| **SK-020** | `Docker`|*"Container orchestration using Docker and Kubernetes"* | Technical | Extracted (`Docker`) | PASS | Exact |

### 2.1 Benchmark Results Summary
- **Total Test Cases:** 20
- **Technical In-Scope Instances:** 11 / 11 Correctly Extracted (Sensitivity = 100.0%)
- **Colloquial False-Positive Traps:** 9 / 9 Correctly Rejected (Specificity = 100.0%)
- **Accuracy on Benchmark Suite:** 20 / 20 = **100.00%** (95% Wilson CI: `[83.89% – 100.00%]`)

---

## 3. Methodological Critique & Production Limitations

While the 5-token contextual co-occurrence guard works as designed for these targeted patterns, asserting generalized "100% precision" across all production text is statistically overreaching:

1. **Sample Size Constraint:**
   - Evaluating 20 sentences yields a wide 95% Wilson score confidence interval of `[83.89% - 100.00%]`. A true production error rate of 5%–10% is entirely compatible with observing zero errors on 20 trials.
2. **Grammatical Complexity in Wild Postings:**
   - Uncurated job postings contain typos, unpunctuated bullet lists, and novel idioms (*"go-getter"*, *"vitamin C"*, *"R&D tax credits"*, *"C-suite"*).
3. **Mandatory Production Guardrails:**
   - The UI must never claim "100% skill extraction accuracy."
   - Extracted skill demand charts must display the underlying sample size $N$ of analyzed job postings (e.g., *"Extracted from N=1,420 postings"*).

---

## 4. Audit Verdict

- **Status:** **RECONCILED — CONDITIONAL GO**
- **Action:** Reclassify claim CLM-005 to `VERIFIED_WITH_LIMITATIONS`. Require sample size badges ($N$) on all skill demand UI components.
