import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  TrendingUp,
  AlertTriangle,
  Layers,
  MapPin,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Sparkles,
  Search,
  ExternalLink,
  ShieldAlert,
  Flame,
  ArrowRight,
  BookOpen,
  Scale,
  Target,
  BarChart2,
  Check,
  Plus,
} from 'lucide-react';
import { api } from '../services/api';
import {
  DemandMarketOverview,
  DemandMetricDefinition,
  DemandObservation,
  OccupationDemandProfile,
  DemandComparisonResult,
  SkillGapAnalysisResult,
  SkillDemandItem,
} from '../types';

type TabType = 'overview' | 'explorer' | 'comparison' | 'skills_gap';

const PROVENANCE_CONFIG: Record<string, { label: string; color: string; bg: string; border: string }> = {
  OFFICIAL_PUBLISHED: {
    label: 'Official statistic',
    color: '#10B981',
    bg: 'rgba(16, 185, 129, 0.12)',
    border: 'rgba(16, 185, 129, 0.3)',
  },
  OFFICIALLY_DERIVED: {
    label: 'Derived from official data',
    color: '#00F0FF',
    bg: 'rgba(0, 240, 255, 0.12)',
    border: 'rgba(0, 240, 255, 0.3)',
  },
  JOBINTEL_CURATED: {
    label: 'JobIntel research benchmark',
    color: '#F59E0B',
    bg: 'rgba(245, 158, 11, 0.12)',
    border: 'rgba(245, 158, 11, 0.3)',
  },
  JOBINTEL_MODEL_ESTIMATE: {
    label: 'Model-derived estimate',
    color: '#8B5CF6',
    bg: 'rgba(139, 92, 246, 0.12)',
    border: 'rgba(139, 92, 246, 0.3)',
  },
  SYNTHETIC_TEST_FIXTURE: {
    label: 'Test data',
    color: '#EC4899',
    bg: 'rgba(236, 72, 153, 0.12)',
    border: 'rgba(236, 72, 153, 0.3)',
  },
  UNVERIFIED: {
    label: 'Verification pending',
    color: '#94A3B8',
    bg: 'rgba(148, 163, 184, 0.12)',
    border: 'rgba(148, 163, 184, 0.3)',
  },
};

const MARKET_FLAGS: Record<string, string> = {
  US: '🇺🇸',
  AU: '🇦🇺',
  UK: '🇬🇧',
  SG: '🇸🇬',
  IN: '🇮🇳',
};

