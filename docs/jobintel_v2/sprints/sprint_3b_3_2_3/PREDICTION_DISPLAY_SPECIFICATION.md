# PREDICTION DISPLAY SPECIFICATION
## Frontend UI & API Schema Implementation Standards for Machine Learning Outputs

**Sprint ID:** 3B.3.2.3  
**Audited Artifacts:**
- Prediction Standard: `JOBINTEL-STD-PRED-001`
- UI Component Inventory: `frontend/src/components/`
- API Routers: `src/backend/routers/`

---

## 1. Core Principles & Prohibited UI Patterns

The user experience of JOBINTEL must foster realistic trust. Users should make informed career and compensation decisions based on transparent, bounded estimates.

### 1.1 Strictly Prohibited UI Patterns
1. **Solitary Point Estimates:** Never display a single dollar or rupee figure (e.g., `₹12,50,000` or `$150,000`) without an accompanying uncertainty band.
2. **Deterministic Certainty Language:** Words such as *"Guaranteed"*, *"Definitive"*, *"Exact"*, or *"Proven"* are prohibited when describing model predictions.
3. **Uncalibrated Probability Percentages:** Never display a heuristic similarity score as a percentage probability (e.g., displaying `0.92` as *"92% Chance of Match"*).
4. **Synthetic Fallback Concealment:** Never display synthetic mock data or estimated values when primary statutory data is withheld; missing data must be explicitly represented as `null` or tagged with an informational `"Withheld"` banner.

---

## 2. Component-by-Component Display Specifications

### 2.1 Salary Intelligence Prediction Widget (`SalaryCard.tsx`)

#### Layout & Visual Hierarchy:
- **Primary Display (Large Font):** Estimated Range (e.g., `₹10.5 LPA – ₹14.5 LPA` or `$135,000 – $165,000`).
- **Secondary Display (Subtle Text):** Benchmark Midpoint (e.g., `Midpoint estimate: ₹12.5 LPA`).
- **Footer Disclosure (Mandatory Text):**
  > **India:** *"Estimated annual base compensation range based on verified Indian tech postings. Actual compensation varies by employer tier, candidate skill depth, and variable performance incentives."*  
  > **USA:** *"Estimated annual base salary range. Total compensation (including equity grants, bonuses, and benefits) frequently exceeds base pay at mid-to-senior levels."*

#### Data Contract Schema (`GET /api/v1/salary/predict`):
```json
{
  "currency": "INR",
  "prediction_interval": {
    "lower": 1050000,
    "point_estimate": 1250000,
    "upper": 1450000,
    "interval_type": "empirical_iqr_band",
    "unit": "INR"
  },
  "model_metadata": {
    "model_id": "MOD_IN_SALARY_HGBR",
    "version": "1.0.0",
    "r_squared": 0.58,
    "holdout_mae_lpa": 3.71,
    "sample_size": 1173
  },
  "disclosure_text": "Estimated compensation range based on verified Indian tech postings."
}
```

---

### 2.2 Occupation & Title Mapping Widget (`OccupationMapper.tsx`)

#### Layout & Visual Hierarchy:
- **Mapped Title Display:** Render canonical occupation title with a green `"Standardized SOC"` badge.
- **Score Representation:** Render match strength as a 5-bar rating or numeric index (e.g., `Match Index: 88/100`), **never** as a probability percentage.
- **Fallback State:** If match score falls below threshold ($\tau < 0.60$), render:
  - Badge: Orange `"Custom / Unmapped Title"`
  - Description: *"Title does not match standardized taxonomy. Displaying broader engineering benchmark."*

---

### 2.3 Skill Extraction & Demand Frequency Widget (`SkillDemandCard.tsx`)

#### Layout & Visual Hierarchy:
- **Frequency Bar:** Render percentage of postings requesting the skill (e.g., `Python: 68%`).
- **Mandatory Sample Size Badge:** The widget header or footer must declare the underlying volume of analyzed job vacancies:
  > *"Based on N = 1,420 verified active postings in the last 60 days."*
- **Scope Disclaimer:**
  > *"Reflects technical skills specified in employer job postings; does not measure internal employee competency."*

---

### 2.4 Employer Intelligence & Demand Overview (`EmployerCard.tsx`)

#### Layout & Visual Hierarchy:
- **Workforce Headcount:** Display statutory headcount with statutory authority attribution:
  > *"5,420 employees (Statutory filing with Ministry of Corporate Affairs / SEC Form 10-K, FY2024)."*
- **Advertised Vacancy Flow:** Explicitly distinguish active job listings from confirmed hires:
  > *"142 open requisitions observed over the last 30 days. Open listings indicate recruitment activity, not net headcount growth."*
- **UK Jurisdiction Banner:** If UK demand intelligence is selected:
  - Render empty state / neutral placeholder.
  - Text: *"UK vacancy flow intelligence is currently withheld pending statutory licensing review."*

---

## 3. API Response Validation Contract

All backend microservices emitting machine learning or algorithmic outputs must include the standard disclosure payload:

```python
class ModelPredictionResponse(BaseModel):
    point_estimate: float
    interval_lower: float
    interval_upper: float
    confidence_level: float = 0.50  # Central IQR
    model_id: str
    governance_status: str = "CONDITIONAL_GO"
    disclosure_notice: str
    sample_size_evaluated: int
```

Any API endpoint failing to return the bounding interval or disclosure notice must be rejected by frontend integration tests.
