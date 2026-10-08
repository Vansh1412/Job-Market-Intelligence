import React, { useState } from 'react';
import { PageHero } from '../components/PageHero';
import { ScientificDisclaimer } from '../components/ScientificDisclaimer';
import { SourceFooter } from '../components/SourceFooter';
import {
  BookOpen,
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  Lock,
  GitBranch,
  Cpu,
  Database,
  Layers,
  Dna,
  BarChart3,
  ChevronDown,
  ChevronUp,
  ArrowDown,
  Info,
  Scale,
} from 'lucide-react';

export const MethodologyPage: React.FC = () => {
  // Expandable state for each of the 8 technical depth sections
  const [expandedSection, setExpandedSection] = useState<number | null>(null);

  const toggleSection = (idx: number) => {
    setExpandedSection((prev) => (prev === idx ? null : idx));
  };

  const PIPELINE_STEPS = [
    { num: '01', title: 'Job Postings', desc: 'Raw market corpus harvested across US & India', icon: Database, color: '#8B5CF6' },
    { num: '02', title: 'Clean & Standardize', desc: 'Deduplication, currency verification & validation', icon: ShieldCheck, color: '#38BDF8' },
    { num: '03', title: 'Extract Skills', desc: 'Curated keyword taxonomy & binary representation', icon: Layers, color: '#F59E0B' },
    { num: '04', title: 'Learn Salary Patterns', desc: 'Supervised regression modeling without data leakage', icon: Cpu, color: '#10B981' },
    { num: '05', title: 'Discover Skill Groups', desc: 'PCA + K-Means clustering for latent archetypes', icon: Dna, color: '#EC4899' },
    { num: '06', title: 'Estimate Salary', desc: 'Deterministic point predictions with error margins', icon: BarChart3, color: '#F97316' },
  ];

  const SECTIONS = [
    {
      id: 1,
      title: '1. Where the data comes from',
      tag: 'CORPUS & INGESTION',
      summary: 'Curated technology postings collected across United States and Indian tech hiring hubs.',
      details: (
        <div>
          <p>
            The JobIntel research corpus is comprised of two distinct, independent labor market datasets:
          </p>
          <ul style={{ paddingLeft: '20px', lineHeight: 1.6 }}>
            <li>
              <strong>United States Tech Market:</strong> 34,036 audited modeling rows filtered from 335,995
              raw tech job postings. Only postings with explicitly disclosed annualized compensation
              ($30k–$600k) were retained.
            </li>
            <li>
              <strong>Indian Tech Market:</strong> 5,859 audited modeling rows filtered from 14,037 raw
              postings. Only postings with valid annual INR compensation (0.5 LPA–100 LPA) were retained.
            </li>
          </ul>
          <p style={{ marginTop: '10px' }}>
            Data ingestion pipelines enforced strict content fingerprint deduplication to avoid artificial
            frequency inflation from duplicate syndicated job listings.
          </p>
        </div>
      ),
    },
    {
      id: 2,
      title: '2. How salary is prepared',
      tag: 'TARGET PREPARATION',
      summary: 'Annualized continuous midpoint salary targets with extreme outlier filtering.',
      details: (
        <div>
          <p>
            Raw job postings feature diverse compensation disclosures (hourly, monthly, annual ranges,
            stipends). The target variable was rigorously standardized:
          </p>
          <ul style={{ paddingLeft: '20px', lineHeight: 1.6 }}>
            <li>
              <strong>Continuous Midpoint Calculation:</strong> Postings disclosing ranges were standardized
              using the arithmetic midpoint between minimum and maximum bounds.
            </li>
            <li>
              <strong>USA Currency Standardization:</strong> Normalized to annualized USD. Bounds enforced:
              $30,000 to $600,000 per year.
            </li>
            <li>
              <strong>India Currency Standardization:</strong> Standardized in Lakhs Per Annum (LPA) and INR.
              Bounds enforced: ₹0.5 LPA (₹50,000) to ₹100.0 LPA (₹10,000,000). Target transformed via
              <code>log1p(salary_lpa)</code> during modeling to stabilize heteroskedastic right-skew variance.
            </li>
            <li>
              <strong>Zero Currency Conversion:</strong> Under no circumstances are USD converted to INR or
              vice-versa using foreign exchange rates, preventing Purchasing Power Parity (PPP) distortion.
            </li>
          </ul>
        </div>
      ),
    },
    {
      id: 3,
      title: '3. How skills are represented',
      tag: 'FEATURE ENGINEERING',
      summary: 'Curated taxonomy binary indicator matrices capturing competency presence.',
      details: (
        <div>
          <p>
            Technical skills were extracted using curated regular expression dictionary matching against raw
            job descriptions:
          </p>
          <ul style={{ paddingLeft: '20px', lineHeight: 1.6 }}>
            <li>
              <strong>USA Skill Matrix:</strong> 82 curated technology skills represented as binary
              indicators (1 = present, 0 = absent). Top skills: Python (47.2%), AWS (38.1%), SQL (36.4%).
            </li>
            <li>
              <strong>India Skill Matrix:</strong> 284 curated technical skills represented as a binary
              indicator matrix. Overall matrix sparsity is 98.58%, reflecting diverse niche technical
              vocabularies in Indian hiring.
            </li>
            <li>
              <strong>Zero Target Leakage:</strong> Skill vocabulary curation was executed prior to model
              training with zero salary reference.
            </li>
          </ul>
        </div>
      ),
    },
    {
      id: 4,
      title: '4. How salary prediction works',
      tag: 'SUPERVISED REGRESSION',
      summary: 'Country-specific gradient boosted decision tree ensembles evaluated on held-out test splits.',
      details: (
        <div>
          <p>
            Both countries utilize separate machine learning regression models fitted strictly on training
            partitions:
          </p>
          <ul style={{ paddingLeft: '20px', lineHeight: 1.6 }}>
            <li>
              <strong>USA Model:</strong> XGBoost Regressor trained on 123 explicit predictors (role family,
              seniority, clean city, remote status, and 82 binary skills). Hyperparameters: 100 estimators,
              max depth 6, learning rate 0.10.
            </li>
            <li>
              <strong>India Model:</strong> HistGradientBoostingRegressor trained on 290 predictors (normalized
              role, experience midpoint, experience range, grouped city, work mode, and 284 binary skills).
              Trained on <code>log1p(salary_lpa)</code> target and inverted via <code>expm1</code>.
            </li>
            <li>
              <strong>Deterministic Runtime:</strong> Models run in inference-only mode from frozen,
              cryptographically certified pickle artifacts. No live retraining or gradient updates occur at
              runtime.
            </li>
          </ul>
        </div>
      ),
    },
    {
      id: 5,
      title: '5. How archetypes are discovered',
      tag: 'UNSUPERVISED CLUSTERING',
      summary: 'Centered Covariance PCA dimensionality reduction and K-Means clustering.',
      details: (
        <div>
          <p>
            Job archetypes represent recurring skill clusters discovered through unsupervised statistical
            learning:
          </p>
          <ul style={{ paddingLeft: '20px', lineHeight: 1.6 }}>
            <li>
              <strong>Dimensionality Reduction:</strong> 15 continuous Principal Component Analysis (PCA)
              dimensions were extracted from the skill matrices to capture latent co-occurrence patterns.
            </li>
            <li>
              <strong>Clustering Algorithm:</strong> K-Means clustering with 10 random initializations.
            </li>
            <li>
              <strong>USA Clusters (K=7):</strong> Mean Adjusted Rand Index (ARI) = 0.7901 across resamples.
            </li>
            <li>
              <strong>India Clusters (K=6):</strong> Mean ARI = 0.8035 across resamples.
            </li>
            <li>
              <strong>Naming Principle:</strong> Archetypes represent skill-based market patterns (e.g.,
              "Python, Cloud Data & Applied AI/ML"), NOT formal occupational categories.
            </li>
          </ul>
        </div>
      ),
    },
    {
      id: 6,
      title: '6. How models are evaluated',
      tag: 'HOLDOUT BENCHMARKS',
      summary: 'Authoritative evaluation on held-out test partitions using MAE, RMSE, R², and Median AE.',
      details: (
        <div>
          <p>
            Models are evaluated using standard regression metrics on untouched test sets:
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginTop: '12px' }}>
            <div style={{ background: 'rgba(56, 189, 248, 0.08)', padding: '14px', borderRadius: '10px', border: '1px solid rgba(56, 189, 248, 0.25)' }}>
              <h4 style={{ color: '#38BDF8', margin: '0 0 6px 0', fontSize: '0.9rem' }}>USA Authoritative Holdout</h4>
              <div style={{ fontSize: '0.8rem', color: '#CBD5E1', lineHeight: 1.6 }}>
                • MAE: <strong>$36,380.64</strong><br />
                • RMSE: <strong>$51,082.06</strong><br />
                • R²: <strong>0.4233</strong><br />
                • MAPE: <strong>21.71%</strong><br />
                • Median Absolute Error: <strong>$26,384.22</strong>
              </div>
            </div>

            <div style={{ background: 'rgba(249, 115, 22, 0.08)', padding: '14px', borderRadius: '10px', border: '1px solid rgba(249, 115, 22, 0.25)' }}>
              <h4 style={{ color: '#F97316', margin: '0 0 6px 0', fontSize: '0.9rem' }}>India Authoritative Holdout</h4>
              <div style={{ fontSize: '0.8rem', color: '#CBD5E1', lineHeight: 1.6 }}>
                • MAE: <strong>₹3.71 LPA</strong><br />
                • RMSE: <strong>₹6.22 LPA</strong><br />
                • R²: <strong>0.5798</strong><br />
                • MAPE: <strong>35.22%</strong><br />
                • Median Absolute Error: <strong>₹2.08 LPA</strong>
              </div>
            </div>
          </div>
          <p style={{ marginTop: '12px', fontSize: '0.78rem', color: '#94A3B8' }}>
            Note: R² denotes coefficient of determination, reflecting the proportion of variance explained
            by the model. It is never conflated with classification accuracy.
          </p>
        </div>
      ),
    },
    {
      id: 7,
      title: '7. Limitations & Scientific Boundaries',
      tag: 'TRANSPARENT BOUNDARIES',
      summary: 'Observational data caveats, salary disclosure bias, and senior compensation error scaling.',
      details: (
        <div>
          <p>
            To maintain strict scientific integrity, the JobIntel platform documents its empirical
            boundaries transparently:
          </p>
          <ul style={{ paddingLeft: '20px', lineHeight: 1.6 }}>
            <li>
              <strong>Observational Association, Not Causality:</strong> All reported skill differences are
              observational associations in the analyzed postings. Learning a skill does not guarantee or
              cause a salary increase.
            </li>
            <li>
              <strong>Salary Disclosure Bias:</strong> In the US corpus, only ~10.13% of postings contained
              disclosed salaries (primarily driven by state pay transparency legislation in CA, NY, WA, CO).
            </li>
            <li>
              <strong>India High-Salary Error Scaling:</strong> Predictions become less reliable at senior
              compensation tiers. For postings ≥ ₹20 LPA, holdout MAE was ~₹8.06 LPA. For ≥ ₹40 LPA, holdout
              MAE was ~₹31.12 LPA due to upper-tail sample sparsity (N=335 in cohort).
            </li>
            <li>
              <strong>Archetype Sample Limitations:</strong> Specialized archetypes (e.g., India Big Data
              N=198, SAP N=125) have wider error margins due to lower sample density.
            </li>
            <li>
              <strong>No Future Guarantee:</strong> Historical market data does not guarantee future hiring
              offers or compensation packages.
            </li>
          </ul>
        </div>
      ),
    },
    {
      id: 8,
      title: '8. Reproducibility & Governance',
      tag: 'ENGINEERING AUDIT',
      summary: 'Frozen cryptographic artifacts, ModelRegistry singleton, and zero live fitting.',
      details: (
        <div>
          <p>
            The entire backend is governed by strict reproducibility standards:
          </p>
          <ul style={{ paddingLeft: '20px', lineHeight: 1.6 }}>
            <li>
              <strong>Cryptographic Hashes:</strong> All 10 frozen research model artifacts and datasets are
              verified at application startup via strict SHA-256 signatures before being loaded into memory.
            </li>
            <li>
              <strong>Zero Retraining Guarantee:</strong> The production backend codebase contains 0 calls to
              <code>.fit()</code> or <code>.fit_transform()</code>. All inference is strictly read-only.
            </li>
            <li>
              <strong>Single Source of Truth:</strong> Metric Lineage Register enforces consistent reporting
              across frontend, backend metadata, and research documentation.
            </li>
          </ul>
        </div>
      ),
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '36px' }}>
      {/* Page Header */}
      <div>
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '4px 12px',
            borderRadius: '9999px',
            background: 'rgba(99, 102, 241, 0.12)',
            border: '1px solid rgba(99, 102, 241, 0.3)',
            marginBottom: '12px',
          }}
        >
          <BookOpen size={14} style={{ color: '#818CF8' }} />
          <span
            style={{
              fontSize: '0.75rem',
              fontWeight: 700,
              letterSpacing: '0.08em',
              color: '#C7D2FE',
              textTransform: 'uppercase',
            }}
          >
            SCIENTIFIC METHODOLOGY & GOVERNANCE
          </span>
        </div>
        <h1
          style={{
            fontSize: 'clamp(2rem, 3.5vw, 2.6rem)',
            fontWeight: 800,
            color: '#FFFFFF',
            letterSpacing: '-0.02em',
            margin: '0 0 8px 0',
          }}
        >
          How JobIntel works
        </h1>
        <p style={{ fontSize: '1rem', color: '#94A3B8', maxWidth: '720px', margin: 0, lineHeight: 1.5 }}>
          Explore the machine learning pipeline, statistical evaluation, and data engineering principles
          that power JobIntel. Designed for transparency for both ordinary users and technical evaluators.
        </p>
      </div>

      {/* ============================================================ */}
      {/* NON-TECHNICAL PIPELINE DIAGRAM                                */}
      {/* ============================================================ */}
      <div
        style={{
          background: 'rgba(21, 23, 31, 0.75)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          borderRadius: '20px',
          padding: '32px 28px',
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#FFFFFF', margin: '0 0 4px 0' }}>
            The JobIntel Data & Machine Learning Pipeline
          </h2>
          <p style={{ fontSize: '0.85rem', color: '#94A3B8', margin: 0 }}>
            How real labor market postings flow into certified salary predictions
          </p>
        </div>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
            gap: '12px',
            position: 'relative',
          }}
        >
          {PIPELINE_STEPS.map((st, i) => {
            const IconComp = st.icon;
            return (
              <div
                key={st.num}
                style={{
                  background: 'rgba(255, 255, 255, 0.02)',
                  border: `1px solid ${st.color}35`,
                  borderRadius: '14px',
                  padding: '18px 14px',
                  textAlign: 'center',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                }}
              >
                <div
                  style={{
                    width: '38px',
                    height: '38px',
                    borderRadius: '10px',
                    background: `${st.color}18`,
                    border: `1px solid ${st.color}40`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: st.color,
                    marginBottom: '10px',
                  }}
                >
                  <IconComp size={18} />
                </div>
                <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
                  STEP {st.num}
                </div>
                <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: '#FFFFFF', margin: '4px 0 6px 0' }}>
                  {st.title}
                </h4>
                <p style={{ fontSize: '0.72rem', color: '#94A3B8', lineHeight: 1.45, margin: 0 }}>
                  {st.desc}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* ============================================================ */}
      {/* 8 DETAILED TECHNICAL EXPANDABLE SECTIONS                      */}
      {/* ============================================================ */}
      <div>
        <div style={{ marginBottom: '18px' }}>
          <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#FFFFFF', margin: '0 0 4px 0' }}>
            Technical Depth & Methodology (Evaluator View)
          </h2>
          <p style={{ fontSize: '0.88rem', color: '#94A3B8', margin: 0 }}>
            Expand any section to inspect data schemas, evaluation benchmarks, and scientific constraints.
          </p>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {SECTIONS.map((sec) => {
            const isExpanded = expandedSection === sec.id;

            return (
              <div
                key={sec.id}
                style={{
                  background: 'rgba(21, 23, 31, 0.75)',
                  border: isExpanded ? '1px solid rgba(99, 102, 241, 0.5)' : '1px solid rgba(255, 255, 255, 0.08)',
                  borderRadius: '16px',
                  overflow: 'hidden',
                  transition: 'border-color 0.2s ease',
                }}
              >
                <button
                  type="button"
                  onClick={() => toggleSection(sec.id)}
                  style={{
                    width: '100%',
                    padding: '20px 24px',
                    background: 'none',
                    border: 'none',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    cursor: 'pointer',
                    textAlign: 'left',
                  }}
                >
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#818CF8', letterSpacing: '0.06em' }}>
                        {sec.tag}
                      </span>
                    </div>
                    <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#FFFFFF', margin: 0 }}>
                      {sec.title}
                    </h3>
                    <p style={{ fontSize: '0.82rem', color: '#94A3B8', margin: 0 }}>
                      {sec.summary}
                    </p>
                  </div>

                  <div
                    style={{
                      width: '32px',
                      height: '32px',
                      borderRadius: '8px',
                      background: 'rgba(255, 255, 255, 0.04)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: '#CBD5E1',
                      flexShrink: 0,
                    }}
                  >
                    {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                  </div>
                </button>

                {isExpanded && (
                  <div
                    style={{
                      padding: '20px 24px 24px 24px',
                      borderTop: '1px solid rgba(255, 255, 255, 0.08)',
                      background: 'rgba(0, 0, 0, 0.25)',
                      fontSize: '0.85rem',
                      color: '#CBD5E1',
                      lineHeight: 1.6,
                    }}
                  >
                    {sec.details}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      <ScientificDisclaimer />
      <SourceFooter />
    </div>
  );
};
