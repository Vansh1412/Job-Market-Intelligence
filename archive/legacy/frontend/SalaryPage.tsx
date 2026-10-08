import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { useMarket } from '../context/MarketContext';
import { PageHero } from '../components/PageHero';
import { KPICard } from '../components/KPICard';
import { ScientificDisclaimer } from '../components/ScientificDisclaimer';
import { SourceFooter } from '../components/SourceFooter';
import {
  DollarSign,
  MapPin,
  Briefcase,
  Award,
  TrendingUp,
  BarChart3,
  Building2,
  Clock,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

export const SalaryPage: React.FC = () => {
  const { market, isUSA, isIndia, currencySymbol, formatSalary } = useMarket();

  const [marketSummary, setMarketSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'roles' | 'experience' | 'locations'>('roles');

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        if (isUSA) {
          const res = await api.getUsaMarketSummary();
          setMarketSummary(res);
        } else {
          const res = await api.getIndiaMarketSummary();
          setMarketSummary(res);
        }
      } catch (err) {
        console.error('Failed to load market summary data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [market]);

  if (loading || !marketSummary) {
    return (
      <div style={{ textAlign: 'center', padding: '80px 20px', color: '#94A3B8' }}>
        <div className="ji-spinner" style={{ margin: '0 auto 16px' }} />
        <p>Loading {market} Market Analytics...</p>
      </div>
    );
  }

  const moments = marketSummary.moments || {};
  const rolesData = marketSummary.by_role || [];
  const expData = isUSA ? (marketSummary.by_seniority || []) : (marketSummary.by_experience || []);
  const locationsData = marketSummary.by_location || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
      {/* Page Hero */}
      <PageHero
        badge={isUSA ? 'USA MARKET ANALYTICS · N = 34,036' : 'INDIA MARKET ANALYTICS · N = 5,859'}
        title={isUSA ? 'Salary Intelligence (USA)' : 'Salary Intelligence (India)'}
        subtitle={
          isUSA
            ? 'Empirical exploration of US technology compensation structures across role families, seniority tiers, and primary metropolitan tech hubs.'
            : 'Empirical exploration of Indian technology compensation structures across 14 normalized technical roles, experience tiers, and 23 metros.'
        }
        accentColor={isUSA ? '#06B6D4' : '#F97316'}
      />

      {/* KPI Cards */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '16px',
        }}
      >
        <KPICard
          label="Median Salary"
          value={
            isUSA
              ? `$${Math.round(moments.median || 0).toLocaleString()}`
              : `₹${(moments.median_lpa || 0).toFixed(1)} LPA`
          }
          sub={isUSA ? `Mean: $${Math.round(moments.mean || 0).toLocaleString()}` : `Mean: ₹${(moments.mean_lpa || 0).toFixed(2)} LPA`}
          accent={isUSA ? '#06B6D4' : '#F97316'}
          icon={<DollarSign size={20} />}
        />
        <KPICard
          label="Cohort Postings"
          value={marketSummary.cohort_size.toLocaleString()}
          sub={`From pool of ${marketSummary.total_job_pool.toLocaleString()}`}
          accent="#8B5CF6"
          icon={<Briefcase size={20} />}
        />
        <KPICard
          label="Salary Disclosure"
          value={`${marketSummary.disclosed_salary_pct}%`}
          sub={isUSA ? 'Excludes undisclosed postings' : 'Transparent compensation rate'}
          accent="#10B981"
          icon={<TrendingUp size={20} />}
        />
        <KPICard
          label="Interquartile Range"
          value={
            isUSA
              ? `$${Math.round(moments.iqr || 0).toLocaleString()}`
              : `₹${(moments.iqr_lpa || 0).toFixed(1)} LPA`
          }
          sub={isUSA ? 'Q1 to Q3 spread' : 'P25 to P75 range'}
          accent="#F59E0B"
          icon={<Award size={20} />}
        />
      </div>

      {/* View Switcher Tabs */}
      <div
        style={{
          display: 'flex',
          gap: '8px',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
          paddingBottom: '12px',
        }}
      >
        {[
          { key: 'roles', label: 'Compensation by Role', icon: Briefcase },
          { key: 'experience', label: isUSA ? 'By Seniority Tier' : 'By Experience Band', icon: Clock },
          { key: 'locations', label: 'By Metropolitan Hub', icon: MapPin },
        ].map((tab) => {
          const IconC = tab.icon;
          const isActive = activeTab === tab.key;
          const activeColor = isUSA ? '#06B6D4' : '#F97316';
          return (
            <button
              key={tab.key}
              type="button"
              onClick={() => setActiveTab(tab.key as any)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px 16px',
                borderRadius: '8px',
                border: isActive ? `1px solid ${activeColor}` : '1px solid transparent',
                background: isActive ? `${activeColor}20` : 'transparent',
                color: isActive ? '#FFFFFF' : '#94A3B8',
                fontWeight: isActive ? 700 : 500,
                fontSize: '0.86rem',
                cursor: 'pointer',
              }}
            >
              <IconC size={16} />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* TAB 1: ROLES */}
      {activeTab === 'roles' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* Chart */}
          <div
            style={{
              background: 'rgba(15, 23, 42, 0.65)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '16px',
              padding: '24px',
            }}
          >
            <h3 style={{ margin: '0 0 16px 0', fontSize: '1.1rem', color: '#FFFFFF', fontWeight: 700 }}>
              Median Compensation by Role ({isUSA ? '$ USD' : '₹ LPA'})
            </h3>
            <div style={{ height: '380px', width: '100%' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={rolesData}
                  layout="vertical"
                  margin={{ top: 10, right: 30, left: 120, bottom: 10 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.06)" />
                  <XAxis
                    type="number"
                    stroke="#64748B"
                    tick={{ fill: '#94A3B8', fontSize: 11 }}
                    unit={isUSA ? '$' : 'LPA'}
                  />
                  <YAxis
                    type="category"
                    dataKey="role"
                    stroke="#64748B"
                    tick={{ fill: '#94A3B8', fontSize: 11 }}
                    width={150}
                  />
                  <Tooltip
                    contentStyle={{
                      background: '#0F172A',
                      borderColor: 'rgba(255, 255, 255, 0.15)',
                      borderRadius: '8px',
                      color: '#F8FAFC',
                    }}
                    formatter={(val: any) => [
                      isUSA ? `$${Math.round(val).toLocaleString()}` : `₹${parseFloat(val).toFixed(2)} LPA`,
                      'Median Salary',
                    ]}
                  />
                  <Bar
                    dataKey={isUSA ? 'median_salary' : 'median_salary_lpa'}
                    fill={isUSA ? '#06B6D4' : '#F97316'}
                    radius={[0, 4, 4, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Table */}
          <div
            style={{
              background: 'rgba(15, 23, 42, 0.65)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '16px',
              padding: '20px',
              overflowX: 'auto',
            }}
          >
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.84rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.1)', color: '#94A3B8', textAlign: 'left' }}>
                  <th style={{ padding: '10px' }}>Role Category</th>
                  <th style={{ padding: '10px' }}>Sample Postings</th>
                  <th style={{ padding: '10px' }}>Median Salary</th>
                  <th style={{ padding: '10px' }}>Mean Salary</th>
                </tr>
              </thead>
              <tbody>
                {rolesData.map((r: any, idx: number) => (
                  <tr
                    key={idx}
                    style={{
                      borderBottom: '1px solid rgba(255, 255, 255, 0.04)',
                      color: '#E2E8F0',
                    }}
                  >
                    <td style={{ padding: '10px', fontWeight: 600 }}>{r.role}</td>
                    <td style={{ padding: '10px', color: '#94A3B8' }}>{r.postings.toLocaleString()}</td>
                    <td style={{ padding: '10px', fontWeight: 700, color: isUSA ? '#38BDF8' : '#FB923C' }}>
                      {isUSA
                        ? `$${Math.round(r.median_salary).toLocaleString()}`
                        : `₹${r.median_salary_lpa.toFixed(2)} LPA`}
                    </td>
                    <td style={{ padding: '10px', color: '#94A3B8' }}>
                      {isUSA
                        ? `$${Math.round(r.mean_salary).toLocaleString()}`
                        : `₹${r.mean_salary_lpa.toFixed(2)} LPA`}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 2: EXPERIENCE / SENIORITY */}
      {activeTab === 'experience' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div
            style={{
              background: 'rgba(15, 23, 42, 0.65)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '16px',
              padding: '24px',
            }}
          >
            <h3 style={{ margin: '0 0 16px 0', fontSize: '1.1rem', color: '#FFFFFF', fontWeight: 700 }}>
              Compensation Progression by {isUSA ? 'Seniority Tier' : 'Experience Band'}
            </h3>
            <div style={{ height: '340px', width: '100%' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={expData}
                  margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.06)" />
                  <XAxis
                    dataKey={isUSA ? 'seniority' : 'experience_band'}
                    stroke="#64748B"
                    tick={{ fill: '#94A3B8', fontSize: 12 }}
                  />
                  <YAxis
                    stroke="#64748B"
                    tick={{ fill: '#94A3B8', fontSize: 12 }}
                    unit={isUSA ? '$' : 'LPA'}
                  />
                  <Tooltip
                    contentStyle={{
                      background: '#0F172A',
                      borderColor: 'rgba(255, 255, 255, 0.15)',
                      borderRadius: '8px',
                      color: '#F8FAFC',
                    }}
                    formatter={(val: any) => [
                      isUSA ? `$${Math.round(val).toLocaleString()}` : `₹${parseFloat(val).toFixed(2)} LPA`,
                      'Median Salary',
                    ]}
                  />
                  <Bar
                    dataKey={isUSA ? 'median_salary' : 'median_salary_lpa'}
                    fill={isUSA ? '#8B5CF6' : '#FB923C'}
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: LOCATIONS */}
      {activeTab === 'locations' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div
            style={{
              background: 'rgba(15, 23, 42, 0.65)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '16px',
              padding: '24px',
            }}
          >
            <h3 style={{ margin: '0 0 16px 0', fontSize: '1.1rem', color: '#FFFFFF', fontWeight: 700 }}>
              Top Tech Metropolitan Hubs ({isUSA ? 'USA Metros' : 'Indian IT Metros'})
            </h3>
            <div style={{ height: '360px', width: '100%' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={locationsData}
                  layout="vertical"
                  margin={{ top: 10, right: 30, left: 100, bottom: 10 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.06)" />
                  <XAxis type="number" stroke="#64748B" tick={{ fill: '#94A3B8', fontSize: 11 }} />
                  <YAxis
                    type="category"
                    dataKey="city"
                    stroke="#64748B"
                    tick={{ fill: '#94A3B8', fontSize: 11 }}
                    width={110}
                  />
                  <Tooltip
                    contentStyle={{
                      background: '#0F172A',
                      borderColor: 'rgba(255, 255, 255, 0.15)',
                      borderRadius: '8px',
                      color: '#F8FAFC',
                    }}
                    formatter={(val: any) => [val.toLocaleString(), 'Postings Count']}
                  />
                  <Bar dataKey="postings" fill={isUSA ? '#10B981' : '#F97316'} radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      <ScientificDisclaimer />
      <SourceFooter />
    </div>
  );
};
