import React, { useEffect, useState } from 'react';
import {
  GitCompare,
  TrendingUp,
  Layers,
  Cpu,
  ShieldCheck,
  AlertCircle,
  BarChart3,
  Globe2,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { api } from '../services/api';
import { CrossMarketSummary } from '../types';
import { PageHero } from '../components/PageHero';

export const CrossMarketPage: React.FC = () => {
  const [data, setData] = useState<CrossMarketSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getCrossMarketSummary()
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '80px 20px', color: '#94A3B8' }}>
        <div className="ji-spinner" style={{ margin: '0 auto 16px' }} />
        <p>Loading Cross-Market Synthesis Data...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div style={{ padding: '40px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid #EF4444', borderRadius: '12px', color: '#FCA5A5' }}>
        <AlertCircle size={24} style={{ marginBottom: '8px' }} />
        <h3>Failed to load cross-market data</h3>
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
      {/* Page Hero */}
      <PageHero
        badge="TWO MARKETS · TWO MODELS · ONE PLATFORM"
        title="USA vs India"
        subtitle="Explore how the two markets differ in salary patterns, skills, and job-market structures. These are independently modeled market estimates using country-specific job-market data."
        accentColor="#38BDF8"
      />

      {/* Critical Methodological Governance Note */}
      <div
        style={{
          background: 'rgba(56, 189, 248, 0.08)',
          border: '1px solid rgba(56, 189, 248, 0.25)',
          borderRadius: '12px',
          padding: '18px 22px',
          display: 'flex',
          alignItems: 'flex-start',
          gap: '14px',
        }}
      >
        <ShieldCheck size={22} style={{ color: '#38BDF8', flexShrink: 0, marginTop: '2px' }} />
        <div style={{ fontSize: '0.85rem', color: '#BAE6FD', lineHeight: 1.55 }}>
          <strong style={{ color: '#FFFFFF' }}>Cross-Market Notice (Strict Zero FX Isolation): </strong>
          Because the underlying datasets and models are different, salary values should not be
          interpreted as a direct currency-converted comparison. USA compensation is modeled in USD ($),
          while Indian compensation is independently modeled in INR (₹ LPA).
        </div>
      </div>

      {/* Side-by-Side Macro Market Comparison Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '24px' }}>
        {/* USA Card */}
        <div
          style={{
            background: 'rgba(15, 23, 42, 0.75)',
            border: '1px solid rgba(59, 130, 246, 0.3)',
            borderRadius: '16px',
            padding: '26px',
            backdropFilter: 'blur(16px)',
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: '4px',
              background: 'linear-gradient(90deg, #2563EB, #60A5FA)',
            }}
          />
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '1.6rem' }}>🇺🇸</span>
              <div>
                <h3 style={{ margin: 0, fontSize: '1.25rem', color: '#FFFFFF', fontWeight: 800 }}>
                  United States
                </h3>
                <span style={{ fontSize: '0.75rem', color: '#93C5FD', fontWeight: 600 }}>
                  Tech Job Market (USD $)
                </span>
              </div>
            </div>
            <span
              style={{
                fontSize: '0.72rem',
                fontWeight: 700,
                padding: '3px 9px',
                borderRadius: '8px',
                background: 'rgba(59, 130, 246, 0.18)',
                color: '#60A5FA',
                border: '1px solid rgba(59, 130, 246, 0.35)',
              }}
            >
              N = {data.usa_overview.cohort_size.toLocaleString()}
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px' }}>
            <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '14px', borderRadius: '10px', border: '1px solid rgba(255, 255, 255, 0.06)' }}>
              <div style={{ fontSize: '0.72rem', color: '#94A3B8', textTransform: 'uppercase', marginBottom: '4px' }}>
                Median Base Salary
              </div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#38BDF8' }}>
                {data.usa_overview.median_salary_display}
              </div>
              <div style={{ fontSize: '0.7rem', color: '#64748B' }}>Mean: {data.usa_overview.mean_salary_display}</div>
            </div>

            <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '14px', borderRadius: '10px', border: '1px solid rgba(255, 255, 255, 0.06)' }}>
              <div style={{ fontSize: '0.72rem', color: '#94A3B8', textTransform: 'uppercase', marginBottom: '4px' }}>
                Salary Disclosure
              </div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#F1F5F9' }}>
                {data.usa_overview.disclosed_pct}%
              </div>
              <div style={{ fontSize: '0.7rem', color: '#64748B' }}>IQR Spread: {data.usa_overview.iqr_display}</div>
            </div>
          </div>

          <div style={{ fontSize: '0.8rem', color: '#94A3B8', borderTop: '1px solid rgba(255, 255, 255, 0.08)', paddingTop: '14px' }}>
            <div><strong>Model:</strong> {data.model_comparison.usa.model_name}</div>
            <div><strong>Predictors:</strong> {data.model_comparison.usa.feature_count} features (15 PCs, 82 Skills)</div>
            <div><strong>Holdout MAE:</strong> {data.model_comparison.usa.holdout_mae} · <strong>R²:</strong> {data.model_comparison.usa.r2_score}</div>
          </div>
        </div>

        {/* India Card */}
        <div
          style={{
            background: 'rgba(15, 23, 42, 0.75)',
            border: '1px solid rgba(249, 115, 22, 0.3)',
            borderRadius: '16px',
            padding: '26px',
            backdropFilter: 'blur(16px)',
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: '4px',
              background: 'linear-gradient(90deg, #EA580C, #FB923C)',
            }}
          />
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '1.6rem' }}>🇮🇳</span>
              <div>
                <h3 style={{ margin: 0, fontSize: '1.25rem', color: '#FFFFFF', fontWeight: 800 }}>
                  India
                </h3>
                <span style={{ fontSize: '0.75rem', color: '#FDBA74', fontWeight: 600 }}>
                  Tech Job Market (INR ₹ LPA)
                </span>
              </div>
            </div>
            <span
              style={{
                fontSize: '0.72rem',
                fontWeight: 700,
                padding: '3px 9px',
                borderRadius: '8px',
                background: 'rgba(249, 115, 22, 0.18)',
                color: '#FB923C',
                border: '1px solid rgba(249, 115, 22, 0.35)',
              }}
            >
              N = {data.india_overview.cohort_size.toLocaleString()}
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px' }}>
            <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '14px', borderRadius: '10px', border: '1px solid rgba(255, 255, 255, 0.06)' }}>
              <div style={{ fontSize: '0.72rem', color: '#94A3B8', textTransform: 'uppercase', marginBottom: '4px' }}>
                Median Midpoint Salary
              </div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#FB923C' }}>
                {data.india_overview.median_salary_display}
              </div>
              <div style={{ fontSize: '0.7rem', color: '#64748B' }}>Mean: {data.india_overview.mean_salary_display}</div>
            </div>

            <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '14px', borderRadius: '10px', border: '1px solid rgba(255, 255, 255, 0.06)' }}>
              <div style={{ fontSize: '0.72rem', color: '#94A3B8', textTransform: 'uppercase', marginBottom: '4px' }}>
                Salary Disclosure
              </div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#F1F5F9' }}>
                {data.india_overview.disclosed_pct}%
              </div>
              <div style={{ fontSize: '0.7rem', color: '#64748B' }}>IQR Spread: {data.india_overview.iqr_display}</div>
            </div>
          </div>

          <div style={{ fontSize: '0.8rem', color: '#94A3B8', borderTop: '1px solid rgba(255, 255, 255, 0.08)', paddingTop: '14px' }}>
            <div><strong>Model:</strong> {data.model_comparison.india.model_name}</div>
            <div><strong>Predictors:</strong> {data.model_comparison.india.feature_count} features (15 PCs, 284 Skills)</div>
            <div><strong>Holdout MAE:</strong> {data.model_comparison.india.holdout_mae} · <strong>R²:</strong> {data.model_comparison.india.r2_score}</div>
          </div>
        </div>
      </div>

      {/* Shared Skills Prevalence Comparison */}
      <div
        style={{
          background: 'rgba(15, 23, 42, 0.65)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          borderRadius: '16px',
          padding: '28px',
          backdropFilter: 'blur(16px)',
        }}
      >
        <div style={{ marginBottom: '20px' }}>
          <h3 style={{ margin: '0 0 6px 0', fontSize: '1.15rem', color: '#FFFFFF', fontWeight: 700 }}>
            Shared Technical Skill Prevalence (%)
          </h3>
          <p style={{ margin: 0, fontSize: '0.82rem', color: '#94A3B8' }}>
            Frequency of mention across tech job postings in the USA (N = 34,036) vs. India (N = 5,859).
          </p>
        </div>

        <div style={{ height: '360px', width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={data.shared_skills_prevalence}
              margin={{ top: 20, right: 30, left: 10, bottom: 20 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.06)" />
              <XAxis dataKey="skill" stroke="#64748B" tick={{ fill: '#94A3B8', fontSize: 12 }} />
              <YAxis stroke="#64748B" tick={{ fill: '#94A3B8', fontSize: 12 }} unit="%" />
              <Tooltip
                contentStyle={{
                  background: '#0F172A',
                  borderColor: 'rgba(255, 255, 255, 0.15)',
                  borderRadius: '8px',
                  color: '#F8FAFC',
                }}
                formatter={(val: any) => [`${val}%`]}
              />
              <Legend wrapperStyle={{ paddingTop: '10px' }} />
              <Bar dataKey="usa_pct" name="USA Tech Postings (%)" fill="#3B82F6" radius={[4, 4, 0, 0]} />
              <Bar dataKey="india_pct" name="India Tech Postings (%)" fill="#F97316" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Role Demand Distribution Comparison */}
      <div
        style={{
          background: 'rgba(15, 23, 42, 0.65)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          borderRadius: '16px',
          padding: '28px',
          backdropFilter: 'blur(16px)',
        }}
      >
        <div style={{ marginBottom: '20px' }}>
          <h3 style={{ margin: '0 0 6px 0', fontSize: '1.15rem', color: '#FFFFFF', fontWeight: 700 }}>
            Structural Role Demand Shares (%)
          </h3>
          <p style={{ margin: 0, fontSize: '0.82rem', color: '#94A3B8' }}>
            Comparison of normalized talent demand across major functional domains in both ecosystems.
          </p>
        </div>

        <div style={{ height: '320px', width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={data.role_demand_comparison}
              layout="vertical"
              margin={{ top: 10, right: 30, left: 100, bottom: 10 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.06)" />
              <XAxis type="number" stroke="#64748B" tick={{ fill: '#94A3B8', fontSize: 12 }} unit="%" />
              <YAxis
                type="category"
                dataKey="role"
                stroke="#64748B"
                tick={{ fill: '#94A3B8', fontSize: 12 }}
                width={160}
              />
              <Tooltip
                contentStyle={{
                  background: '#0F172A',
                  borderColor: 'rgba(255, 255, 255, 0.15)',
                  borderRadius: '8px',
                  color: '#F8FAFC',
                }}
                formatter={(val: any) => [`${val}%`]}
              />
              <Legend wrapperStyle={{ paddingTop: '10px' }} />
              <Bar dataKey="usa_share_pct" name="USA Share (%)" fill="#60A5FA" radius={[0, 4, 4, 0]} />
              <Bar dataKey="india_share_pct" name="India Share (%)" fill="#FB923C" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Synthesis Takeaways */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '20px',
        }}
      >
        <div
          style={{
            background: 'rgba(255, 255, 255, 0.02)',
            border: '1px solid rgba(255, 255, 255, 0.07)',
            borderRadius: '12px',
            padding: '20px',
          }}
        >
          <h4 style={{ color: '#38BDF8', margin: '0 0 8px 0', fontSize: '0.95rem' }}>
            1. Salary Transparency Divergence
          </h4>
          <p style={{ margin: 0, fontSize: '0.82rem', color: '#94A3B8', lineHeight: 1.5 }}>
            Indian tech postings disclose compensation at <strong>34.78%</strong>, over 3.4× the US rate (<strong>10.13%</strong>).
            This reflects strong competitive recruitment pressures in Indian IT hubs for transparent bands.
          </p>
        </div>

        <div
          style={{
            background: 'rgba(255, 255, 255, 0.02)',
            border: '1px solid rgba(255, 255, 255, 0.07)',
            borderRadius: '12px',
            padding: '20px',
          }}
        >
          <h4 style={{ color: '#F59E0B', margin: '0 0 8px 0', fontSize: '0.95rem' }}>
            2. Skill Granularity & Density
          </h4>
          <p style={{ margin: 0, fontSize: '0.82rem', color: '#94A3B8', lineHeight: 1.5 }}>
            While USA tech postings reflect high multi-skill co-occurrence (SQL, Python, AWS), Indian postings feature
            specialized enterprise technology clusters (SAP, Spark/Big Data, Spring Boot) with distinct wage tiers.
          </p>
        </div>

        <div
          style={{
            background: 'rgba(255, 255, 255, 0.02)',
            border: '1px solid rgba(255, 255, 255, 0.07)',
            borderRadius: '12px',
            padding: '20px',
          }}
        >
          <h4 style={{ color: '#10B981', margin: '0 0 8px 0', fontSize: '0.95rem' }}>
            3. Model Performance Parity
          </h4>
          <p style={{ margin: 0, fontSize: '0.82rem', color: '#94A3B8', lineHeight: 1.5 }}>
            Both models achieved robust explanatory power (USA XGBoost R² = <strong>0.4233</strong>, MAE = <strong>$36,381</strong>; India HistGradientBoosting R² = <strong>0.580</strong>, MAE = <strong>₹3.71 LPA</strong>),
            proving reproducible predictability across diverse labor market structures.
          </p>
        </div>
      </div>
    </div>
  );
};
