import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { KPIData, FunnelStage, DataFlowItem, ResearchQuestion } from '../types';
import { PageHero } from '../components/PageHero';
import { KPICard } from '../components/KPICard';
import { ResearchQuestionCard } from '../components/ResearchQuestionCard';
import { DataFlowVisual } from '../components/DataFlowVisual';
import { ScientificDisclaimer } from '../components/ScientificDisclaimer';
import { SourceFooter } from '../components/SourceFooter';
import { CheckCircle2, TrendingUp, Sparkles } from 'lucide-react';

export const OverviewPage: React.FC = () => {
  const [kpis, setKpis] = useState<Record<string, KPIData> | null>(null);
  const [dataFlow, setDataFlow] = useState<DataFlowItem[]>([]);
  const [rqs, setRqs] = useState<ResearchQuestion[]>([]);
  const [funnel, setFunnel] = useState<FunnelStage[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [kpiRes, flowRes, rqRes, funnelRes] = await Promise.all([
          api.getOverviewKPIs(),
          api.getDataFlow(),
          api.getResearchQuestions(),
          api.getFunnel(),
        ]);
        setKpis(kpiRes);
        setDataFlow(flowRes);
        setRqs(rqRes);
        setFunnel(funnelRes);
      } catch (err) {
        console.error('Failed to load overview data', err);
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
          Loading Research Overview...
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Editorial Hero Header */}
      <PageHero
        badgeText="INT234 PREDICTIVE ANALYTICS · FROZEN SSOT"
        badgeColor="#8B5CF6"
        title="Job Market Intelligence"
        subtitle="An empirical research platform for discovering skill-based job archetypes, analyzing labor market salary structures, and evaluating supervised machine learning performance across the technology sector."
      />

      {/* Visual Data Flow Pipeline */}
      {dataFlow.length > 0 && <DataFlowVisual items={dataFlow} />}

      {/* Section 1: Research Scale & Model Benchmarks */}
      <div style={{ marginBottom: '32px' }}>
        <div style={{ marginBottom: '14px' }}>
          <h2
            style={{
              fontSize: '1.3rem',
              fontWeight: 700,
              color: '#FFFFFF',
              letterSpacing: '-0.02em',
              marginBottom: '4px',
            }}
          >
            Research Scale & Model Benchmarks
          </h2>
          <p style={{ fontSize: '0.85rem', color: '#94A3B8' }}>
            Audited corpus statistics and holdout evaluation metrics from Phase 1 through Phase 5.
          </p>
        </div>

        {kpis && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {/* Top Row: Corpus Scale */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(4, 1fr)',
                gap: '14px',
              }}
            >
              <KPICard
                label={kpis.raw_harvested.label}
                value={kpis.raw_harvested.value}
                sub={kpis.raw_harvested.sub}
                accentColor="#8B5CF6"
              />
              <KPICard
                label={kpis.skill_bearing.label}
                value={kpis.skill_bearing.value}
                sub={kpis.skill_bearing.sub}
                accentColor="#06B6D4"
              />
              <KPICard
                label={kpis.salary_cohort.label}
                value={kpis.salary_cohort.value}
                sub={kpis.salary_cohort.sub}
                accentColor="#10B981"
              />
              <KPICard
                label={kpis.holdout_mae.label}
                value={kpis.holdout_mae.value}
                sub="XGBoost Holdout Error"
                delta={kpis.holdout_mae.delta}
                deltaPositive={true}
                accentColor="#EC4899"
              />
            </div>

            {/* Bottom Row: Model & Archetypes */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(4, 1fr)',
                gap: '14px',
              }}
            >
              <KPICard
                label={kpis.holdout_r2.label}
                value={kpis.holdout_r2.value}
                sub={kpis.holdout_r2.sub}
                accentColor="#8B5CF6"
              />
              <KPICard
                label={kpis.holdout_rmse.label}
                value={kpis.holdout_rmse.value}
                sub="XGBoost Holdout RMSE"
                delta={kpis.holdout_rmse.delta}
                deltaPositive={true}
                accentColor="#06B6D4"
              />
              <KPICard
                label={kpis.archetypes_count.label}
                value={kpis.archetypes_count.value}
                sub={kpis.archetypes_count.sub}
                accentColor="#F59E0B"
              />
              <KPICard
                label={kpis.skills_count.label}
                value={kpis.skills_count.value}
                sub={kpis.skills_count.sub}
                accentColor="#14B8A6"
              />
            </div>
          </div>
        )}
      </div>

      {/* Section 2: The Three Research Questions */}
      <div style={{ marginBottom: '32px' }}>
        <div style={{ marginBottom: '14px' }}>
          <h2
            style={{
              fontSize: '1.3rem',
              fontWeight: 700,
              color: '#FFFFFF',
              letterSpacing: '-0.02em',
              marginBottom: '4px',
            }}
          >
            The Three Research Questions
          </h2>
          <p style={{ fontSize: '0.85rem', color: '#94A3B8' }}>
            Empirical objectives, statistical methodologies, and validated project outcomes.
          </p>
        </div>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '16px',
            alignItems: 'stretch',
          }}
        >
          {rqs.map((rq) => (
            <ResearchQuestionCard key={rq.id} rq={rq} />
          ))}
        </div>
      </div>

      {/* Section 3: Population Funnel & Research Milestones */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ marginBottom: '14px' }}>
          <h2
            style={{
              fontSize: '1.3rem',
              fontWeight: 700,
              color: '#FFFFFF',
              letterSpacing: '-0.02em',
              marginBottom: '4px',
            }}
          >
            Dataset Curation & Research Milestones
          </h2>
          <p style={{ fontSize: '0.85rem', color: '#94A3B8' }}>
            Step-by-step sample attrition and verified data integrity protocols.
          </p>
        </div>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1.2fr 1fr',
            gap: '16px',
          }}
        >
          {/* Funnel Progress Table */}
          <div className="ji-card-static" style={{ padding: '20px' }}>
            <div style={{ fontSize: '0.88rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '14px' }}>
              Population Attrition Stages
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {funnel.map((stg) => {
                const pct = (stg.Count / 394300) * 100;
                return (
                  <div key={stg.Stage}>
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        fontSize: '0.8rem',
                        marginBottom: '4px',
                      }}
                    >
                      <span style={{ color: '#E2E8F0', fontWeight: 500 }}>{stg.Stage}</span>
                      <span style={{ color: '#94A3B8', fontFamily: 'var(--font-mono)' }}>
                        {stg.Count.toLocaleString()} ({pct.toFixed(1)}%)
                      </span>
                    </div>

                    <div
                      style={{
                        height: '6px',
                        background: 'rgba(255, 255, 255, 0.06)',
                        borderRadius: '3px',
                        overflow: 'hidden',
                      }}
                    >
                      <div
                        style={{
                          height: '100%',
                          width: `${pct}%`,
                          background: 'linear-gradient(90deg, #8B5CF6 0%, #06B6D4 100%)',
                          borderRadius: '3px',
                        }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Research Milestones */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div
              className="ji-card"
              style={{
                padding: '16px 18px',
                borderLeft: '3px solid #8B5CF6',
              }}
            >
              <div style={{ fontSize: '0.84rem', fontWeight: 700, color: '#A78BFA', marginBottom: '4px' }}>
                Milestone 1: Exact Deduplication
              </div>
              <div style={{ fontSize: '0.78rem', color: '#94A3B8', lineHeight: 1.5 }}>
                Eliminated 58,305 redundant records (14.8%) through exact casing, whitespace, and title normalization, preserving full corpus provenance without distorting market density.
              </div>
            </div>

            <div
              className="ji-card"
              style={{
                padding: '16px 18px',
                borderLeft: '3px solid #06B6D4',
              }}
            >
              <div style={{ fontSize: '0.84rem', fontWeight: 700, color: '#38BDF8', marginBottom: '4px' }}>
                Milestone 2: Zero-Skill Quarantine
              </div>
              <div style={{ fontSize: '0.78rem', color: '#94A3B8', lineHeight: 1.5 }}>
                Phase 4.1 quarantined 219,165 zero-skill postings from primary archetype clustering, preventing centroid collapse and isolating 116,830 skill-bearing jobs.
              </div>
            </div>

            <div
              className="ji-card"
              style={{
                padding: '16px 18px',
                borderLeft: '3px solid #10B981',
              }}
            >
              <div style={{ fontSize: '0.84rem', fontWeight: 700, color: '#34D399', marginBottom: '4px' }}>
                Milestone 3: Ground-Truth Salary Filter
              </div>
              <div style={{ fontSize: '0.78rem', color: '#94A3B8', lineHeight: 1.5 }}>
                The supervised regression cohort comprises 34,036 technology postings with verified direct USD salary midpoints constrained to the defensible [$30,000, $600,000] interval.
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Disclaimers & Provenance */}
      <ScientificDisclaimer />
      <SourceFooter sourceFile="reports/frozen_results_registry.md" phaseTag="Phase 6 Synthesis" />
    </div>
  );
};