export const DemandPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [markets, setMarkets] = useState<DemandMarketOverview[]>([]);
  const [metrics, setMetrics] = useState<DemandMetricDefinition[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Tab 2 Explorer States
  const [selectedMarket, setSelectedMarket] = useState<string>('US');
  const [marketObservations, setMarketObservations] = useState<DemandObservation[]>([]);
  const [selectedOccId, setSelectedOccId] = useState<string>('');
  const [occupationProfile, setOccupationProfile] = useState<OccupationDemandProfile | null>(null);
  const [profileLoading, setProfileLoading] = useState(false);
  const [showProvenanceDetails, setShowProvenanceDetails] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Tab 3 Comparison States
  const [compCanonical, setCompCanonical] = useState('CAN_OCC_SOFTWARE_ENGINEER');
  const [compMarketA, setCompMarketA] = useState('US');
  const [compMarketB, setCompMarketB] = useState('AU');
  const [comparisonResult, setComparisonResult] = useState<DemandComparisonResult | null>(null);
  const [compLoading, setCompLoading] = useState(false);

  // Tab 4 Skill Gap States
  const [gapOccupationId, setGapOccupationId] = useState('15-1252');
  const [gapMarket, setGapMarket] = useState('US');
  const [userSkills, setUserSkills] = useState<string[]>([
    'Python',
    'SQL',
    'Git',
    'Docker',
    'REST APIs',
  ]);
  const [customSkillInput, setCustomSkillInput] = useState('');
  const [gapResult, setGapResult] = useState<SkillGapAnalysisResult | null>(null);
  const [gapLoading, setGapLoading] = useState(false);

  // Load Initial Catalog Data
  useEffect(() => {
    let isMounted = true;
    async function loadInitialData() {
      try {
        setLoading(true);
        setError(null);
        const [mkts, mtrs] = await Promise.all([
          api.getDemandMarkets(),
          api.getDemandMetrics(),
        ]);
        if (isMounted) {
          setMarkets(mkts);
          setMetrics(mtrs);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.message || 'Failed to load demand intelligence metadata.');
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadInitialData();
    return () => {
      isMounted = false;
    };
  }, []);

  // Load observations for selected market in Explorer
  useEffect(() => {
    let isMounted = true;
    async function loadMarketObs() {
      try {
        const obs = await api.getDemandOccupations(selectedMarket);
        if (isMounted) {
          setMarketObservations(obs);
          if (obs.length > 0) {
            setSelectedOccId(obs[0].occupation_id);
          } else {
            setSelectedOccId('');
            setOccupationProfile(null);
          }
        }
      } catch (err: any) {
        console.error('Error loading market observations:', err);
      }
    }
    loadMarketObs();
    return () => {
      isMounted = false;
    };
  }, [selectedMarket]);

  // Load specific occupation profile
  useEffect(() => {
    if (!selectedOccId) return;
    // Guard against cross-market mismatch during market state transitions
    const isMatchingMarket = marketObservations.some(
      (o) => o.occupation_id === selectedOccId && o.market_id === selectedMarket
    );
    if (!isMatchingMarket && marketObservations.length > 0) return;

    let isMounted = true;
    async function loadProfile() {
      try {
        setProfileLoading(true);
        const prof = await api.getOccupationDemandProfile(selectedOccId, selectedMarket);
        if (isMounted) {
          setOccupationProfile(prof);
        }
      } catch (err: any) {
        console.error('Error loading occupation profile:', err);
        if (isMounted) setOccupationProfile(null);
      } finally {
        if (isMounted) setProfileLoading(false);
      }
    }
    loadProfile();
    return () => {
      isMounted = false;
    };
  }, [selectedOccId, selectedMarket, marketObservations]);

  // Execute Cross-Market Comparison
  useEffect(() => {
    if (activeTab !== 'comparison') return;
    let isMounted = true;
    async function runComparison() {
      try {
        setCompLoading(true);
        const res = await api.compareDemand(compCanonical, compMarketA, compMarketB);
        if (isMounted) setComparisonResult(res);
      } catch (err: any) {
        console.error('Error running demand comparison:', err);
      } finally {
        if (isMounted) setCompLoading(false);
      }
    }
    runComparison();
    return () => {
      isMounted = false;
    };
  }, [compCanonical, compMarketA, compMarketB, activeTab]);

  // Execute Skill Gap Analysis
  useEffect(() => {
    if (activeTab !== 'skills_gap') return;
    let isMounted = true;
    async function runGapAnalysis() {
      try {
        setGapLoading(true);
        const res = await api.analyzeSkillGaps({
          target_occupation_id: gapOccupationId,
          market_id: gapMarket,
          user_skills: userSkills,
        });
        if (isMounted) setGapResult(res);
      } catch (err: any) {
        console.error('Error analyzing skill gaps:', err);
      } finally {
        if (isMounted) setGapLoading(false);
      }
    }
    runGapAnalysis();
    return () => {
      isMounted = false;
    };
  }, [gapOccupationId, gapMarket, userSkills, activeTab]);

  const toggleUserSkill = (skill: string) => {
    if (userSkills.includes(skill)) {
      setUserSkills(userSkills.filter((s) => s !== skill));
    } else {
      setUserSkills([...userSkills, skill]);
    }
  };

  const addCustomSkill = () => {
    if (!customSkillInput.trim()) return;
    const clean = customSkillInput.trim();
    if (!userSkills.includes(clean)) {
      setUserSkills([...userSkills, clean]);
    }
    setCustomSkillInput('');
  };

  return (
    <div style={{ color: '#E2E8F0', paddingBottom: '80px' }}>
      {/* Header Banner */}
      <div style={{ marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
          <span
            style={{
              padding: '4px 10px',
              borderRadius: '20px',
              fontSize: '12px',
              fontWeight: 600,
              background: 'rgba(0, 240, 255, 0.1)',
              color: '#00F0FF',
              border: '1px solid rgba(0, 240, 255, 0.3)',
            }}
          >
            SPRINT 3B.2 — PRODUCTION STAGING
          </span>
          <span style={{ fontSize: '12px', color: '#94A3B8' }}>
            Multi-Market Labour Demand Analytics & Skill Architecture
          </span>
        </div>
        <h1
          style={{
            fontSize: '32px',
            fontWeight: 800,
            letterSpacing: '-0.02em',
            margin: '0 0 12px 0',
            background: 'linear-gradient(135deg, #FFFFFF 0%, #94A3B8 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}
        >
          Global Job Demand Intelligence
        </h1>
        <p style={{ fontSize: '15px', color: '#94A3B8', maxWidth: '880px', lineHeight: 1.6, margin: 0 }}>
          Source-backed, descriptive occupational demand intelligence across 5 national markets.
          Enforces statistical non-collapsibility, transparent limitations, and rigorous 11-dimension
          comparability between online job postings, establishment vacancies, and projected openings.
        </p>
      </div>

      {/* Tab Navigation Pill Bar */}
      <div
        style={{
          display: 'flex',
          gap: '8px',
          background: 'rgba(15, 23, 42, 0.6)',
          backdropFilter: 'blur(16px)',
          padding: '6px',
          borderRadius: '12px',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          marginBottom: '28px',
          overflowX: 'auto',
        }}
      >
        {[
          { id: 'overview', label: '1. Market Overview & Governance', icon: Scale },
          { id: 'explorer', label: '2. Occupational Demand Explorer', icon: BarChart2 },
          { id: 'comparison', label: '3. 11-Dimension Comparability', icon: HelpCircle },
          { id: 'skills_gap', label: '4. Skill Demand & Gap Analyzer', icon: Target },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as TabType)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 18px',
                borderRadius: '8px',
                border: 'none',
                background: isActive ? 'rgba(0, 240, 255, 0.15)' : 'transparent',
                color: isActive ? '#00F0FF' : '#94A3B8',
                fontSize: '14px',
                fontWeight: isActive ? 600 : 500,
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                whiteSpace: 'nowrap',
                boxShadow: isActive ? '0 0 16px rgba(0, 240, 255, 0.2)' : 'none',
              }}
            >
              <Icon size={16} />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* TAB 1: OVERVIEW & GOVERNANCE */}
      {activeTab === 'overview' && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          {/* Methodological Non-Collapsibility Callout */}
          <div
            style={{
              background: 'linear-gradient(135deg, rgba(121, 40, 202, 0.12) 0%, rgba(0, 112, 243, 0.08) 100%)',
              border: '1px solid rgba(121, 40, 202, 0.3)',
              borderRadius: '12px',
              padding: '20px 24px',
              marginBottom: '32px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '14px' }}>
              <ShieldAlert size={24} style={{ color: '#C084FC', flexShrink: 0, marginTop: '2px' }} />
              <div>
                <h3 style={{ margin: '0 0 6px 0', fontSize: '16px', fontWeight: 700, color: '#E2E8F0' }}>
                  Core Methodology: Why Demand Data Cannot Be Collapsed
                </h3>
                <p style={{ margin: 0, fontSize: '14px', color: '#CBD5E1', lineHeight: 1.6 }}>
                  National statistical systems measure labour demand through fundamentally distinct instruments:
                  <strong> Online Job Adverts</strong> (Australia JSA, UK ONS) capture web recruitment churn;
                  <strong> Official Vacancies</strong> (Singapore MOM) measure active unfilled establishment positions;
                  and <strong> Annual Job Openings</strong> (US BLS) model structural 10-year replacements and net growth.
                  JOBINTEL refuses to combine these into an artificial composite score.
                </p>
              </div>
            </div>
          </div>

          {/* 5-Market Portfolio Cards */}
          <h2 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '16px', color: '#F8FAFC' }}>
            National Labour Demand Coverage Portfolio
          </h2>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
              gap: '16px',
              marginBottom: '36px',
            }}
          >
            {markets.map((m) => (
              <div
                key={m.market_id}
                style={{
                  background: 'rgba(15, 23, 42, 0.7)',
                  borderRadius: '12px',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  padding: '20px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '12px',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontSize: '24px' }}>{MARKET_FLAGS[m.market_id] || '🌐'}</span>
                    <span style={{ fontSize: '16px', fontWeight: 700, color: '#FFFFFF' }}>{m.market_name}</span>
                  </div>
                  <span
                    style={{
                      fontSize: '11px',
                      fontWeight: 700,
                      padding: '3px 8px',
                      borderRadius: '12px',
                      background: m.coverage_status === 'WITHHELD_PENDING_REVIEW'
                        ? 'rgba(239, 68, 68, 0.15)'
                        : 'rgba(16, 185, 129, 0.15)',
                      color: m.coverage_status === 'WITHHELD_PENDING_REVIEW' ? '#EF4444' : '#10B981',
                      border: m.coverage_status === 'WITHHELD_PENDING_REVIEW'
                        ? '1px solid rgba(239, 68, 68, 0.3)'
                        : '1px solid rgba(16, 185, 129, 0.3)',
                    }}
                  >
                    {m.coverage_status.replace(/_/g, ' ')}
                  </span>
                </div>

                <div>
                  <div style={{ fontSize: '12px', color: '#94A3B8', marginBottom: '2px' }}>
                    Primary Demand Instrument
                  </div>
                  <div style={{ fontSize: '13px', fontWeight: 600, color: '#00F0FF' }}>
                    {m.metric_label}
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '12px', color: '#94A3B8', marginBottom: '2px' }}>
                    Official Data Authority
                  </div>
                  <div style={{ fontSize: '12px', color: '#CBD5E1' }}>
                    {m.primary_source_name}
                  </div>
                </div>

                <div
                  style={{
                    marginTop: 'auto',
                    paddingTop: '12px',
                    borderTop: '1px solid rgba(255, 255, 255, 0.06)',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    fontSize: '11px',
                    color: '#64748B',
                  }}
                >
                  <span>{m.total_observations} Observations</span>
                  <span style={{ maxWidth: '120px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {m.license}
                  </span>
                </div>
              </div>
            ))}
          </div>

          {/* Metric Glossary & Underlying Constructs */}
          <h2 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '16px', color: '#F8FAFC' }}>
            Demand Metric Types & Statistical Constructs
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '16px' }}>
            {metrics.map((def) => (
              <div
                key={def.metric_type}
                style={{
                  background: 'rgba(15, 23, 42, 0.6)',
                  borderRadius: '12px',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  padding: '20px',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                  <h4 style={{ margin: 0, fontSize: '15px', fontWeight: 700, color: '#FFFFFF' }}>
                    {def.display_name}
                  </h4>
                  <span
                    style={{
                      fontSize: '11px',
                      padding: '2px 8px',
                      borderRadius: '6px',
                      background: 'rgba(255, 255, 255, 0.05)',
                      color: '#94A3B8',
                    }}
                  >
                    {def.unit}
                  </span>
                </div>
                <p style={{ fontSize: '13px', color: '#94A3B8', lineHeight: 1.5, marginBottom: '12px' }}>
                  {def.description}
                </p>
                <div
                  style={{
                    background: 'rgba(0, 0, 0, 0.25)',
                    padding: '10px 12px',
                    borderRadius: '8px',
                    fontSize: '12px',
                    color: '#CBD5E1',
                    marginBottom: '12px',
                  }}
                >
                  <strong style={{ color: '#00F0FF' }}>Construct: </strong>
                  {def.underlying_construct}
                </div>
                <div style={{ fontSize: '12px', color: '#64748B' }}>
                  <strong style={{ color: '#F59E0B' }}>Limitations: </strong>
                  {def.limitations.join(' ')}
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* TAB 2: OCCUPATIONAL DEMAND EXPLORER */}
      {activeTab === 'explorer' && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          {/* Controls Bar */}
          <div
            style={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: '16px',
              background: 'rgba(15, 23, 42, 0.6)',
              padding: '16px 20px',
              borderRadius: '12px',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              marginBottom: '24px',
              alignItems: 'center',
            }}
          >
            {/* Market Picker */}
            <div>
              <label style={{ display: 'block', fontSize: '11px', fontWeight: 600, color: '#94A3B8', marginBottom: '6px' }}>
                SELECT MARKET
              </label>
              <div style={{ display: 'flex', gap: '6px' }}>
                {(['US', 'AU', 'UK', 'SG', 'IN'] as const).map((mCode) => (
                  <button
                    key={mCode}
                    onClick={() => setSelectedMarket(mCode)}
                    style={{
                      padding: '8px 14px',
                      borderRadius: '8px',
                      border: selectedMarket === mCode ? '1px solid #00F0FF' : '1px solid rgba(255, 255, 255, 0.1)',
                      background: selectedMarket === mCode ? 'rgba(0, 240, 255, 0.15)' : 'rgba(255, 255, 255, 0.03)',
                      color: selectedMarket === mCode ? '#00F0FF' : '#E2E8F0',
                      fontSize: '13px',
                      fontWeight: 600,
                      cursor: 'pointer',
                    }}
                  >
                    {MARKET_FLAGS[mCode]} {mCode}
                  </button>
                ))}
              </div>
            </div>

            {/* Occupation Selector */}
            <div style={{ flex: 1, minWidth: '280px' }}>
              <label style={{ display: 'block', fontSize: '11px', fontWeight: 600, color: '#94A3B8', marginBottom: '6px' }}>
                SELECT NATIONAL OCCUPATION ({marketObservations.length} available)
              </label>
              <select
                value={selectedOccId}
                onChange={(e) => setSelectedOccId(e.target.value)}
                style={{
                  width: '100%',
                  padding: '9px 12px',
                  borderRadius: '8px',
                  background: '#0B0F17',
                  border: '1px solid rgba(255, 255, 255, 0.15)',
                  color: '#FFFFFF',
                  fontSize: '13px',
                }}
              >
                {marketObservations.map((o) => (
                  <option key={o.observation_id} value={o.occupation_id}>
                    {o.occupation_id.split(':').pop()} — {o.notes?.split('.')[0] || o.occupation_id}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Profile Content */}
          {profileLoading && (
            <div style={{ textAlign: 'center', padding: '60px 0', color: '#94A3B8' }}>
              Loading occupation demand profile...
            </div>
          )}

          {!profileLoading && occupationProfile && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              {/* UK Publication Gate Banner */}
              {occupationProfile.publication_gate_active && (
                <div
                  style={{
                    padding: '20px 24px',
                    background: 'rgba(239, 68, 68, 0.12)',
                    border: '1px solid rgba(239, 68, 68, 0.35)',
                    borderRadius: '16px',
                    color: '#FCA5A5',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                    <ShieldAlert size={22} style={{ color: '#EF4444' }} />
                    <h3 style={{ fontSize: '16px', fontWeight: 700, margin: 0, color: '#FFFFFF' }}>
                      UK Labour Demand Publication Gate Active ({occupationProfile.publication_gate_code || 'UK_DEMAND_DATA_NOT_PUBLISHED'})
                    </h3>
                  </div>
                  <p style={{ margin: '0 0 10px 0', fontSize: '14px', lineHeight: 1.5, color: '#FEE2E2', fontWeight: 600 }}>
                    {occupationProfile.publication_gate_message || 'UK demand data is currently withheld pending source-use and redistribution review.'}
                  </p>
                  <div style={{ fontSize: '12px', color: '#CBD5E1', lineHeight: 1.5 }}>
                    <strong>Governance Notice: </strong> ONS experimental online advert volumes utilize third-party job vacancy feeds from Textkernel BV. While UK shortage occupations from the Home Office Immigration Salary List remain accessible, numeric advertisement index distributions are withheld pending commercial redistribution and licensing review.
                  </div>
                </div>
              )}

              {/* India Calibrated Benchmark Banner */}
              {occupationProfile.benchmark_disclosure && (
                <div
                  style={{
                    padding: '16px 20px',
                    background: 'rgba(245, 158, 11, 0.12)',
                    border: '1px solid rgba(245, 158, 11, 0.35)',
                    borderRadius: '12px',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#F59E0B', fontWeight: 700, fontSize: '13px', marginBottom: '4px' }}>
                    <AlertTriangle size={16} />
                    CALIBRATED BENCHMARK — EMPIRICAL TECH SAMPLE
                  </div>
                  <div style={{ fontSize: '12px', color: '#CBD5E1', lineHeight: 1.5 }}>
                    {occupationProfile.benchmark_disclosure}
                  </div>
                </div>
              )}

              {/* Primary Stat Card */}
              <div
                style={{
                  background: 'rgba(15, 23, 42, 0.75)',
                  borderRadius: '16px',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  padding: '24px 28px',
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                  gap: '24px',
                  alignItems: 'center',
                }}
              >
                <div>
                  <div style={{ fontSize: '13px', color: '#94A3B8', marginBottom: '4px' }}>
                    {occupationProfile.occupation_id}
                  </div>
                  <h2 style={{ fontSize: '24px', fontWeight: 800, margin: '0 0 8px 0', color: '#FFFFFF' }}>
                    {occupationProfile.occupation_title}
                  </h2>
                  <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                    <span
                      style={{
                        fontSize: '11px',
                        padding: '3px 10px',
                        borderRadius: '20px',
                        background: 'rgba(0, 240, 255, 0.12)',
                        color: '#00F0FF',
                        border: '1px solid rgba(0, 240, 255, 0.3)',
                      }}
                    >
                      Canonical: {occupationProfile.canonical_title || 'Software Engineer'}
                    </span>
                    <span
                      style={{
                        fontSize: '11px',
                        padding: '3px 10px',
                        borderRadius: '20px',
                        background: 'rgba(255, 255, 255, 0.08)',
                        color: '#CBD5E1',
                      }}
                    >
                      Ref: {occupationProfile.reference_period}
                    </span>
                    {(() => {
                      const provKey = occupationProfile.provenance || 'OFFICIALLY_DERIVED';
                      const provCfg = PROVENANCE_CONFIG[provKey] || PROVENANCE_CONFIG.OFFICIALLY_DERIVED;
                      return (
                        <button
                          onClick={() => setShowProvenanceDetails(!showProvenanceDetails)}
                          style={{
                            fontSize: '11px',
                            fontWeight: 600,
                            padding: '3px 10px',
                            borderRadius: '20px',
                            background: provCfg.bg,
                            color: provCfg.color,
                            border: `1px solid ${provCfg.border}`,
                            cursor: 'pointer',
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '4px',
                          }}
                          title="Click to view full provenance & derivation methodology"
                        >
                          <span>{provCfg.label}</span>
                          <HelpCircle size={12} />
                        </button>
                      );
                    })()}
                  </div>
                  {showProvenanceDetails && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      style={{
                        marginTop: '12px',
                        padding: '12px 16px',
                        background: 'rgba(0, 0, 0, 0.4)',
                        border: '1px solid rgba(255, 255, 255, 0.1)',
                        borderRadius: '10px',
                        fontSize: '12px',
                        color: '#CBD5E1',
                        lineHeight: 1.5,
                      }}
                    >
                      <div style={{ fontWeight: 700, color: '#00F0FF', marginBottom: '4px' }}>
                        Methodology & Provenance Ledger
                      </div>
                      <div style={{ marginBottom: '4px' }}>
                        <strong>Description: </strong>{occupationProfile.provenance_description || 'Derived from verified official statistics.'}
                      </div>
                      {occupationProfile.transformation_method && (
                        <div style={{ marginBottom: '4px' }}>
                          <strong>Transformation: </strong><code>{occupationProfile.transformation_method}</code>
                        </div>
                      )}
                      {occupationProfile.derivation_summary && (
                        <div>
                          <strong>Derivation Details: </strong>{occupationProfile.derivation_summary}
                        </div>
                      )}
                    </motion.div>
                  )}
                </div>

                <div>
                  <div style={{ fontSize: '12px', color: '#94A3B8', marginBottom: '4px' }}>
                    PRIMARY DEMAND VOLUME
                  </div>
                  <div style={{ fontSize: occupationProfile.publication_gate_active ? '20px' : '32px', fontWeight: 800, color: occupationProfile.publication_gate_active ? '#EF4444' : '#00F0FF', letterSpacing: '-0.02em' }}>
                    {occupationProfile.publication_gate_active
                      ? 'WITHHELD PENDING REVIEW'
                      : occupationProfile.primary_metric_value === 0
                      ? '0'
                      : occupationProfile.primary_metric_value !== null && occupationProfile.primary_metric_value !== undefined
                      ? occupationProfile.primary_metric_value.toLocaleString()
                      : 'Not available'}
                  </div>
                  <div style={{ fontSize: '13px', color: '#CBD5E1' }}>
                    {occupationProfile.primary_metric_unit}
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '12px', color: '#94A3B8', marginBottom: '4px' }}>
                    DEMAND TREND & VELOCITY
                  </div>
                  <div
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '6px',
                      fontSize: '15px',
                      fontWeight: 700,
                      color:
                        occupationProfile.trend_direction.includes('GROWTH')
                          ? '#10B981'
                          : occupationProfile.trend_direction.includes('DECLINE')
                          ? '#EF4444'
                          : '#F59E0B',
                    }}
                  >
                    <TrendingUp size={18} />
                    {occupationProfile.trend_direction.replace(/_/g, ' ')}
                    {occupationProfile.trend_percentage_change != null && (
                      <span>({occupationProfile.trend_percentage_change > 0 ? '+' : ''}{occupationProfile.trend_percentage_change}%)</span>
                    )}
                  </div>
                  <div style={{ fontSize: '12px', color: '#94A3B8', marginTop: '2px' }}>
                    {occupationProfile.future_demand_rating || 'Assessed via time-series'}
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '12px', color: '#94A3B8', marginBottom: '4px' }}>
                    GOVERNMENT SHORTAGE STATUS
                  </div>
                  <div
                    style={{
                      fontSize: '13px',
                      fontWeight: 700,
                      padding: '6px 12px',
                      borderRadius: '8px',
                      display: 'inline-block',
                      background:
                        occupationProfile.shortage_status === 'NATIONAL_SHORTAGE'
                          ? 'rgba(239, 68, 68, 0.15)'
                          : occupationProfile.shortage_status === 'REGIONAL_SHORTAGE'
                          ? 'rgba(245, 158, 11, 0.15)'
                          : 'rgba(16, 185, 129, 0.15)',
                      color:
                        occupationProfile.shortage_status === 'NATIONAL_SHORTAGE'
                          ? '#EF4444'
                          : occupationProfile.shortage_status === 'REGIONAL_SHORTAGE'
                          ? '#F59E0B'
                          : '#10B981',
                      border:
                        occupationProfile.shortage_status === 'NATIONAL_SHORTAGE'
                          ? '1px solid rgba(239, 68, 68, 0.3)'
                          : occupationProfile.shortage_status === 'REGIONAL_SHORTAGE'
                          ? '1px solid rgba(245, 158, 11, 0.3)'
                          : '1px solid rgba(16, 185, 129, 0.3)',
                    }}
                  >
                    {occupationProfile.shortage_status.replace(/_/g, ' ')}
                  </div>
                  {occupationProfile.unfilled_rate_over_6_months && (
                    <div style={{ fontSize: '12px', color: '#F59E0B', marginTop: '4px' }}>
                      ⚡ {occupationProfile.unfilled_rate_over_6_months}% unfilled &gt; 6 mo
                    </div>
                  )}
                </div>
              </div>

              {/* Time Series & Regional Breakdown */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '20px' }}>
                {/* Time Series */}
                <div
                  style={{
                    background: 'rgba(15, 23, 42, 0.6)',
                    borderRadius: '12px',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    padding: '20px',
                  }}
                >
                  <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#FFFFFF', marginBottom: '16px' }}>
                    Demand Trajectory & Time-Series Points
                  </h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    {occupationProfile.trend_time_series.length === 0 ? (
                      <div
                        style={{
                          padding: '24px 16px',
                          textAlign: 'center',
                          color: '#94A3B8',
                          fontSize: '13px',
                          background: 'rgba(0, 0, 0, 0.2)',
                          borderRadius: '8px',
                          border: '1px dashed rgba(255, 255, 255, 0.1)',
                        }}
                      >
                        {occupationProfile.publication_gate_active
                          ? 'Time-series observations withheld pending source-use review.'
                          : 'No published time-series observations available for this occupation.'}
                      </div>
                    ) : (
                      occupationProfile.trend_time_series.map((pt) => {
                        const maxVal = Math.max(...occupationProfile.trend_time_series.map((p) => p.value));
                        const pct = Math.round((pt.value / maxVal) * 100);
                        return (
                          <div key={pt.period} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                            <span style={{ width: '100px', fontSize: '12px', color: '#94A3B8' }}>{pt.period}</span>
                            <div style={{ flex: 1, background: 'rgba(255, 255, 255, 0.05)', borderRadius: '4px', height: '14px', overflow: 'hidden' }}>
                              <div
                                style={{
                                  width: `${pct}%`,
                                  height: '100%',
                                  background: pt.is_projected
                                    ? 'linear-gradient(90deg, #7928CA 0%, #FF0080 100%)'
                                    : 'linear-gradient(90deg, #0070F3 0%, #00F0FF 100%)',
                                }}
                              />
                            </div>
                            <span style={{ width: '80px', textAlign: 'right', fontSize: '12px', fontWeight: 600, color: '#FFFFFF' }}>
                              {pt.value.toLocaleString()}
                            </span>
                          </div>
                        );
                      })
                    )}
                  </div>
                </div>

                {/* Regional Breakdown */}
                <div
                  style={{
                    background: 'rgba(15, 23, 42, 0.6)',
                    borderRadius: '12px',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    padding: '20px',
                  }}
                >
                  <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#FFFFFF', marginBottom: '12px' }}>
                    Geographic & Regional Concentration
                  </h3>
                  {occupationProfile.regional_disclosure && (
                    <div
                      style={{
                        padding: '10px 14px',
                        background: 'rgba(0, 240, 255, 0.08)',
                        border: '1px solid rgba(0, 240, 255, 0.2)',
                        borderRadius: '8px',
                        fontSize: '11px',
                        color: '#93C5FD',
                        marginBottom: '12px',
                        lineHeight: 1.4,
                      }}
                    >
                      ℹ️ {occupationProfile.regional_disclosure}
                    </div>
                  )}
                  {occupationProfile.occupation_inheritance_disclosure && (
                    <div
                      style={{
                        padding: '10px 14px',
                        background: 'rgba(245, 158, 11, 0.08)',
                        border: '1px solid rgba(245, 158, 11, 0.2)',
                        borderRadius: '8px',
                        fontSize: '11px',
                        color: '#FCD34D',
                        marginBottom: '12px',
                        lineHeight: 1.4,
                      }}
                    >
                      ⚠️ {occupationProfile.occupation_inheritance_disclosure}
                    </div>
                  )}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    {occupationProfile.regional_distribution.length === 0 ? (
                      <div
                        style={{
                          padding: '24px 16px',
                          textAlign: 'center',
                          color: '#94A3B8',
                          fontSize: '13px',
                          background: 'rgba(0, 0, 0, 0.2)',
                          borderRadius: '8px',
                          border: '1px dashed rgba(255, 255, 255, 0.1)',
                        }}
                      >
                        {occupationProfile.publication_gate_active
                          ? 'Regional distribution withheld pending source-use review.'
                          : 'No published regional distribution available for this occupation.'}
                      </div>
                    ) : (
                      occupationProfile.regional_distribution.map((r) => (
                        <div key={r.region_code} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                          <span style={{ width: '140px', fontSize: '12px', color: '#CBD5E1', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {r.region_name}
                          </span>
                          <div style={{ flex: 1, background: 'rgba(255, 255, 255, 0.05)', borderRadius: '4px', height: '14px', overflow: 'hidden' }}>
                            <div
                              style={{
                                width: `${r.share_percentage || 20}%`,
                                height: '100%',
                                background: '#10B981',
                              }}
                            />
                          </div>
                          <span style={{ width: '50px', textAlign: 'right', fontSize: '12px', fontWeight: 600, color: '#10B981' }}>
                            {r.share_percentage ? `${r.share_percentage}%` : `${r.value}`}
                          </span>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>

              {/* Top Skills for Occupation */}
              <div
                style={{
                  background: 'rgba(15, 23, 42, 0.6)',
                  borderRadius: '12px',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  padding: '20px',
                }}
              >
                <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#FFFFFF', marginBottom: '16px' }}>
                  In-Demand Competencies & Technical Skills
                </h3>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
                  {occupationProfile.top_skills.map((s) => (
                    <div
                      key={s.skill_name}
                      style={{
                        padding: '8px 14px',
                        borderRadius: '8px',
                        background: s.is_hot_skill ? 'rgba(245, 158, 11, 0.12)' : 'rgba(255, 255, 255, 0.04)',
                        border: s.is_hot_skill ? '1px solid rgba(245, 158, 11, 0.3)' : '1px solid rgba(255, 255, 255, 0.08)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                      }}
                    >
                      {s.is_hot_skill && <Flame size={14} style={{ color: '#F59E0B' }} />}
                      <span style={{ fontSize: '13px', fontWeight: 600, color: '#FFFFFF' }}>{s.skill_name}</span>
                      <span style={{ fontSize: '11px', color: '#94A3B8' }}>{s.importance_score}/100</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Source Provenance Footer */}
              <div
                style={{
                  padding: '16px 20px',
                  background: 'rgba(0, 0, 0, 0.3)',
                  borderRadius: '8px',
                  fontSize: '12px',
                  color: '#94A3B8',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  flexWrap: 'wrap',
                  gap: '12px',
                }}
              >
                <div>
                  <strong>Official Authority: </strong>
                  {occupationProfile.source_attributions[0]?.publisher} (
                  <a
                    href={occupationProfile.source_attributions[0]?.canonical_url}
                    target="_blank"
                    rel="noreferrer"
                    style={{ color: '#00F0FF', textDecoration: 'none' }}
                  >
                    {occupationProfile.source_attributions[0]?.source_name}
                  </a>
                  ) — License: {occupationProfile.source_attributions[0]?.license}
                </div>
                <div style={{ color: '#64748B' }}>
                  Quality Grade: {occupationProfile.source_attributions[0]?.data_quality_grade}
                </div>
              </div>
            </div>
          )}
        </motion.div>
      )}

      {/* TAB 3: 11-DIMENSION CROSS-MARKET COMPARISON */}
      {activeTab === 'comparison' && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          {/* Controls */}
          <div
            style={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: '16px',
              background: 'rgba(15, 23, 42, 0.6)',
              padding: '16px 20px',
              borderRadius: '12px',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              marginBottom: '24px',
              alignItems: 'center',
            }}
          >
            <div>
              <label style={{ display: 'block', fontSize: '11px', fontWeight: 600, color: '#94A3B8', marginBottom: '6px' }}>
                CANONICAL CONCEPT
              </label>
              <select
                value={compCanonical}
                onChange={(e) => setCompCanonical(e.target.value)}
                style={{
                  padding: '8px 12px',
                  borderRadius: '8px',
                  background: '#0B0F17',
                  border: '1px solid rgba(255, 255, 255, 0.15)',
                  color: '#FFFFFF',
                  fontSize: '13px',
                }}
              >
                <option value="CAN_OCC_SOFTWARE_ENGINEER">Software Engineer</option>
                <option value="CAN_OCC_DATA_SCIENTIST">Data Scientist</option>
                <option value="CAN_OCC_CYBERSECURITY_ANALYST">Cybersecurity Analyst</option>
                <option value="CAN_OCC_QA_TEST_ENGINEER">Software QA / Test Engineer</option>
                <option value="CAN_OCC_DEVOPS_ENGINEER">DevOps & Cloud Engineer</option>
                <option value="CAN_OCC_DATABASE_ADMIN">Database Administrator</option>
                <option value="CAN_OCC_SYSTEMS_ANALYST">Systems Analyst</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '11px', fontWeight: 600, color: '#94A3B8', marginBottom: '6px' }}>
                MARKET A
              </label>
              <select
                value={compMarketA}
                onChange={(e) => setCompMarketA(e.target.value)}
                style={{
                  padding: '8px 12px',
                  borderRadius: '8px',
                  background: '#0B0F17',
                  border: '1px solid rgba(255, 255, 255, 0.15)',
                  color: '#FFFFFF',
                  fontSize: '13px',
                }}
              >
                <option value="US">🇺🇸 United States</option>
                <option value="AU">🇦🇺 Australia</option>
                <option value="UK">🇬🇧 United Kingdom</option>
                <option value="SG">🇸🇬 Singapore</option>
                <option value="IN">🇮🇳 India</option>
              </select>
            </div>

            <div style={{ alignSelf: 'flex-end', paddingBottom: '8px', color: '#64748B' }}>
              <ArrowRight size={18} />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '11px', fontWeight: 600, color: '#94A3B8', marginBottom: '6px' }}>
                MARKET B
              </label>
              <select
                value={compMarketB}
                onChange={(e) => setCompMarketB(e.target.value)}
                style={{
                  padding: '8px 12px',
                  borderRadius: '8px',
                  background: '#0B0F17',
                  border: '1px solid rgba(255, 255, 255, 0.15)',
                  color: '#FFFFFF',
                  fontSize: '13px',
                }}
              >
                <option value="AU">🇦🇺 Australia</option>
                <option value="US">🇺🇸 United States</option>
                <option value="UK">🇬🇧 United Kingdom</option>
                <option value="SG">🇸🇬 Singapore</option>
                <option value="IN">🇮🇳 India</option>
              </select>
            </div>
          </div>

          {compLoading && (
            <div style={{ textAlign: 'center', padding: '60px 0', color: '#94A3B8' }}>
              Running 11-dimension comparability engine...
            </div>
          )}

          {!compLoading && comparisonResult && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              {/* Verdict Banner */}
              <div
                style={{
                  background:
                    comparisonResult.verdict === 'DIRECTLY_COMPARABLE'
                      ? 'rgba(16, 185, 129, 0.12)'
                      : comparisonResult.verdict === 'DIRECTIONALLY_COMPARABLE'
                      ? 'rgba(0, 112, 243, 0.12)'
                      : 'rgba(121, 40, 202, 0.12)',
                  border:
                    comparisonResult.verdict === 'DIRECTLY_COMPARABLE'
                      ? '1px solid rgba(16, 185, 129, 0.3)'
                      : comparisonResult.verdict === 'DIRECTIONALLY_COMPARABLE'
                      ? '1px solid rgba(0, 112, 243, 0.3)'
                      : '1px solid rgba(121, 40, 202, 0.3)',
                  borderRadius: '12px',
                  padding: '20px 24px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                  <Scale size={20} style={{ color: '#00F0FF' }} />
                  <span style={{ fontSize: '12px', fontWeight: 700, color: '#94A3B8', letterSpacing: '0.05em' }}>
                    COMPARABILITY ENGINE VERDICT
                  </span>
                  <span
                    style={{
                      fontSize: '12px',
                      fontWeight: 700,
                      padding: '3px 10px',
                      borderRadius: '16px',
                      background: 'rgba(255, 255, 255, 0.1)',
                      color: '#FFFFFF',
                    }}
                  >
                    {comparisonResult.verdict.replace(/_/g, ' ')}
                  </span>
                </div>
                <p style={{ margin: 0, fontSize: '14px', color: '#E2E8F0', lineHeight: 1.6 }}>
                  {comparisonResult.verdict_summary}
                </p>
                {comparisonResult.warnings.length > 0 && (
                  <div style={{ marginTop: '12px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    {comparisonResult.warnings.map((w, i) => (
                      <div key={i} style={{ fontSize: '12px', color: '#F59E0B', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <AlertTriangle size={14} />
                        {w}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Side-by-Side Metric Representation */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div style={{ background: 'rgba(15, 23, 42, 0.6)', borderRadius: '12px', padding: '20px', border: '1px solid rgba(255, 255, 255, 0.08)' }}>
                  <div style={{ fontSize: '12px', color: '#94A3B8', marginBottom: '4px' }}>
                    {MARKET_FLAGS[comparisonResult.market_a]} {comparisonResult.market_a} Profile ({comparisonResult.occupation_a_id})
                  </div>
                  <div style={{ fontSize: comparisonResult.metric_a.publication_gate_active ? '18px' : '24px', fontWeight: 800, color: comparisonResult.metric_a.publication_gate_active ? '#EF4444' : '#00F0FF' }}>
                    {comparisonResult.metric_a.publication_gate_active
                      ? 'WITHHELD PENDING REVIEW'
                      : comparisonResult.metric_a.value === 0
                      ? `0 ${comparisonResult.metric_a.unit}`
                      : comparisonResult.metric_a.value !== null && comparisonResult.metric_a.value !== undefined
                      ? `${comparisonResult.metric_a.value.toLocaleString()} ${comparisonResult.metric_a.unit}`
                      : 'Not available'}
                  </div>
                  <div style={{ fontSize: '12px', color: '#CBD5E1', marginTop: '4px' }}>
                    Construct: {comparisonResult.metric_a.metric_type}
                  </div>
                </div>

                <div style={{ background: 'rgba(15, 23, 42, 0.6)', borderRadius: '12px', padding: '20px', border: '1px solid rgba(255, 255, 255, 0.08)' }}>
                  <div style={{ fontSize: '12px', color: '#94A3B8', marginBottom: '4px' }}>
                    {MARKET_FLAGS[comparisonResult.market_b]} {comparisonResult.market_b} Profile ({comparisonResult.occupation_b_id})
                  </div>
                  <div style={{ fontSize: comparisonResult.metric_b.publication_gate_active ? '18px' : '24px', fontWeight: 800, color: comparisonResult.metric_b.publication_gate_active ? '#EF4444' : '#00F0FF' }}>
                    {comparisonResult.metric_b.publication_gate_active
                      ? 'WITHHELD PENDING REVIEW'
                      : comparisonResult.metric_b.value === 0
                      ? `0 ${comparisonResult.metric_b.unit}`
                      : comparisonResult.metric_b.value !== null && comparisonResult.metric_b.value !== undefined
                      ? `${comparisonResult.metric_b.value.toLocaleString()} ${comparisonResult.metric_b.unit}`
                      : 'Not available'}
                  </div>
                  <div style={{ fontSize: '12px', color: '#CBD5E1', marginTop: '4px' }}>
                    Construct: {comparisonResult.metric_b.metric_type}
                  </div>
                </div>
              </div>

              {/* 11-Dimension Evaluation Table */}
              <div style={{ background: 'rgba(15, 23, 42, 0.6)', borderRadius: '12px', border: '1px solid rgba(255, 255, 255, 0.08)', overflow: 'hidden' }}>
                <div style={{ padding: '16px 20px', borderBottom: '1px solid rgba(255, 255, 255, 0.08)', fontWeight: 700, fontSize: '14px', color: '#FFFFFF' }}>
                  Detailed 11-Dimension Evaluation Matrix
                </div>
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px', textAlign: 'left' }}>
                    <thead>
                      <tr style={{ background: 'rgba(0, 0, 0, 0.3)', color: '#94A3B8' }}>
                        <th style={{ padding: '12px 16px' }}>Dimension</th>
                        <th style={{ padding: '12px 16px' }}>{comparisonResult.market_a} Value</th>
                        <th style={{ padding: '12px 16px' }}>{comparisonResult.market_b} Value</th>
                        <th style={{ padding: '12px 16px' }}>Match</th>
                        <th style={{ padding: '12px 16px' }}>Methodological Assessment</th>
                      </tr>
                    </thead>
                    <tbody>
                      {comparisonResult.dimension_evaluations.map((dim, idx) => (
                        <tr key={idx} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                          <td style={{ padding: '12px 16px', fontWeight: 600, color: '#FFFFFF' }}>
                            {dim.dimension}
                          </td>
                          <td style={{ padding: '12px 16px', color: '#CBD5E1' }}>{dim.market_a_value}</td>
                          <td style={{ padding: '12px 16px', color: '#CBD5E1' }}>{dim.market_b_value}</td>
                          <td style={{ padding: '12px 16px' }}>
                            {dim.match ? (
                              <span style={{ color: '#10B981', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                <Check size={14} /> Match
                              </span>
                            ) : (
                              <span
                                style={{
                                  color: dim.severity === 'CRITICAL' ? '#EF4444' : '#F59E0B',
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: '4px',
                                  fontWeight: 600,
                                }}
                              >
                                <XCircle size={14} /> {dim.severity} Mismatch
                              </span>
                            )}
                          </td>
                          <td style={{ padding: '12px 16px', color: '#94A3B8', fontSize: '12px' }}>
                            {dim.comment}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </motion.div>
      )}

      {/* TAB 4: INTERACTIVE SKILL DEMAND & GAP ANALYZER */}
      {activeTab === 'skills_gap' && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px' }}>
            {/* Left: Input & Selectors */}
            <div>
              <div
                style={{
                  background: 'rgba(15, 23, 42, 0.6)',
                  borderRadius: '12px',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  padding: '20px',
                  marginBottom: '20px',
                }}
              >
                <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#FFFFFF', marginBottom: '16px' }}>
                  Target Career Role & Market
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  <div>
                    <label style={{ display: 'block', fontSize: '11px', fontWeight: 600, color: '#94A3B8', marginBottom: '4px' }}>
                      TARGET MARKET
                    </label>
                    <select
                      value={gapMarket}
                      onChange={(e) => setGapMarket(e.target.value)}
                      style={{
                        width: '100%',
                        padding: '8px 12px',
                        borderRadius: '8px',
                        background: '#0B0F17',
                        border: '1px solid rgba(255, 255, 255, 0.15)',
                        color: '#FFFFFF',
                      }}
                    >
                      <option value="US">🇺🇸 United States (BLS / O*NET)</option>
                      <option value="AU">🇦🇺 Australia (JSA IVI / SPL)</option>
                      <option value="UK">🇬🇧 United Kingdom (ONS / Skills England)</option>
                      <option value="SG">🇸🇬 Singapore (MOM / SkillsFuture)</option>
                      <option value="IN">🇮🇳 India (JobIntel Tech Benchmark)</option>
                    </select>
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '11px', fontWeight: 600, color: '#94A3B8', marginBottom: '4px' }}>
                      OCCUPATION CODE
                    </label>
                    <input
                      type="text"
                      value={gapOccupationId}
                      onChange={(e) => setGapOccupationId(e.target.value)}
                      placeholder="e.g. 15-1252, 261313, 2134, 25121"
                      style={{
                        width: '100%',
                        padding: '8px 12px',
                        borderRadius: '8px',
                        background: '#0B0F17',
                        border: '1px solid rgba(255, 255, 255, 0.15)',
                        color: '#FFFFFF',
                      }}
                    />
                  </div>
                </div>
              </div>

              {/* Skill Input & Quick Toggles */}
              <div
                style={{
                  background: 'rgba(15, 23, 42, 0.6)',
                  borderRadius: '12px',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  padding: '20px',
                }}
              >
                <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#FFFFFF', marginBottom: '12px' }}>
                  Your Current Skills Inventory
                </h3>
                <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
                  <input
                    type="text"
                    value={customSkillInput}
                    onChange={(e) => setCustomSkillInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && addCustomSkill()}
                    placeholder="Add a skill (e.g. Kubernetes, React, AWS)..."
                    style={{
                      flex: 1,
                      padding: '8px 12px',
                      borderRadius: '8px',
                      background: '#0B0F17',
                      border: '1px solid rgba(255, 255, 255, 0.15)',
                      color: '#FFFFFF',
                      fontSize: '13px',
                    }}
                  />
                  <button
                    onClick={addCustomSkill}
                    style={{
                      padding: '8px 16px',
                      borderRadius: '8px',
                      background: 'rgba(0, 240, 255, 0.15)',
                      border: '1px solid rgba(0, 240, 255, 0.3)',
                      color: '#00F0FF',
                      fontSize: '13px',
                      fontWeight: 600,
                      cursor: 'pointer',
                    }}
                  >
                    Add
                  </button>
                </div>

                <div style={{ fontSize: '11px', fontWeight: 600, color: '#94A3B8', marginBottom: '8px' }}>
                  QUICK TOGGLE POPULAR TECH SKILLS:
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '16px' }}>
                  {[
                    'Python',
                    'Java',
                    'TypeScript',
                    'SQL',
                    'Docker',
                    'Kubernetes',
                    'AWS',
                    'System Design',
                    'REST APIs',
                    'React',
                    'Git',
                    'Machine Learning',
                    'CI/CD',
                  ].map((s) => {
                    const isSelected = userSkills.includes(s);
                    return (
                      <button
                        key={s}
                        onClick={() => toggleUserSkill(s)}
                        style={{
                          padding: '5px 10px',
                          borderRadius: '16px',
                          border: isSelected ? '1px solid #00F0FF' : '1px solid rgba(255, 255, 255, 0.1)',
                          background: isSelected ? 'rgba(0, 240, 255, 0.15)' : 'rgba(255, 255, 255, 0.03)',
                          color: isSelected ? '#00F0FF' : '#94A3B8',
                          fontSize: '12px',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '4px',
                        }}
                      >
                        {isSelected && <Check size={12} />}
                        {s}
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Right: Gap Analysis Results */}
            <div>
              {gapLoading && (
                <div style={{ textAlign: 'center', padding: '60px 0', color: '#94A3B8' }}>
                  Calculating alignment with market prerequisites...
                </div>
              )}

              {!gapLoading && gapResult && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                  {/* Alignment Scorecard */}
                  <div
                    style={{
                      background: 'rgba(15, 23, 42, 0.7)',
                      borderRadius: '12px',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      padding: '24px',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                      <div>
                        <div style={{ fontSize: '12px', color: '#94A3B8' }}>
                          CAREER MARKET READINESS
                        </div>
                        <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 700, color: '#FFFFFF' }}>
                          {gapResult.target_occupation_title}
                        </h3>
                      </div>
                      <span
                        style={{
                          fontSize: '13px',
                          fontWeight: 700,
                          padding: '6px 14px',
                          borderRadius: '20px',
                          background:
                            gapResult.readiness_level === 'HIGH'
                              ? 'rgba(16, 185, 129, 0.2)'
                              : gapResult.readiness_level === 'MODERATE'
                              ? 'rgba(0, 112, 243, 0.2)'
                              : 'rgba(245, 158, 11, 0.2)',
                          color:
                            gapResult.readiness_level === 'HIGH'
                              ? '#10B981'
                              : gapResult.readiness_level === 'MODERATE'
                              ? '#0070F3'
                              : '#F59E0B',
                          border:
                            gapResult.readiness_level === 'HIGH'
                              ? '1px solid #10B981'
                              : gapResult.readiness_level === 'MODERATE'
                              ? '1px solid #0070F3'
                              : '1px solid #F59E0B',
                        }}
                      >
                        {gapResult.readiness_level} TIER
                      </span>
                    </div>

                    {/* Progress Bar */}
                    <div style={{ marginBottom: '8px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
                        <span style={{ color: '#CBD5E1' }}>Overall Skill Match Weight</span>
                        <span style={{ color: '#00F0FF' }}>{gapResult.match_percentage}%</span>
                      </div>
                      <div style={{ background: 'rgba(255, 255, 255, 0.08)', borderRadius: '6px', height: '12px', overflow: 'hidden' }}>
                        <div
                          style={{
                            width: `${gapResult.match_percentage}%`,
                            height: '100%',
                            background: 'linear-gradient(90deg, #0070F3 0%, #00F0FF 100%)',
                          }}
                        />
                      </div>
                    </div>

                    {/* Mathematical Formula Transparency */}
                    <div
                      style={{
                        marginTop: '12px',
                        padding: '12px 14px',
                        background: 'rgba(0, 0, 0, 0.3)',
                        borderRadius: '8px',
                        border: '1px solid rgba(255, 255, 255, 0.08)',
                        fontSize: '11px',
                        color: '#94A3B8',
                        lineHeight: 1.5,
                      }}
                    >
                      <div style={{ fontWeight: 600, color: '#CBD5E1', marginBottom: '4px' }}>
                        📐 Mathematical Formula & Weight Breakdown:
                      </div>
                      <code style={{ color: '#00F0FF', display: 'block', marginBottom: '6px' }}>
                        {gapResult.formula_explanation || 'Skill Coverage (%) = (Matched Skill Weight / Total Required Skill Weight) * 100'}
                      </code>
                      <div style={{ marginBottom: '4px' }}>
                        Matched Weight: <strong style={{ color: '#FFFFFF' }}>{gapResult.matched_skill_weight ?? '—'}</strong> / Total Required Weight: <strong style={{ color: '#FFFFFF' }}>{gapResult.total_required_weight ?? '—'}</strong>
                      </div>
                      <div style={{ fontSize: '10px', color: '#64748B' }}>
                        {gapResult.methodology_notes || 'Skill coverage measures alignment between candidate skills and employer-requested competencies for the occupation. It is not an employability probability, hiring probability, or placement guarantee.'}
                      </div>
                    </div>
                  </div>

                  {/* Missing Critical Skills */}
                  {gapResult.missing_critical_skills.length > 0 && (
                    <div
                      style={{
                        background: 'rgba(239, 68, 68, 0.08)',
                        border: '1px solid rgba(239, 68, 68, 0.25)',
                        borderRadius: '12px',
                        padding: '20px',
                      }}
                    >
                      <h4 style={{ margin: '0 0 12px 0', fontSize: '14px', fontWeight: 700, color: '#EF4444', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <AlertTriangle size={16} />
                        Missing Critical Competencies ({gapResult.missing_critical_skills.length})
                      </h4>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                        {gapResult.missing_critical_skills.map((s) => (
                          <div
                            key={s.skill_name}
                            style={{
                              padding: '6px 12px',
                              borderRadius: '8px',
                              background: 'rgba(239, 68, 68, 0.15)',
                              border: '1px solid rgba(239, 68, 68, 0.3)',
                              fontSize: '12px',
                              color: '#FCA5A5',
                              fontWeight: 600,
                            }}
                          >
                            {s.skill_name} ({s.importance_score}/100)
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Recommendations */}
                  <div
                    style={{
                      background: 'rgba(15, 23, 42, 0.6)',
                      borderRadius: '12px',
                      border: '1px solid rgba(255, 255, 255, 0.08)',
                      padding: '20px',
                    }}
                  >
                    <h4 style={{ margin: '0 0 12px 0', fontSize: '14px', fontWeight: 700, color: '#FFFFFF', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <Sparkles size={16} style={{ color: '#00F0FF' }} />
                      Actionable Career Learning Roadmap
                    </h4>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      {gapResult.recommendations.map((rec, i) => (
                        <div
                          key={i}
                          style={{
                            padding: '10px 14px',
                            borderRadius: '8px',
                            background: 'rgba(255, 255, 255, 0.03)',
                            fontSize: '13px',
                            color: '#CBD5E1',
                            lineHeight: 1.5,
                          }}
                        >
                          {rec}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};
