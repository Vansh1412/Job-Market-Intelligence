import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { FeatureSet, FeatureImportance } from '../types';
import { PageHero } from '../components/PageHero';
import { KPICard } from '../components/KPICard';
import { ScientificDisclaimer } from '../components/ScientificDisclaimer';
import { SourceFooter } from '../components/SourceFooter';
import { Award, BarChart3, Layers, CheckCircle2, TrendingUp, Cpu } from 'lucide-react';

export const ModelEvalPage: React.FC = () => {
  const [benchmarks, setBenchmarks] = useState<any>(null);
  const [featureSets, setFeatureSets] = useState<FeatureSet[]>([]);
  const [importances, setImportances] = useState<FeatureImportance[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [bRes, fRes, iRes] = await Promise.all([
          api.getModelBenchmarks(),
          api.getFeatureSets(),
          api.getFeatureImportance(),
        ]);
        setBenchmarks(bRes);
        setFeatureSets(fRes);
        setImportances(iRes);
      } catch (err) {
        console.error('Failed to load model eval data', err);
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
          Loading Model Performance Metrics...
        </div>
      </div>
    );
  }

  const best = benchmarks?.best_model;

  return (
    <div>
      <PageHero
        badgeText="PHASE 5 SUPERVISED BENCHMARKS · 5-FOLD CROSS VALIDATION"
        badgeColor="#8B5CF6"
        title="Model Performance & Evaluation"
        subtitle="Empirical evaluation of five regression architectures, baseline comparison tests, feature set ablation studies, and feature importance rankings."
      />

      {/* Winning Model Hero Observability Showcase */}
      {best && (
        <div
          className="ji-card"
          style={{
            padding: '26px 30px',
            marginBottom: '32px',
            borderTop: '3px solid #8B5CF6',
            background: 'rgba(16, 17, 22, 0.8)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '8px',
                  background: 'rgba(139, 92, 246, 0.2)',
                  border: '1px solid rgba(139, 92, 246, 0.4)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Award size={18} style={{ color: '#A78BFA' }} />
              </div>
              <div>
                <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#A78BFA', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                  Best Performing Regressor
                </span>
                <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#FFFFFF' }}>
                  {best.name}
                </h2>
              </div>
            </div>

            <div
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                padding: '4px 12px',
                borderRadius: '16px',
                background: 'rgba(16, 185, 129, 0.15)',
                border: '1px solid rgba(16, 185, 129, 0.3)',
                color: '#34D399',
                fontSize: '0.78rem',
                fontWeight: 700,
              }}
            >
              <span>{best.improvement_pct}% Error Reduction vs. Baseline</span>
            </div>
          </div>

          {/* Metrics Quad */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '14px' }}>
            <div style={{ background: '#15171F', padding: '14px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.06)' }}>
              <div style={{ fontSize: '0.7rem', color: '#94A3B8', marginBottom: '2px' }}>Holdout Test MAE</div>
              <div className="font-mono-numbers" style={{ fontSize: '1.6rem', fontWeight: 800, color: '#FFFFFF' }}>
                ${best.test_mae.toLocaleString()}
              </div>
              <div style={{ fontSize: '0.7rem', color: '#34D399', fontWeight: 600 }}>
                28.4% improvement
              </div>
            </div>

            <div style={{ background: '#15171F', padding: '14px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.06)' }}>
              <div style={{ fontSize: '0.7rem', color: '#94A3B8', marginBottom: '2px' }}>Holdout Test RMSE</div>
              <div className="font-mono-numbers" style={{ fontSize: '1.6rem', fontWeight: 800, color: '#38BDF8' }}>
                ${best.test_rmse.toLocaleString()}
              </div>
              <div style={{ fontSize: '0.7rem', color: '#34D399', fontWeight: 600 }}>
                24.5% improvement
              </div>
            </div>

            <div style={{ background: '#15171F', padding: '14px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.06)' }}>
              <div style={{ fontSize: '0.7rem', color: '#94A3B8', marginBottom: '2px' }}>Holdout Test R²</div>
              <div className="font-mono-numbers" style={{ fontSize: '1.6rem', fontWeight: 800, color: '#A78BFA' }}>
                {best.test_r2}
              </div>
              <div style={{ fontSize: '0.7rem', color: '#94A3B8' }}>
                42.33% variance explained
              </div>
            </div>

            <div style={{ background: '#15171F', padding: '14px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.06)' }}>
              <div style={{ fontSize: '0.7rem', color: '#94A3B8', marginBottom: '2px' }}>Unexplained Variance</div>
              <div className="font-mono-numbers" style={{ fontSize: '1.6rem', fontWeight: 800, color: '#F97316' }}>
                {best.unexplained_variance_pct}%
              </div>
              <div style={{ fontSize: '0.7rem', color: '#64748B' }}>
                Unobserved firm/interview factors
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Feature Set Architecture Comparison (A vs B vs C) */}
      <div style={{ marginBottom: '32px' }}>
        <div style={{ marginBottom: '14px' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '4px' }}>
            Feature Set Architecture Comparison
          </h2>
          <p style={{ fontSize: '0.85rem', color: '#94A3B8' }}>
            Empirical test: Does latent archetype assignment add predictive value beyond explicit skill indicators?
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
          {featureSets.map((fs) => (
            <div
              key={fs.id}
              className="ji-card"
              style={{
                padding: '22px',
                borderTop: `3px solid ${fs.color}`,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span style={{ fontSize: '0.72rem', fontWeight: 700, color: fs.color, letterSpacing: '0.06em', textTransform: 'uppercase' }}>
                    {fs.id}
                  </span>
                  {fs.is_best && (
                    <span style={{ fontSize: '0.67rem', fontWeight: 700, padding: '2px 8px', borderRadius: '10px', background: 'rgba(16, 185, 129, 0.18)', color: '#34D399', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
                      RECOMMENDED
                    </span>
                  )}
                </div>

                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '6px' }}>
                  {fs.name}
                </h3>

                <div className="font-mono-numbers" style={{ fontSize: '1.7rem', fontWeight: 800, color: '#FFFFFF', marginBottom: '4px' }}>
                  ${fs.mae.toLocaleString()} <span style={{ fontSize: '0.9rem', color: '#94A3B8', fontWeight: 500 }}>MAE</span>
                </div>

                <div style={{ fontSize: '0.8rem', color: '#38BDF8', fontFamily: 'var(--font-mono)', marginBottom: '12px' }}>
                  R² = {fs.r2} · {fs.features_count} Features
                </div>

                <p style={{ fontSize: '0.78rem', color: '#94A3B8', lineHeight: 1.5, marginBottom: '16px' }}>
                  {fs.composition}
                </p>
              </div>

              <div style={{ paddingTop: '12px', borderTop: '1px solid rgba(255, 255, 255, 0.06)', fontSize: '0.74rem', color: fs.color, fontWeight: 600 }}>
                Delta vs Explicit Baseline: {fs.delta_vs_a}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Candidate Algorithm Benchmark Table & Feature Importances */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1.2fr 1fr',
          gap: '18px',
          marginBottom: '24px',
        }}
      >
        {/* Benchmark Table */}
        <div className="ji-card-static" style={{ padding: '22px' }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '14px' }}>
            Holdout Test Candidate Model Benchmarks
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {(benchmarks?.test_results || []).map((m: any, idx: number) => {
              const isBest = idx === 0 || m.Model?.includes('XGBoost');
              return (
                <div
                  key={idx}
                  style={{
                    padding: '10px 14px',
                    borderRadius: '6px',
                    background: isBest ? 'rgba(139, 92, 246, 0.1)' : 'rgba(255, 255, 255, 0.02)',
                    border: `1px solid ${isBest ? 'rgba(139, 92, 246, 0.3)' : 'rgba(255, 255, 255, 0.05)'}`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <div>
                    <div style={{ fontSize: '0.84rem', fontWeight: isBest ? 700 : 500, color: isBest ? '#FFFFFF' : '#CBD5E1' }}>
                      {m.Model || m.Algorithm}
                    </div>
                    <div style={{ fontSize: '0.7rem', color: '#64748B' }}>
                      R²: {m.R2?.toFixed(4) || m.Test_R2?.toFixed(4)} · RMSE: ${m.RMSE?.toLocaleString() || m.Test_RMSE?.toLocaleString()}
                    </div>
                  </div>

                  <div className="font-mono-numbers" style={{ fontSize: '0.98rem', fontWeight: 700, color: isBest ? '#34D399' : '#FFFFFF' }}>
                    ${(m.MAE || m.Test_MAE)?.toLocaleString()}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Feature Importance Rankings */}
        <div className="ji-card-static" style={{ padding: '22px' }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '14px' }}>
            Top 12 Predictive Features (Split Gain)
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {importances.slice(0, 12).map((f) => {
              const maxImp = 0.22;
              const barWidth = Math.min(100, (f.Importance / maxImp) * 100);

              return (
                <div key={f.Feature} style={{ padding: '4px 0' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: '3px' }}>
                    <span style={{ color: '#E2E8F0', fontFamily: 'var(--font-mono)' }}>{f.Feature}</span>
                    <span style={{ color: '#8B5CF6', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
                      {(f.Importance * 100).toFixed(2)}%
                    </span>
                  </div>
                  <div style={{ height: '3px', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '2px' }}>
                    <div style={{ height: '100%', width: `${barWidth}%`, background: '#8B5CF6', borderRadius: '2px' }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <ScientificDisclaimer />
      <SourceFooter sourceFile="reports/tables/phase5/phase5_model_comparison.csv & phase5_test_results.csv" phaseTag="Phase 5 Model Benchmarks" />
    </div>
  );
};
