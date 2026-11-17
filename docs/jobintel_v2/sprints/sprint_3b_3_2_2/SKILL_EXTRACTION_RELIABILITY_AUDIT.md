# JOBINTEL 2.0 — SKILL EXTRACTION RELIABILITY AUDIT
## Independent Audit of Context-Guarded Skill Extraction, Short-Token Ambiguity & Benchmark Scope

**Sprint:** 3B.3.2.2 — Global Prediction Reliability, Calibration & Claims Audit  
**Auditor Role:** Senior ML Reliability Engineer, NLP & Taxonomy Auditor  
**System Audited:** `SYS_SKILL_EXTRACTOR` (Contextual Skill Extraction Engine)  
**Dataset Reference:** `docs/jobintel_v2/sprints/sprint_3b_3_2_2/SKILL_EXTRACTION_TEST_CASES.csv`  

---

## 1. THE SHORT-TOKEN AMBIGUITY CHALLENGE

In labour market text mining, single-letter, two-letter, and common acronym tokens present severe risks of false-positive semantic hallucination:
- `Go`: Matches the English verb "go" (e.g. "go to market", "go-getter").
- `C`: Matches letter grades, contract clauses, and funding rounds (e.g. "Series C funding", "Grade C").
- `R`: Matches corporate divisions and organizational jargon (e.g. "R&D", "Section R").
- `SQL`, `AWS`, `ML`, `AI`: Can appear in non-technical product codes, abbreviations, or measurements (e.g. "50 ml dosage").

---

## 2. THE 5-TOKEN CONTEXTUAL CO-OCCURRENCE PROTOCOL

To eliminate naive regex over-matching without requiring brittle, slow deep learning models, JOBINTEL engineered the **5-Token Contextual Co-occurrence Window Protocol**:

```
+----------------------------------------------------------------------------------------------------+
| 5-TOKEN CONTEXTUAL CO-OCCURRENCE ARCHITECTURE                                                     |
+----------------------------------------------------------------------------------------------------+
| Input Text:  "Seeking an engineer proficient in Go (Golang) microservices architecture..."        |
| Token Match: "Go" identified at character offset 42                                               |
| Context Window: [-5 tokens, +5 tokens] -> ["engineer", "proficient", "in", "golang", "microservices"]|
| Technical Guard List for Go: [golang, microservices, goroutines, channels, docker, backend, etc.] |
| Guard Decision: Found "golang" & "microservices" -> VALIDATED TECHNICAL SKILL                     |
|                                                                                                    |
| Adversarial Input: "Must be ready to go to market with the enterprise sales leadership..."         |
| Context Window: ["ready", "to", "to", "market", "with"]                                            |
| Guard Decision: Zero technical indicators found -> REJECTED COLLOQUIAL USAGE                      |
+----------------------------------------------------------------------------------------------------+
```

---

## 3. INDEPENDENT ADVERSARIAL BENCHMARK REPRODUCTION

The 20 adversarial test cases in [SKILL_EXTRACTION_TEST_CASES.csv](file:///e:/Job%20Market/docs/jobintel_v2/sprints/sprint_3b_3_2_2/SKILL_EXTRACTION_TEST_CASES.csv) were independently executed:

```
+----------------------------------------------------------------------------------------------------+
| ADVERSARIAL SKILL BENCHMARK REPRODUCTION SCORECARD (20 PHRASES)                                   |
+--------------------------+-----------------------+--------------------+----------------------------+
| Metric Parameter         | Raw Regex Baseline    | 5-Token Guard (V2) | Operational Impact         |
+--------------------------+-----------------------+--------------------+----------------------------+
| Technical Recall (10 TCs)| 10 / 10 (100.0%)      | 10 / 10 (100.0%)   | Zero valid skills missed   |
| Colloquial Rejection (10)| 2 / 10 (20.0%)        | 10 / 10 (100.0%)   | +80.0% specificity gain    |
| False Positive Detections| 8 / 10 (80.0% FP)     | 0 / 10 (0.0% FP)   | Eliminated false skills    |
| Overall Benchmark Acc    | 12 / 20 (60.0%)       | 20 / 20 (100.0%)   | High adversarial accuracy  |
+--------------------------+-----------------------+--------------------+----------------------------+
```

---

## 4. CRITICAL AUDIT DISTINCTION: TEST SUITE VS. PRODUCTION PERFORMANCE

### The Fallacy to Ban Permanently
A critical reporting defect identified in earlier sprints was phrasing benchmark test passes as general claims of production model accuracy:
> ❌ *"5-token contextual co-occurrence window achieves 100% precision on skill extraction."*

### Mandatory Governance Distinction
The Reliability Standard mandates strict separation across four distinct levels of software validation:

```
====================================================================================================
THE FOUR TIERS OF MODEL VALIDATION
====================================================================================================
Tier 1: Unit Test Pass             Proves that specific hand-crafted software code executes without 
                                   crashing and returns the expected assertion.
Tier 2: Benchmark Performance      Proves that the algorithm achieves a measured metric on a curated, 
                                   fixed evaluation sample (e.g. 100% on 20 test cases).
Tier 3: Independent Evaluation     Proves out-of-sample performance on an unseen, representative 
                                   labour market corpus with independent ground truth labels.
Tier 4: Production Reliability     Measures real-world longitudinal error rates under diverse, noisy, 
                                   unfiltered internet vacancy feeds.
====================================================================================================
```

**Auditor Directive:**
A passing 20-case test suite **only proves that the 20 tested phrases behaved correctly**. It must **never** be cited as evidence of "100% production accuracy." All user-facing skill cards must display the underlying posting sample size ($N$) and include standard NLP disclaimer tooltips.
