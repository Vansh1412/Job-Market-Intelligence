import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { ArchetypeError } from '../types';
import { PageHero } from '../components/PageHero';
import { ScientificDisclaimer } from '../components/ScientificDisclaimer';
import { SourceFooter } from '../components/SourceFooter';
import { ShieldAlert, AlertCircle, BarChart2, CheckCircle2 } from 'lucide-react';

export const ErrorAnalysisPage: React.FC = () => {
  const [errors, setErrors] = useState<ArchetypeError[]>([]);
  const [statTest, setStatTest] = useState<any>(null);
  const [hypotheses, setHypotheses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [eRes, sRes, hRes] = await Promise.all([
          api.getArchetypeErrors(),
          api.getStatisticalTest(),
          api.getHypotheses(),
        ]);
        setErrors(eRes);
        setStatTest(sRes);
        setHypotheses(hRes);
      } catch (err) {
        console.error('Failed to load error analysis data', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div style={{ padding: '60px 0', textAlign: 'center', color: '#94A3B8' }}>
        <div className="ji-pulse" style={{ fontSize: '1.2rem', fontWeight: 600 }}>
          Loading Archetype Error Analysis...
        </div>
      </div>
    );
  }

  const maxMAE = 50000;

  return (
    <div>
      <PageHero
        badgeText="EMPIRICAL VALIDATION · RESEARCH QUESTION 3"
        badgeColor="#F97316"
        title="Archetype Error Analysis"
        subtitle="Where does salary prediction become difficult? Statistical tests and error variance disaggregations across the seven discovered job archetypes."
      />

      {/* Main Error Visualization & Statistical Test Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1.35fr 1fr',
          gap: '20px',
          marginBottom: '32px',
        }}
      >
        {/* Horizontal Error Disaggregation Bar Chart */}
        <div
          className="ji-card-static"
          style={{
            padding: '24px 26px',
            background: 'rgba(16, 17, 22, 0.78)',
          }}
        >
          <div style={{ marginBottom: '18px' }}>
            <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#F97316', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '4px' }}>
              Holdout Error Hierarchy
            </div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#FFFFFF' }}>
              Holdout Test MAE Across 7 Archetypes
            </h3>
            <p style={{ fontSize: '0.78rem', color: '#94A3B8' }}>
              Error magnitude varies from $27,002 (AI_ML) to $46,098 (CLOUD_ARCH).
            </p>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {errors.map((item) => {
              const barWidth = (item.mae / maxMAE) * 100;
              const isLowest = item.code === 'AI_ML';
              const isHighest = item.code === 'CLOUD_ARCH';

              return (
                <div key={item.code}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '5px', fontSize: '0.82rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontWeight: 700, color: item.color, fontFamily: 'var(--font-mono)' }}>
                        {item.code}
                      </span>
                      <span style={{ color: '#E2E8F0' }}>{item.name}</span>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span style={{ fontSize: '0.72rem', color: '#64748B' }}>
                        ~{item.rel_error_pct.toFixed(1)}% rel
                      </span>
                      <span className="font-mono-numbers" style={{ fontWeight: 800, color: isLowest ? '#34D399' : isHighest ? '#F87171' : '#FFFFFF' }}>
                        ${item.mae.toLocaleString()}
                      </span>
                    </div>
                  </div>

                  <div style={{ height: '8px', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '4px', overflow: 'hidden' }}>
                    <div
                      style={{
                        height: '100%',
                        width: `${barWidth}%`,
                        background: `linear-gradient(90deg, ${item.color}88, ${item.color})`,
                        borderRadius: '4px',
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Statistical Test Evidence Card */}
        {statTest && (
          <div
            className="ji-card"
            style={{
              padding: '24px 26px',
              borderTop: '3px solid #10B981',
              background: 'rgba(16, 17, 22, 0.85)',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#34D399', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                  Statistical Hypothesis Test
                </span>
                <span
                  style={{
                    fontSize: '0.67rem',
                    fontWeight: 700,
                    padding: '2px 8px',
                    borderRadius: '10px',
                    background: 'rgba(16, 185, 129, 0.18)',
                    color: '#34D399',
                    border: '1px solid rgba(16, 185, 129, 0.3)',
                  }}
                >
                  STATISTICALLY SIGNIFICANT
                </span>
              </div>

              <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#FFFFFF', marginBottom: '14px' }}>
                {statTest.test_name}
              </h3>

              {/* Stats Dual Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px' }}>
                <div style={{ background: '#15171F', padding: '12px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.06)' }}>
                  <div style={{ fontSize: '0.7rem', color: '#94A3B8', marginBottom: '2px' }}>Kruskal-Wallis H</div>
                  <div className="font-mono-numbers" style={{ fontSize: '1.7rem', fontWeight: 900, color: '#FFFFFF' }}>
                    {statTest.statistic_h}
                  </div>
                  <div style={{ fontSize: '0.68rem', color: '#64748B' }}>df = {statTest.degrees_of_freedom}</div>
                </div>

                <div style={{ background: '#15171F', padding: '12px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.06)' }}>
                  <div style={{ fontSize: '0.7rem', color: '#94A3B8', marginBottom: '2px' }}>P-Value</div>
                  <div className="font-mono-numbers" style={{ fontSize: '1.25rem', fontWeight: 800, color: '#34D399', marginTop: '4px' }}>
                    {statTest.p_value_formatted}
                  </div>
                  <div style={{ fontSize: '0.68rem', color: '#34D399', fontWeight: 600 }}>p &lt; 0.001 (Null Rejected)</div>
                </div>
              </div>

              <div
                style={{
                  fontSize: '0.82rem',
                  color: '#CBD5E1',
                  lineHeight: 1.55,
                  padding: '12px',
                  background: 'rgba(255, 255, 255, 0.03)',
                  borderRadius: '8px',
                  border: '1px solid rgba(255, 255, 255, 0.06)',
                  marginBottom: '16px',
                }}
              >
                <strong>Empirical Verdict: </strong>
                {statTest.verdict}
              </div>
            </div>

            <div style={{ fontSize: '0.74rem', color: '#64748B', lineHeight: 1.45, paddingTop: '12px', borderTop: '1px solid rgba(255, 255, 255, 0.06)' }}>
              <strong>Boundary Notice: </strong>
              {statTest.inferential_boundary}
            </div>
          </div>
        )}
      </div>

      {/* Analytical Hypotheses Cards (Labeled Strictly as Observational Hypotheses) */}
      <div style={{ marginBottom: '28px' }}>
        <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '14px' }}>
          Plausible Analytical Hypotheses (Mechanisms for Observed Differentials)
        </h3>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
          {hypotheses.map((h) => (
            <div
              key={h.id}
              className="ji-card"
              style={{
                padding: '20px',
                borderLeft: `4px solid ${h.color}`,
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span style={{ fontSize: '0.72rem', fontWeight: 700, color: h.color, textTransform: 'uppercase' }}>
                  Hypothesis {h.id}: {h.archetype}
                </span>
                <span className="font-mono-numbers" style={{ fontSize: '0.75rem', fontWeight: 600, color: '#94A3B8' }}>
                  {h.stat}
                </span>
              </div>

              <h4 style={{ fontSize: '0.98rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '8px' }}>
                {h.title}
              </h4>

              <p style={{ fontSize: '0.78rem', color: '#94A3B8', lineHeight: 1.55 }}>
                {h.summary}
              </p>
            </div>
          ))}
        </div>
      </div>

      <ScientificDisclaimer customText="The Kruskal-Wallis test rejects the null hypothesis of equal error distributions across archetypes (p = 7.53×10⁻¹⁷). The mechanisms above represent observational hypotheses and must not be interpreted as deterministic causal claims." />
      <SourceFooter sourceFile="reports/tables/phase5/phase5_archetype_errors.csv" phaseTag="Phase 5 Error Disaggregation" />
    </div>
  );
};
