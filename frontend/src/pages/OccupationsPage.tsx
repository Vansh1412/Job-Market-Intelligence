import React, { useEffect, useState } from 'react';
import {
  Globe2,
  Search,
  Layers,
  ArrowRight,
  ShieldCheck,
  AlertTriangle,
  Info,
  BookOpen,
  CheckCircle2,
  ExternalLink,
  ChevronRight,
  Sparkles,
  GitCompare,
  DollarSign,
  Coins,
  Scale,
  ArrowRightLeft,
  TrendingUp,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { PageHero } from '../components/PageHero';
import { api } from '../services/api';
import {
  ClassificationSystem,
  NationalOccupation,
  CanonicalOccupation,
  CrossMarketComparisonResult,
  ConcordanceCoverageStats,
  OccupationSalaryProfile,
  CrossMarketSalaryComparisonResult,
  SalarySourceMeta,
  PppFxRatesPayload,
  SalaryConversionResult,
  ComparabilityVerdict,
} from '../types';

type ActiveTab = 'concordance' | 'explorer' | 'canonical' | 'salary';

const MARKET_FLAGS: Record<string, string> = {
  UK: '🇬🇧',
  US: '🇺🇸',
  AU: '🇦🇺',
  SG: '🇸🇬',
  IN: '🇮🇳',
  INT: '🌐',
};

const COMPARABILITY_VERDICT_COLORS: Record<string, { bg: string; text: string; border: string; label: string }> = {
  DIRECTLY_COMPARABLE_WITHIN_SOURCE_LIMITATIONS: {
    bg: 'rgba(34, 197, 94, 0.15)',
    text: '#4ADE80',
    border: 'rgba(34, 197, 94, 0.3)',
    label: 'Directly Comparable Within Limitations',
  },
  COMPARABLE_WITH_ADJUSTMENTS: {
    bg: 'rgba(59, 130, 246, 0.15)',
    text: '#60A5FA',
    border: 'rgba(59, 130, 246, 0.3)',
    label: 'Comparable With Adjustments',
  },
  COMPARABLE_WITH_MAJOR_CAVEATS: {
    bg: 'rgba(234, 179, 8, 0.15)',
    text: '#FACC15',
    border: 'rgba(234, 179, 8, 0.3)',
    label: 'Comparable With Major Caveats',
  },
  NOT_COMPARABLE: {
    bg: 'rgba(239, 68, 68, 0.15)',
    text: '#F87171',
    border: 'rgba(239, 68, 68, 0.3)',
    label: 'Not Comparable',
  },
  INSUFFICIENT_DATA: {
    bg: 'rgba(148, 163, 184, 0.15)',
    text: '#94A3B8',
    border: 'rgba(148, 163, 184, 0.3)',
    label: 'Data Withheld / Insufficient',
  },
};

const RELATIONSHIP_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  EXACT_MATCH: { bg: 'rgba(34, 197, 94, 0.15)', text: '#4ADE80', border: 'rgba(34, 197, 94, 0.3)' },
  CLOSE_MATCH: { bg: 'rgba(59, 130, 246, 0.15)', text: '#60A5FA', border: 'rgba(59, 130, 246, 0.3)' },
  BROADER_THAN: { bg: 'rgba(234, 179, 8, 0.15)', text: '#FACC15', border: 'rgba(234, 179, 8, 0.3)' },
  NARROWER_THAN: { bg: 'rgba(249, 115, 22, 0.15)', text: '#FB923C', border: 'rgba(249, 115, 22, 0.3)' },
  PARTIAL_OVERLAP: { bg: 'rgba(168, 85, 247, 0.15)', text: '#C084FC', border: 'rgba(168, 85, 247, 0.3)' },
  RELATED_BUT_DISTINCT: { bg: 'rgba(148, 163, 184, 0.15)', text: '#94A3B8', border: 'rgba(148, 163, 184, 0.3)' },
  NO_SUPPORTED_MAPPING: { bg: 'rgba(239, 68, 68, 0.15)', text: '#F87171', border: 'rgba(239, 68, 68, 0.3)' },
};

export const OccupationsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<ActiveTab>('concordance');
  const [classifications, setClassifications] = useState<ClassificationSystem[]>([]);
  const [canonicalList, setCanonicalList] = useState<CanonicalOccupation[]>([]);
  const [coverageStats, setCoverageStats] = useState<ConcordanceCoverageStats | null>(null);
  const [selectedClassification, setSelectedClassification] = useState<string>('UK_SOC_2020');
  const [occupationsList, setOccupationsList] = useState<NationalOccupation[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Concordance State
  const [selectedSourceId, setSelectedSourceId] = useState<string>('UK_SOC_2020:2134');
  const [concordanceResult, setConcordanceResult] = useState<CrossMarketComparisonResult | null>(null);
  const [concordanceLoading, setConcordanceLoading] = useState<boolean>(false);

  // Search State
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [searchResults, setSearchResults] = useState<NationalOccupation[]>([]);
  const [searching, setSearching] = useState<boolean>(false);

  // Salary Intelligence State (Sprint 3B.1)
  const [salarySourceId, setSalarySourceId] = useState<string>('US_SOC_2018:15-1252');
  const [salaryComparison, setSalaryComparison] = useState<CrossMarketSalaryComparisonResult | null>(null);
  const [salaryProfile, setSalaryProfile] = useState<OccupationSalaryProfile | null>(null);
  const [salaryRates, setSalaryRates] = useState<PppFxRatesPayload | null>(null);
  const [salarySources, setSalarySources] = useState<SalarySourceMeta[]>([]);
  const [salaryLoading, setSalaryLoading] = useState<boolean>(false);
  const [salaryError, setSalaryError] = useState<string | null>(null);

  // Live Currency & PPP Converter State
  const [calcAmount, setCalcAmount] = useState<number>(1200000);
  const [calcCurrency, setCalcCurrency] = useState<string>('INR');
  const [calcResult, setCalcResult] = useState<SalaryConversionResult | null>(null);

  // Initial Load: classifications, canonical concepts, and coverage stats
  useEffect(() => {
    setLoading(true);
    Promise.all([api.getClassifications(), api.getCanonicalOccupations(), api.getConcordanceCoverage()])
      .then(([classData, canonicalData, coverageData]) => {
        setClassifications(classData);
        setCanonicalList(canonicalData);
        setCoverageStats(coverageData);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || 'Failed to initialize occupation intelligence');
        setLoading(false);
      });
  }, []);

  // Load Occupations for selected classification
  useEffect(() => {
    if (!selectedClassification) return;
    api
      .getOccupationsByClassification(selectedClassification, { page: 1, page_size: 50 })
      .then((res) => {
        setOccupationsList(res.items);
      })
      .catch((err) => {
        console.error('Failed to load occupations for classification', err);
      });
  }, [selectedClassification]);

  // Load Concordance Comparison when source changes
  useEffect(() => {
    if (!selectedSourceId) return;
    setConcordanceLoading(true);
    api
      .compareAcrossMarkets(selectedSourceId)
      .then((res) => {
        setConcordanceResult(res);
        setConcordanceLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load concordance comparison', err);
        setConcordanceLoading(false);
      });
  }, [selectedSourceId]);

  // Load Salary Rates and Sources once
  useEffect(() => {
    Promise.all([api.getSalaryRates(), api.getSalarySources()])
      .then(([ratesData, sourcesData]) => {
        setSalaryRates(ratesData);
        setSalarySources(sourcesData);
      })
      .catch((err) => {
        console.error('Failed to load salary rates or sources', err);
      });
  }, []);

  // Load Salary Comparison & Profile when salarySourceId changes
  useEffect(() => {
    if (!salarySourceId) return;
    setSalaryLoading(true);
    setSalaryError(null);
    Promise.allSettled([
      api.compareCrossMarketSalaries(salarySourceId),
      api.getOccupationSalaryProfile(salarySourceId),
    ]).then(([compRes, profRes]) => {
      if (compRes.status === 'fulfilled') {
        setSalaryComparison(compRes.value);
      } else {
        setSalaryError((compRes.reason as Error)?.message || 'Failed to load cross-market comparison');
      }

      if (profRes.status === 'fulfilled') {
        setSalaryProfile(profRes.value);
      } else {
        setSalaryProfile(null);
      }
      setSalaryLoading(false);
    });
  }, [salarySourceId]);

  // Converter execution
  useEffect(() => {
    if (!calcAmount || !calcCurrency) return;
    api
      .convertSalaryAmount(calcAmount, calcCurrency)
      .then((res) => setCalcResult(res))
      .catch((err) => console.error('Converter error', err));
  }, [calcAmount, calcCurrency]);

  // Live Search handler
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setSearching(true);
    api
      .searchOccupations(searchQuery.trim(), undefined, undefined)
      .then((res) => {
        setSearchResults(res);
        setSearching(false);
      })
      .catch((err) => {
        console.error('Search error', err);
        setSearching(false);
      });
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 20px', color: '#94A3B8' }}>
        <div className="ji-spinner" style={{ margin: '0 auto 16px' }} />
        <p>Loading Global Occupation Intelligence Engine...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '40px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid #EF4444', borderRadius: '12px', color: '#FCA5A5', margin: '20px' }}>
        <AlertTriangle size={24} style={{ marginBottom: '8px' }} />
        <h3>Failed to load Occupation Intelligence</h3>
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '1360px', margin: '0 auto', padding: '0 24px 60px 24px' }}>
      <PageHero
        title="Global Occupation Intelligence"
        subtitle="Official national occupational taxonomies, evidence-backed concordance crosswalks, and canonical career concepts across five jurisdictions."
        badge="OFFICIAL TAXONOMIES · EVIDENCE-BACKED CONCORDANCE"
        accentColor="#6366F1"
      />

      {/* Coverage & Concordance Quality Scorecard */}
      {coverageStats && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '14px', marginBottom: '28px' }}>
          <div style={{ background: '#12141A', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '12px', padding: '16px 20px' }}>
            <div style={{ fontSize: '0.74rem', fontWeight: 800, color: '#94A3B8', textTransform: 'uppercase', marginBottom: '4px' }}>
              National Occupations
            </div>
            <div style={{ fontSize: '1.6rem', fontWeight: 900, color: '#FFFFFF' }}>
              {coverageStats.mapped_national_occupations} / {coverageStats.total_national_occupations}
            </div>
            <div style={{ fontSize: '0.78rem', color: '#4ADE80', marginTop: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <CheckCircle2 size={13} />
              100% Coverage (28 Nat + 2 ISCO-08 Intl)
            </div>
          </div>

          <div style={{ background: '#12141A', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '12px', padding: '16px 20px' }}>
            <div style={{ fontSize: '0.74rem', fontWeight: 800, color: '#94A3B8', textTransform: 'uppercase', marginBottom: '4px' }}>
              Canonical Concepts
            </div>
            <div style={{ fontSize: '1.6rem', fontWeight: 900, color: '#FFFFFF' }}>
              {coverageStats.linked_canonical_concepts} / {coverageStats.total_canonical_concepts}
            </div>
            <div style={{ fontSize: '0.78rem', color: '#93C5FD', marginTop: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Layers size={13} />
              {coverageStats.linked_canonical_concepts} Activated · {coverageStats.unlinked_canonical_concepts} Idle (Data Eng)
            </div>
          </div>

          <div style={{ background: '#12141A', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '12px', padding: '16px 20px' }}>
            <div style={{ fontSize: '0.74rem', fontWeight: 800, color: '#94A3B8', textTransform: 'uppercase', marginBottom: '4px' }}>
              Concordance Crosswalks
            </div>
            <div style={{ fontSize: '1.6rem', fontWeight: 900, color: '#FFFFFF' }}>
              {coverageStats.total_mappings}
            </div>
            <div style={{ fontSize: '0.78rem', color: '#A5B4FC', marginTop: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <GitCompare size={13} />
              {coverageStats.official_mappings_count} Official · {coverageStats.expert_reviewed_mappings_count} Expert-Reviewed
            </div>
          </div>

          <div style={{ background: '#12141A', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '12px', padding: '16px 20px' }}>
            <div style={{ fontSize: '0.74rem', fontWeight: 800, color: '#94A3B8', textTransform: 'uppercase', marginBottom: '4px' }}>
              Classification Systems
            </div>
            <div style={{ fontSize: '1.6rem', fontWeight: 900, color: '#FFFFFF' }}>
              {classifications.length}
            </div>
            <div style={{ fontSize: '0.78rem', color: '#FACC15', marginTop: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <ShieldCheck size={13} />
              5 Target Jurisdictions + ILO ISCO-08
            </div>
          </div>
        </div>
      )}

      {/* Main Mode Navigation Tabs */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '28px', borderBottom: '1px solid rgba(255, 255, 255, 0.08)', paddingBottom: '14px' }}>
        <button
          onClick={() => setActiveTab('concordance')}
          style={{
            padding: '10px 18px',
            borderRadius: '8px',
            border: activeTab === 'concordance' ? '1px solid #6366F1' : '1px solid rgba(255, 255, 255, 0.08)',
            background: activeTab === 'concordance' ? 'rgba(99, 102, 241, 0.18)' : 'rgba(255, 255, 255, 0.03)',
            color: activeTab === 'concordance' ? '#FFFFFF' : '#94A3B8',
            fontSize: '0.92rem',
            fontWeight: 700,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}
        >
          <GitCompare size={17} />
          Cross-Market Concordance
        </button>

        <button
          onClick={() => setActiveTab('explorer')}
          style={{
            padding: '10px 18px',
            borderRadius: '8px',
            border: activeTab === 'explorer' ? '1px solid #6366F1' : '1px solid rgba(255, 255, 255, 0.08)',
            background: activeTab === 'explorer' ? 'rgba(99, 102, 241, 0.18)' : 'rgba(255, 255, 255, 0.03)',
            color: activeTab === 'explorer' ? '#FFFFFF' : '#94A3B8',
            fontSize: '0.92rem',
            fontWeight: 700,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}
        >
          <Globe2 size={17} />
          National Taxonomy Explorer
        </button>

        <button
          onClick={() => setActiveTab('canonical')}
          style={{
            padding: '10px 18px',
            borderRadius: '8px',
            border: activeTab === 'canonical' ? '1px solid #6366F1' : '1px solid rgba(255, 255, 255, 0.08)',
            background: activeTab === 'canonical' ? 'rgba(99, 102, 241, 0.18)' : 'rgba(255, 255, 255, 0.03)',
            color: activeTab === 'canonical' ? '#FFFFFF' : '#94A3B8',
            fontSize: '0.92rem',
            fontWeight: 700,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}
        >
          <Layers size={17} />
          Canonical Career Concepts
        </button>

        <button
          onClick={() => setActiveTab('salary')}
          style={{
            padding: '10px 18px',
            borderRadius: '8px',
            border: activeTab === 'salary' ? '1px solid #10B981' : '1px solid rgba(255, 255, 255, 0.08)',
            background: activeTab === 'salary' ? 'rgba(16, 185, 129, 0.18)' : 'rgba(255, 255, 255, 0.03)',
            color: activeTab === 'salary' ? '#FFFFFF' : '#94A3B8',
            fontSize: '0.92rem',
            fontWeight: 700,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}
        >
          <DollarSign size={17} />
          Cross-Market Salary Intelligence
        </button>
      </div>

      {/* TAB 1: CONCORDANCE & CROSS-MARKET COMPARISON */}
      {activeTab === 'concordance' && (
        <div>
          {/* Quick Benchmark Picker */}
          <div style={{ background: '#12141A', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '12px', padding: '20px', marginBottom: '24px' }}>
            <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>
              Select Source Occupation to Compare Across International Jurisdictions:
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {[
                { id: 'UK_SOC_2020:2134', label: '🇬🇧 UK 2134 Programmers & Software Dev' },
                { id: 'US_SOC_2018:15-1252', label: '🇺🇸 US 15-1252 Software Developers' },
                { id: 'US_SOC_2018:15-2051', label: '🇺🇸 US 15-2051 Data Scientists' },
                { id: 'US_SOC_2018:15-1242', label: '🇺🇸 US 15-1242 Database Administrators' },
                { id: 'UK_SOC_2020:2133', label: '🇬🇧 UK 2133 Systems Designers & Architects' },
                { id: 'UK_SOC_2020:2137', label: '🇬🇧 UK 2137 IT Network Professionals' },
                { id: 'UK_SOC_2020:2131', label: '🇬🇧 UK 2131 IT Project Managers' },
                { id: 'UK_SOC_2020:2135', label: '🇬🇧 UK 2135 Cyber Security Professionals' },
                { id: 'UK_SOC_2020:2136', label: '🇬🇧 UK 2136 IT Quality & Testing' },
                { id: 'AU_OSCA_2024:261313', label: '🇦🇺 AU 261313 Software Engineer' },
                { id: 'SG_SSOC_2024:25121', label: '🇸🇬 SG 25121 Software Developer' },
                { id: 'IN_NCO_2015:2512.0100', label: '🇮🇳 IN 2512.0100 Software Developer' },
              ].map((bench) => (
                <button
                  key={bench.id}
                  onClick={() => setSelectedSourceId(bench.id)}
                  style={{
                    padding: '8px 14px',
                    borderRadius: '6px',
                    border: selectedSourceId === bench.id ? '1px solid #8B5CF6' : '1px solid rgba(255, 255, 255, 0.06)',
                    background: selectedSourceId === bench.id ? 'rgba(139, 92, 246, 0.25)' : 'rgba(255, 255, 255, 0.02)',
                    color: selectedSourceId === bench.id ? '#FFFFFF' : '#CBD5E1',
                    fontSize: '0.85rem',
                    cursor: 'pointer',
                    fontWeight: selectedSourceId === bench.id ? 700 : 500,
                  }}
                >
                  {bench.label}
                </button>
              ))}
            </div>
          </div>

          {concordanceLoading && (
            <div style={{ textAlign: 'center', padding: '40px', color: '#94A3B8' }}>
              <div className="ji-spinner" style={{ margin: '0 auto 12px' }} />
              <p>Analyzing crosswalk concordance graph...</p>
            </div>
          )}

          {!concordanceLoading && concordanceResult && (
            <div>
              {/* Source Profile Header Card */}
              <div style={{ background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%)', border: '1px solid rgba(255, 255, 255, 0.1)', borderRadius: '14px', padding: '24px', marginBottom: '24px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                  <span style={{ fontSize: '1.4rem' }}>{MARKET_FLAGS[concordanceResult.source_occupation.market_id] || '🌐'}</span>
                  <span style={{ fontSize: '0.78rem', fontWeight: 800, padding: '3px 8px', borderRadius: '4px', background: 'rgba(99, 102, 241, 0.25)', color: '#A5B4FC' }}>
                    {concordanceResult.source_occupation.classification_id} · CODE {concordanceResult.source_occupation.occupation_code}
                  </span>
                  <span style={{ fontSize: '0.78rem', color: '#94A3B8' }}>{concordanceResult.source_occupation.hierarchy_level}</span>
                </div>
                <h2 style={{ fontSize: '1.45rem', fontWeight: 900, color: '#FFFFFF', margin: '0 0 10px 0' }}>
                  {concordanceResult.source_occupation.occupation_title}
                </h2>
                <p style={{ fontSize: '0.92rem', color: '#CBD5E1', lineHeight: '1.55', margin: '0 0 14px 0' }}>
                  {concordanceResult.source_occupation.official_definition}
                </p>
                {concordanceResult.source_occupation.entry_qualifications && (
                  <div style={{ fontSize: '0.82rem', color: '#94A3B8', borderTop: '1px solid rgba(255, 255, 255, 0.06)', paddingTop: '10px' }}>
                    <strong>Entry Routes & Qualifications:</strong> {concordanceResult.source_occupation.entry_qualifications}
                  </div>
                )}
              </div>

              {/* Supported Matches Grid */}
              <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#FFFFFF', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle2 size={18} color="#22C55E" />
                Supported Cross-Market Equivalents & Concordance Records ({concordanceResult.total_matches})
              </h3>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(420px, 1fr))', gap: '16px', marginBottom: '28px' }}>
                {concordanceResult.matches.map((match, idx) => {
                  const relStyle = RELATIONSHIP_COLORS[match.relationship_type] || RELATIONSHIP_COLORS.PARTIAL_OVERLAP;
                  const isCanonical = match.target_type === 'CANONICAL';
                  const title = 'occupation_title' in match.target_occupation
                    ? match.target_occupation.occupation_title
                    : match.target_occupation.preferred_title;
                  const code = 'occupation_code' in match.target_occupation
                    ? match.target_occupation.occupation_code
                    : match.target_occupation.canonical_occupation_id;

                  return (
                    <div
                      key={idx}
                      style={{
                        background: '#12141A',
                        border: '1px solid rgba(255, 255, 255, 0.08)',
                        borderRadius: '12px',
                        padding: '20px',
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'space-between',
                      }}
                    >
                      <div>
                        {/* Header: Flag, Type, Confidence */}
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <span style={{ fontSize: '1.3rem' }}>{MARKET_FLAGS[match.target_market_id] || '🌐'}</span>
                            <span style={{ fontSize: '0.75rem', fontWeight: 800, padding: '2px 7px', borderRadius: '4px', background: isCanonical ? 'rgba(168, 85, 247, 0.2)' : 'rgba(59, 130, 246, 0.2)', color: isCanonical ? '#D8B4FE' : '#93C5FD' }}>
                              {isCanonical ? 'CANONICAL CONCEPT' : match.target_market_id}
                            </span>
                            <span style={{ fontSize: '0.78rem', color: '#64748B' }}>{code}</span>
                          </div>

                          <div style={{ textAlign: 'right', display: 'flex', flexDirection: 'column', gap: '4px', alignItems: 'flex-end' }}>
                            <span
                              style={{
                                fontSize: '0.82rem',
                                fontWeight: 800,
                                padding: '3px 8px',
                                borderRadius: '6px',
                                background: Number(match.confidence_score) >= 0.95 ? 'rgba(34, 197, 94, 0.2)' : 'rgba(234, 179, 8, 0.2)',
                                color: Number(match.confidence_score) >= 0.95 ? '#4ADE80' : '#FACC15',
                              }}
                              title="Rule-based heuristic expert confidence"
                            >
                              {Math.round(Number(match.confidence_score) * 100)}% EXPERT HEURISTIC
                            </span>
                            {match.task_similarity != null && (
                              <span
                                style={{
                                  fontSize: '0.74rem',
                                  fontWeight: 700,
                                  padding: '2px 6px',
                                  borderRadius: '4px',
                                  background: 'rgba(99, 102, 241, 0.15)',
                                  color: '#A5B4FC',
                                }}
                                title="Unsupervised lexical task description similarity (TF-IDF Cosine)"
                              >
                                {Math.round(match.task_similarity * 100)}% Lexical Overlap
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Occupation Title */}
                        <h4 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#FFFFFF', margin: '0 0 8px 0' }}>
                          {title}
                        </h4>

                        {/* Relationship Badge */}
                        <div style={{ marginBottom: '12px' }}>
                          <span
                            style={{
                              display: 'inline-block',
                              fontSize: '0.72rem',
                              fontWeight: 800,
                              padding: '2px 8px',
                              borderRadius: '4px',
                              background: relStyle.bg,
                              color: relStyle.text,
                              border: `1px solid ${relStyle.border}`,
                              textTransform: 'uppercase',
                              letterSpacing: '0.04em',
                            }}
                          >
                            {match.relationship_type.replace(/_/g, ' ')}
                          </span>
                        </div>

                        {/* Notes and limitations */}
                        <p style={{ fontSize: '0.85rem', color: '#CBD5E1', lineHeight: '1.5', margin: '0 0 12px 0' }}>
                          {match.notes_and_limitations}
                        </p>

                        {/* Approximation Warning */}
                        {match.approximation_warning && (
                          <div style={{ background: 'rgba(234, 179, 8, 0.08)', border: '1px solid rgba(234, 179, 8, 0.25)', borderRadius: '6px', padding: '8px 10px', fontSize: '0.78rem', color: '#FDE047', marginBottom: '12px' }}>
                            <AlertTriangle size={13} style={{ display: 'inline', marginRight: '5px' }} />
                            {match.approximation_warning}
                          </div>
                        )}
                      </div>

                      {/* Footer: Provenance & Methodology */}
                      <div style={{ borderTop: '1px solid rgba(255, 255, 255, 0.06)', paddingTop: '10px', fontSize: '0.74rem', color: '#64748B', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span>Method: {match.methodology.replace(/_/g, ' ')}</span>
                        <span>Status: {match.review_status.replace(/_/g, ' ')}</span>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Unmapped Markets Section */}
              {concordanceResult.unmapped_markets.length > 0 && (
                <div style={{ background: 'rgba(239, 68, 68, 0.05)', border: '1px solid rgba(239, 68, 68, 0.2)', borderRadius: '12px', padding: '18px 20px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#FCA5A5', fontWeight: 800, fontSize: '0.92rem', marginBottom: '6px' }}>
                    <Info size={16} />
                    Unmapped Jurisdictions ({concordanceResult.unmapped_markets.join(', ')})
                  </div>
                  <p style={{ fontSize: '0.84rem', color: '#94A3B8', margin: 0, lineHeight: '1.5' }}>
                    No verified official concordance or high-confidence correspondence is published between this occupation and the remaining target markets. JOBINTEL strictly preserves national classifications and does not manufacture synthetic matches where task-level alignment is unproven.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* TAB 2: NATIONAL TAXONOMY EXPLORER */}
      {activeTab === 'explorer' && (
        <div>
          {/* Classification Selector */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '20px' }}>
            {classifications.map((cls) => (
              <button
                key={cls.classification_id}
                onClick={() => setSelectedClassification(cls.classification_id)}
                style={{
                  padding: '9px 16px',
                  borderRadius: '8px',
                  border: selectedClassification === cls.classification_id ? '1px solid #3B82F6' : '1px solid rgba(255, 255, 255, 0.08)',
                  background: selectedClassification === cls.classification_id ? 'rgba(59, 130, 246, 0.2)' : 'rgba(255, 255, 255, 0.02)',
                  color: selectedClassification === cls.classification_id ? '#FFFFFF' : '#94A3B8',
                  fontSize: '0.88rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                }}
              >
                <span>{MARKET_FLAGS[cls.market_id] || '🌐'}</span>
                <span>{cls.official_title}</span>
              </button>
            ))}
          </div>

          {/* Active Classification Details */}
          {classifications.find((c) => c.classification_id === selectedClassification) && (
            <div style={{ background: '#12141A', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '12px', padding: '18px 22px', marginBottom: '24px' }}>
              {(() => {
                const c = classifications.find((x) => x.classification_id === selectedClassification)!;
                return (
                  <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
                    <div>
                      <div style={{ fontSize: '0.76rem', fontWeight: 800, color: '#3B82F6', textTransform: 'uppercase' }}>
                        {c.market_id} · {c.version_edition}
                      </div>
                      <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#FFFFFF', margin: '4px 0' }}>
                        {c.official_title}
                      </h3>
                      <div style={{ fontSize: '0.82rem', color: '#94A3B8' }}>
                        Issuing Authority: <strong>{c.issuing_authority}</strong>
                      </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: '0.78rem', color: '#64748B' }}>License: {c.license_attribution}</div>
                      <a
                        href={c.source_reference}
                        target="_blank"
                        rel="noreferrer"
                        style={{ fontSize: '0.82rem', color: '#60A5FA', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '4px', marginTop: '6px' }}
                      >
                        Official Source Documentation <ExternalLink size={13} />
                      </a>
                    </div>
                  </div>
                );
              })()}
            </div>
          )}

          {/* Search within this taxonomy */}
          <form onSubmit={handleSearch} style={{ display: 'flex', gap: '10px', marginBottom: '22px' }}>
            <input
              type="text"
              placeholder="Search by code (e.g. 2134, 15-1252) or title..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                flex: 1,
                padding: '12px 16px',
                borderRadius: '8px',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                background: '#0D0F14',
                color: '#FFFFFF',
                fontSize: '0.92rem',
              }}
            />
            <button
              type="submit"
              disabled={searching}
              style={{
                padding: '12px 22px',
                borderRadius: '8px',
                border: 'none',
                background: '#3B82F6',
                color: '#FFFFFF',
                fontWeight: 700,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              <Search size={16} />
              {searching ? 'Searching...' : 'Search Occupations'}
            </button>
          </form>

          {/* Occupations Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))', gap: '16px' }}>
            {(searchResults.length > 0 ? searchResults : occupationsList).map((occ) => (
              <div
                key={occ.occupation_id}
                style={{
                  background: '#12141A',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  borderRadius: '12px',
                  padding: '20px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                }}
              >
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                      <span style={{ fontSize: '0.78rem', fontWeight: 800, padding: '2px 8px', borderRadius: '4px', background: 'rgba(59, 130, 246, 0.15)', color: '#93C5FD' }}>
                        CODE {occ.occupation_code}
                      </span>
                      {occ.task_provenance && (
                        <span
                          style={{
                            fontSize: '0.70rem',
                            fontWeight: 700,
                            padding: '2px 6px',
                            borderRadius: '4px',
                            background:
                              occ.task_provenance === 'OFFICIAL_VERBATIM'
                                ? 'rgba(34, 197, 94, 0.15)'
                                : occ.task_provenance === 'OFFICIALLY_DERIVED'
                                ? 'rgba(59, 130, 246, 0.15)'
                                : 'rgba(234, 179, 8, 0.15)',
                            color:
                              occ.task_provenance === 'OFFICIAL_VERBATIM'
                                ? '#4ADE80'
                                : occ.task_provenance === 'OFFICIALLY_DERIVED'
                                ? '#93C5FD'
                                : '#FDE047',
                          }}
                        >
                          {occ.task_provenance === 'OFFICIAL_VERBATIM'
                            ? 'Official Verbatim'
                            : occ.task_provenance === 'OFFICIALLY_DERIVED'
                            ? 'Officially Derived'
                            : 'Curated by JOBINTEL'}
                        </span>
                      )}
                    </div>
                    <span style={{ fontSize: '0.76rem', color: '#64748B' }}>{occ.hierarchy_level}</span>
                  </div>
                  <h4 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#FFFFFF', margin: '0 0 10px 0' }}>
                    {occ.occupation_title}
                  </h4>
                  <p style={{ fontSize: '0.84rem', color: '#94A3B8', lineHeight: '1.5', margin: '0 0 12px 0' }}>
                    {occ.official_definition}
                  </p>
                  {occ.alternate_titles.length > 0 && (
                    <div style={{ fontSize: '0.78rem', color: '#64748B', marginBottom: '10px' }}>
                      <strong>Aliases:</strong> {occ.alternate_titles.join(', ')}
                    </div>
                  )}
                </div>

                <div style={{ borderTop: '1px solid rgba(255, 255, 255, 0.06)', paddingTop: '10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <button
                    onClick={() => {
                      setSelectedSourceId(occ.occupation_id);
                      setActiveTab('concordance');
                      window.scrollTo({ top: 0, behavior: 'smooth' });
                    }}
                    style={{
                      background: 'transparent',
                      border: 'none',
                      color: '#60A5FA',
                      fontSize: '0.82rem',
                      fontWeight: 700,
                      cursor: 'pointer',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '4px',
                      padding: 0,
                    }}
                  >
                    Compare Internationally <ChevronRight size={14} />
                  </button>
                  <span style={{ fontSize: '0.74rem', color: '#475569' }}>{occ.classification_id}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 3: CANONICAL CAREER CONCEPTS */}
      {activeTab === 'canonical' && (
        <div>
          <div style={{ background: 'rgba(99, 102, 241, 0.06)', border: '1px solid rgba(99, 102, 241, 0.2)', borderRadius: '12px', padding: '18px 22px', marginBottom: '24px' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#FFFFFF', margin: '0 0 6px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Layers size={18} color="#A5B4FC" />
              Harmonized Canonical Career Layer
            </h3>
            <p style={{ fontSize: '0.86rem', color: '#94A3B8', margin: 0, lineHeight: '1.5' }}>
              Canonical occupations are cross-jurisdictional abstractions that harmonize common roles without overriding official national classifications. Each concept defines core technical competencies required across all jurisdictions.
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))', gap: '16px' }}>
            {canonicalList.map((canon) => (
              <div
                key={canon.canonical_occupation_id}
                style={{
                  background: '#12141A',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  borderRadius: '12px',
                  padding: '22px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                }}
              >
                <div>
                  <div style={{ fontSize: '0.74rem', fontWeight: 800, color: '#A5B4FC', textTransform: 'uppercase', marginBottom: '4px' }}>
                    {canon.concept_family}
                  </div>
                  <h4 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#FFFFFF', margin: '0 0 8px 0' }}>
                    {canon.preferred_title}
                  </h4>
                  <p style={{ fontSize: '0.85rem', color: '#94A3B8', lineHeight: '1.5', margin: '0 0 14px 0' }}>
                    {canon.description}
                  </p>
                  <div style={{ fontSize: '0.78rem', fontWeight: 700, color: '#CBD5E1', marginBottom: '8px' }}>
                    Core Technical Competencies:
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '14px' }}>
                    {canon.core_competencies.map((comp, cIdx) => (
                      <span
                        key={cIdx}
                        style={{
                          fontSize: '0.72rem',
                          padding: '2px 7px',
                          borderRadius: '4px',
                          background: 'rgba(255, 255, 255, 0.05)',
                          color: '#CBD5E1',
                          border: '1px solid rgba(255, 255, 255, 0.06)',
                        }}
                      >
                        {comp}
                      </span>
                    ))}
                  </div>
                </div>

                <div style={{ borderTop: '1px solid rgba(255, 255, 255, 0.06)', paddingTop: '10px', fontSize: '0.74rem', color: '#64748B', display: 'flex', justifyContent: 'space-between' }}>
                  <span>ID: {canon.canonical_occupation_id}</span>
                  <span style={{ color: '#22C55E', fontWeight: 700 }}>STATUS: {canon.status}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 4: CROSS-MARKET SALARY INTELLIGENCE (Sprint 3B.1) */}
      {activeTab === 'salary' && (
        <div>
          {/* Quick Benchmark Picker */}
          <div style={{ background: '#12141A', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '12px', padding: '20px', marginBottom: '24px' }}>
            <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>
              Select Source Occupation for Cross-Market Descriptive Salary Benchmarking:
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '14px' }}>
              {[
                { id: 'US_SOC_2018:15-1252', label: '🇺🇸 US Software Developers (15-1252)' },
                { id: 'US_SOC_2018:15-2051', label: '🇺🇸 US Data Scientists (15-2051)' },
                { id: 'AU_OSCA_2024:261313', label: '🇦🇺 AU Software Engineer (261313)' },
                { id: 'SG_SSOC_2024:25121', label: '🇸🇬 SG Software Developer (25121)' },
                { id: 'IN_NCO_2015:2512.0100', label: '🇮🇳 IN Software Developer (2512.0100)' },
                { id: 'UK_SOC_2020:2134', label: '🇬🇧 UK Software Dev (2134) [Governance Gate]' },
              ].map((bench) => (
                <button
                  key={bench.id}
                  onClick={() => setSalarySourceId(bench.id)}
                  style={{
                    padding: '8px 14px',
                    borderRadius: '8px',
                    border: salarySourceId === bench.id ? '1px solid #10B981' : '1px solid rgba(255, 255, 255, 0.08)',
                    background: salarySourceId === bench.id ? 'rgba(16, 185, 129, 0.2)' : 'rgba(255, 255, 255, 0.03)',
                    color: salarySourceId === bench.id ? '#FFFFFF' : '#CBD5E1',
                    fontSize: '0.84rem',
                    fontWeight: 600,
                    cursor: 'pointer',
                  }}
                >
                  {bench.label}
                </button>
              ))}
            </div>

            {/* Complete Dropdown Selector */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '0.82rem', color: '#94A3B8' }}>Or choose from all 28 catalog occupations:</span>
              <select
                value={salarySourceId}
                onChange={(e) => setSalarySourceId(e.target.value)}
                style={{
                  background: '#0B0D12',
                  border: '1px solid rgba(255, 255, 255, 0.15)',
                  borderRadius: '6px',
                  color: '#FFFFFF',
                  padding: '6px 12px',
                  fontSize: '0.85rem',
                  cursor: 'pointer',
                  maxWidth: '450px',
                }}
              >
                <optgroup label="United States (BLS OEWS)">
                  <option value="US_SOC_2018:15-1252">15-1252 Software Developers</option>
                  <option value="US_SOC_2018:15-2051">15-2051 Data Scientists</option>
                  <option value="US_SOC_2018:15-1253">15-1253 Software QA Analysts and Testers</option>
                  <option value="US_SOC_2018:15-1212">15-1212 Information Security Analysts</option>
                  <option value="US_SOC_2018:15-1242">15-1242 Database Administrators</option>
                  <option value="US_SOC_2018:15-1244">15-1244 Network and Systems Administrators</option>
                  <option value="US_SOC_2018:15-1211">15-1211 Computer Systems Analysts</option>
                </optgroup>
                <optgroup label="Australia (ABS EEH / JSA)">
                  <option value="AU_OSCA_2024:261313">261313 Software Engineer</option>
                  <option value="AU_OSCA_2024:224411">224411 Data Scientist</option>
                  <option value="AU_OSCA_2024:262112">262112 ICT Security Specialist</option>
                  <option value="AU_OSCA_2024:261314">261314 Software Tester</option>
                </optgroup>
                <optgroup label="Singapore (MOM OWS)">
                  <option value="SG_SSOC_2024:25121">25121 Software Developer</option>
                  <option value="SG_SSOC_2024:25131">25131 AI / ML Engineer</option>
                  <option value="SG_SSOC_2024:25132">25132 Data Scientist</option>
                  <option value="SG_SSOC_2024:25124">25124 Cloud Architect</option>
                  <option value="SG_SSOC_2024:25125">25125 DevOps Engineer</option>
                  <option value="SG_SSOC_2024:25211">25211 Cybersecurity Specialist</option>
                </optgroup>
                <optgroup label="India (JobIntel Benchmark / Model)">
                  <option value="IN_NCO_2015:2512.0100">2512.0100 Software Developer</option>
                  <option value="IN_NCO_2015:2511.0100">2511.0100 Systems Analyst</option>
                  <option value="IN_NCO_2015:2521.0100">2521.0100 Database Administrator</option>
                </optgroup>
                <optgroup label="United Kingdom (ONS ASHE - Governance Gate)">
                  <option value="UK_SOC_2020:2134">2134 Programmers and software development professionals</option>
                  <option value="UK_SOC_2020:2135">2135 Cyber security professionals</option>
                  <option value="UK_SOC_2020:2136">2136 IT quality and testing professionals</option>
                  <option value="UK_SOC_2020:2133">2133 IT business analysts and architects</option>
                  <option value="UK_SOC_2020:2137">2137 IT network professionals</option>
                  <option value="UK_SOC_2020:2131">2131 IT project managers</option>
                  <option value="UK_SOC_2020:3133">3133 Database administrators</option>
                  <option value="UK_SOC_2020:3544">3544 Data analysts</option>
                </optgroup>
              </select>
            </div>
          </div>

          {/* Strict FX vs PPP Methodological Separation Callout */}
          <div
            style={{
              background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(59, 130, 246, 0.08) 100%)',
              border: '1px solid rgba(16, 185, 129, 0.25)',
              borderRadius: '12px',
              padding: '18px 22px',
              marginBottom: '28px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#34D399', fontWeight: 800, fontSize: '0.88rem', marginBottom: '8px' }}>
              <Scale size={18} />
              CRITICAL METHODOLOGICAL SEPARATION: NOMINAL FX vs. PURCHASING POWER PARITY (PPP)
            </div>
            <p style={{ fontSize: '0.84rem', color: '#CBD5E1', lineHeight: '1.6', margin: 0 }}>
              <strong>Nominal Currency Conversion</strong> uses market foreign exchange spot rates (e.g. $1 USD = ₹83.50 INR) to measure international currency exchange value and cross-border cash transfer worth. In contrast, <strong>Purchasing Power Parity (PPP)</strong> uses World Bank International Comparison Program (ICP) 2024 consumption price level factors (e.g. $1 Int$ = ₹23.80 INR) to reflect local purchasing power and living standards within domestic economies. These metrics serve fundamentally distinct analytical purposes and <em>must never be averaged, blended, or conflated</em>.
            </p>
          </div>

          {/* Loading or Error States */}
          {salaryLoading && (
            <div style={{ textAlign: 'center', padding: '60px 20px', color: '#94A3B8' }}>
              <div className="ji-spinner" style={{ margin: '0 auto 16px' }} />
              <p>Evaluating Cross-Market Salary Concordance & Comparability...</p>
            </div>
          )}

          {salaryError && (
            <div style={{ padding: '24px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid #EF4444', borderRadius: '12px', color: '#FCA5A5', marginBottom: '24px' }}>
              <AlertTriangle size={24} style={{ marginBottom: '8px' }} />
              <h4 style={{ margin: '0 0 6px 0', fontWeight: 800 }}>Salary Publication Gate / Query Notice</h4>
              <p style={{ margin: 0, fontSize: '0.88rem' }}>{salaryError}</p>
              {salarySourceId.startsWith('UK_') && (
                <div style={{ marginTop: '12px', fontSize: '0.82rem', color: '#F87171', background: 'rgba(0,0,0,0.3)', padding: '10px 14px', borderRadius: '8px' }}>
                  🔒 <strong>Governance Revocation Gate Enforced:</strong> Under ONS Open Government Licence v3.0 compliance rules, UK ASHE salary data is withheld pending affirmative publication authorization (Fail-Closed HTTP 503).
                </div>
              )}
            </div>
          )}

          {/* Source Profile Card */}
          {salaryProfile && (
            <div style={{ background: '#12141A', border: '1px solid rgba(255, 255, 255, 0.1)', borderRadius: '14px', padding: '24px', marginBottom: '28px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px', marginBottom: '16px' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                    <span style={{ fontSize: '1.4rem' }}>{MARKET_FLAGS[salaryProfile.market_id] || '🌐'}</span>
                    <span style={{ fontSize: '0.78rem', fontWeight: 800, color: '#94A3B8', textTransform: 'uppercase' }}>
                      SOURCE BENCHMARK · {salaryProfile.market_id}
                    </span>
                    <span style={{ fontSize: '0.72rem', padding: '2px 8px', borderRadius: '4px', background: 'rgba(255, 255, 255, 0.08)', color: '#A5B4FC' }}>
                      {salaryProfile.occupation_id}
                    </span>
                  </div>
                  <h3 style={{ fontSize: '1.45rem', fontWeight: 900, color: '#FFFFFF', margin: 0 }}>
                    {salaryProfile.occupation_title}
                  </h3>
                  {salaryProfile.source_meta && (
                    <div style={{ fontSize: '0.78rem', color: '#64748B', marginTop: '4px' }}>
                      Source: {salaryProfile.source_meta.authority} · {salaryProfile.source_meta.publication_name} ({salaryProfile.source_meta.reference_period}) · License: {salaryProfile.source_meta.license}
                    </div>
                  )}
                </div>

                {/* Badges */}
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.74rem', padding: '4px 10px', borderRadius: '6px', background: 'rgba(16, 185, 129, 0.15)', color: '#34D399', border: '1px solid rgba(16, 185, 129, 0.3)', fontWeight: 700 }}>
                    {salaryProfile.quality_flag}
                  </span>
                </div>
              </div>

              {/* 3 Metric Cards */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '14px', marginBottom: '20px' }}>
                <div style={{ background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '10px', padding: '16px' }}>
                  <div style={{ fontSize: '0.72rem', fontWeight: 800, color: '#94A3B8', textTransform: 'uppercase', marginBottom: '4px' }}>
                    Original Median ({salaryProfile.currency})
                  </div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 900, color: '#FFFFFF' }}>
                    {salaryProfile.currency === 'INR'
                      ? `₹${((salaryProfile.percentiles.p50 || 0) / 100000).toFixed(2)} Lakhs`
                      : salaryProfile.currency === 'GBP'
                      ? `£${salaryProfile.percentiles.p50?.toLocaleString()}`
                      : `$${salaryProfile.percentiles.p50?.toLocaleString()} ${salaryProfile.currency}`}
                  </div>
                  <div style={{ fontSize: '0.74rem', color: '#64748B', marginTop: '4px' }}>
                    {salaryProfile.source_meta?.pay_concept}
                  </div>
                </div>

                <div style={{ background: 'rgba(59, 130, 246, 0.06)', border: '1px solid rgba(59, 130, 246, 0.2)', borderRadius: '10px', padding: '16px' }}>
                  <div style={{ fontSize: '0.72rem', fontWeight: 800, color: '#93C5FD', textTransform: 'uppercase', marginBottom: '4px' }}>
                    Nominal USD Median (Market FX)
                  </div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 900, color: '#60A5FA' }}>
                    ${salaryProfile.nominal_usd_median?.toLocaleString()} USD
                  </div>
                  <div style={{ fontSize: '0.74rem', color: '#93C5FD', marginTop: '4px' }}>
                    Spot FX Conversion
                  </div>
                </div>

                <div style={{ background: 'rgba(16, 185, 129, 0.06)', border: '1px solid rgba(16, 185, 129, 0.2)', borderRadius: '10px', padding: '16px' }}>
                  <div style={{ fontSize: '0.72rem', fontWeight: 800, color: '#6EE7B7', textTransform: 'uppercase', marginBottom: '4px' }}>
                    PPP Int$ Median (World Bank ICP 2024)
                  </div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 900, color: '#34D399' }}>
                    ${salaryProfile.ppp_usd_median?.toLocaleString()} Int$
                  </div>
                  <div style={{ fontSize: '0.74rem', color: '#6EE7B7', marginTop: '4px' }}>
                    Domestic Purchasing Power Parity
                  </div>
                </div>
              </div>

              {/* Percentile Distribution Strip */}
              <div style={{ background: 'rgba(0, 0, 0, 0.2)', border: '1px solid rgba(255, 255, 255, 0.05)', borderRadius: '8px', padding: '14px 18px' }}>
                <div style={{ fontSize: '0.74rem', fontWeight: 800, color: '#94A3B8', textTransform: 'uppercase', marginBottom: '10px' }}>
                  Percentile Wage Distribution ({salaryProfile.currency})
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '10px', textAlign: 'center' }}>
                  {[
                    { label: 'p10 (10th)', val: salaryProfile.percentiles.p10 },
                    { label: 'p25 (25th)', val: salaryProfile.percentiles.p25 },
                    { label: 'p50 (Median)', val: salaryProfile.percentiles.p50, highlight: true },
                    { label: 'p75 (75th)', val: salaryProfile.percentiles.p75 },
                    { label: 'p90 (90th)', val: salaryProfile.percentiles.p90 },
                  ].map((pct, idx) => (
                    <div key={idx} style={{ background: pct.highlight ? 'rgba(16, 185, 129, 0.12)' : 'rgba(255, 255, 255, 0.03)', padding: '8px 4px', borderRadius: '6px' }}>
                      <div style={{ fontSize: '0.7rem', color: pct.highlight ? '#34D399' : '#94A3B8', fontWeight: 700 }}>{pct.label}</div>
                      <div style={{ fontSize: '0.88rem', fontWeight: 800, color: pct.highlight ? '#FFFFFF' : '#CBD5E1', marginTop: '2px' }}>
                        {pct.val !== null && pct.val !== undefined ? `${pct.val.toLocaleString()}` : 'N/A'}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Cross-Market Comparative Benchmarks */}
          {salaryComparison && salaryComparison.comparisons.length > 0 && (
            <div style={{ marginBottom: '36px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px' }}>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 900, color: '#FFFFFF', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <TrendingUp size={20} style={{ color: '#10B981' }} />
                  Cross-Market Comparative Salary Benchmarks ({salaryComparison.comparisons.length} Markets)
                </h3>
                <span style={{ fontSize: '0.78rem', color: '#94A3B8' }}>
                  Base: {salaryComparison.source_occupation_title} ({salaryComparison.source_market_id})
                </span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: '18px' }}>
                {salaryComparison.comparisons.map((comp, idx) => {
                  const verdictStyle = COMPARABILITY_VERDICT_COLORS[comp.comparability_verdict] || COMPARABILITY_VERDICT_COLORS.INSUFFICIENT_DATA;
                  return (
                    <div
                      key={idx}
                      style={{
                        background: '#12141A',
                        border: '1px solid rgba(255, 255, 255, 0.08)',
                        borderRadius: '14px',
                        padding: '20px',
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'space-between',
                      }}
                    >
                      <div>
                        {/* Header: Market Flag, Title, Code */}
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
                          <div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                              <span style={{ fontSize: '1.3rem' }}>{MARKET_FLAGS[comp.market_id] || '🌐'}</span>
                              <span style={{ fontSize: '0.8rem', fontWeight: 800, color: '#94A3B8' }}>
                                {comp.market_id}
                              </span>
                              <span style={{ fontSize: '0.72rem', color: '#A5B4FC', background: 'rgba(255, 255, 255, 0.06)', padding: '2px 7px', borderRadius: '4px' }}>
                                {comp.occupation_id}
                              </span>
                            </div>
                            <h4 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#FFFFFF', margin: '0 0 6px 0' }}>
                              {comp.occupation_title}
                            </h4>
                          </div>

                          {/* Relationship Badge */}
                          <span
                            style={{
                              fontSize: '0.72rem',
                              padding: '3px 8px',
                              borderRadius: '4px',
                              background: 'rgba(255, 255, 255, 0.06)',
                              color: '#CBD5E1',
                              fontWeight: 700,
                            }}
                          >
                            {comp.relationship_to_source}
                          </span>
                        </div>

                        {/* Comparability Verdict Badge */}
                        <div style={{ marginBottom: '16px' }}>
                          <span
                            style={{
                              fontSize: '0.76rem',
                              fontWeight: 800,
                              padding: '4px 10px',
                              borderRadius: '6px',
                              background: verdictStyle.bg,
                              color: verdictStyle.text,
                              border: `1px solid ${verdictStyle.border}`,
                              display: 'inline-block',
                            }}
                          >
                            {verdictStyle.label}
                          </span>
                        </div>

                        {/* If Suppressed (e.g. UK ASHE) */}
                        {comp.is_suppressed ? (
                          <div
                            style={{
                              background: 'rgba(239, 68, 68, 0.08)',
                              border: '1px solid rgba(239, 68, 68, 0.25)',
                              borderRadius: '8px',
                              padding: '14px',
                              marginBottom: '16px',
                              fontSize: '0.82rem',
                              color: '#FCA5A5',
                              lineHeight: '1.5',
                            }}
                          >
                            🔒 <strong>Data Withheld by Governance Gate:</strong> {comp.comparability_caveats[0] || 'UK ASHE salary analytics are not currently published due to active governance gate.'}
                          </div>
                        ) : (
                          <>
                            {/* Dual Metrics: Nominal USD vs PPP USD */}
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '14px' }}>
                              <div style={{ background: 'rgba(59, 130, 246, 0.06)', border: '1px solid rgba(59, 130, 246, 0.15)', borderRadius: '8px', padding: '12px' }}>
                                <div style={{ fontSize: '0.7rem', fontWeight: 800, color: '#93C5FD', textTransform: 'uppercase', marginBottom: '2px' }}>
                                  Nominal USD Median
                                </div>
                                <div style={{ fontSize: '1.3rem', fontWeight: 900, color: '#60A5FA' }}>
                                  ${comp.nominal_usd_median?.toLocaleString()} USD
                                </div>
                                <div style={{ fontSize: '0.72rem', color: '#94A3B8', marginTop: '2px' }}>
                                  Orig: {comp.original_currency === 'INR' ? `₹${((comp.original_median || 0) / 100000).toFixed(2)}L` : `${comp.original_median?.toLocaleString()} ${comp.original_currency}`}
                                </div>
                              </div>

                              <div style={{ background: 'rgba(16, 185, 129, 0.06)', border: '1px solid rgba(16, 185, 129, 0.15)', borderRadius: '8px', padding: '12px' }}>
                                <div style={{ fontSize: '0.7rem', fontWeight: 800, color: '#6EE7B7', textTransform: 'uppercase', marginBottom: '2px' }}>
                                  PPP Int$ Median
                                </div>
                                <div style={{ fontSize: '1.3rem', fontWeight: 900, color: '#34D399' }}>
                                  ${comp.ppp_usd_median?.toLocaleString()} Int$
                                </div>
                                <div style={{ fontSize: '0.72rem', color: '#6EE7B7', marginTop: '2px' }}>
                                  World Bank ICP 2024
                                </div>
                              </div>
                            </div>

                            {/* Percentiles Miniature */}
                            <div style={{ background: 'rgba(255, 255, 255, 0.02)', borderRadius: '6px', padding: '10px', marginBottom: '14px' }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.74rem', color: '#94A3B8', marginBottom: '4px' }}>
                                <span>p10: {comp.percentiles_original?.p10?.toLocaleString() || 'N/A'}</span>
                                <span>p50 (Med): {comp.percentiles_original?.p50?.toLocaleString() || 'N/A'}</span>
                                <span>p90: {comp.percentiles_original?.p90?.toLocaleString() || 'N/A'}</span>
                              </div>
                            </div>
                          </>
                        )}

                        {/* Methodological Caveats */}
                        {comp.comparability_caveats.length > 0 && !comp.is_suppressed && (
                          <div style={{ background: 'rgba(0, 0, 0, 0.3)', borderRadius: '8px', padding: '12px', fontSize: '0.78rem', color: '#CBD5E1' }}>
                            <div style={{ fontWeight: 800, color: '#FACC15', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                              <Info size={14} />
                              Comparability Dimensions & Limitations:
                            </div>
                            <ul style={{ margin: 0, paddingLeft: '18px', lineHeight: '1.5' }}>
                              {comp.comparability_caveats.map((cav, cIdx) => (
                                <li key={cIdx} style={{ marginBottom: '4px' }}>
                                  {cav}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>

                      <div style={{ borderTop: '1px solid rgba(255, 255, 255, 0.06)', paddingTop: '10px', marginTop: '14px', fontSize: '0.72rem', color: '#64748B', display: 'flex', justifyContent: 'space-between' }}>
                        <span>Source: {comp.source_id}</span>
                        <span>Flag: {comp.quality_flag}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Interactive Live Currency & PPP Converter Tool */}
          <div
            style={{
              background: '#12141A',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '14px',
              padding: '24px',
              marginBottom: '28px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '14px' }}>
              <Coins size={22} style={{ color: '#FACC15' }} />
              <div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 900, color: '#FFFFFF', margin: 0 }}>
                  Interactive FX vs. PPP Multiplier Calculator
                </h3>
                <span style={{ fontSize: '0.78rem', color: '#94A3B8' }}>
                  Live conversion illustrating the divergence between nominal financial transfers and domestic purchasing power.
                </span>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', alignItems: 'flex-end', marginBottom: '20px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.76rem', fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', marginBottom: '6px' }}>
                  Enter Amount:
                </label>
                <input
                  type="number"
                  value={calcAmount}
                  onChange={(e) => setCalcAmount(Number(e.target.value) || 0)}
                  style={{
                    width: '100%',
                    background: '#0B0D12',
                    border: '1px solid rgba(255, 255, 255, 0.15)',
                    borderRadius: '8px',
                    color: '#FFFFFF',
                    padding: '10px 14px',
                    fontSize: '1.05rem',
                    fontWeight: 700,
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.76rem', fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', marginBottom: '6px' }}>
                  Select Currency:
                </label>
                <select
                  value={calcCurrency}
                  onChange={(e) => setCalcCurrency(e.target.value)}
                  style={{
                    width: '100%',
                    background: '#0B0D12',
                    border: '1px solid rgba(255, 255, 255, 0.15)',
                    borderRadius: '8px',
                    color: '#FFFFFF',
                    padding: '10px 14px',
                    fontSize: '0.95rem',
                    fontWeight: 700,
                    cursor: 'pointer',
                  }}
                >
                  <option value="INR">🇮🇳 INR (Indian Rupee)</option>
                  <option value="GBP">🇬🇧 GBP (British Pound)</option>
                  <option value="AUD">🇦🇺 AUD (Australian Dollar)</option>
                  <option value="SGD">🇸🇬 SGD (Singapore Dollar)</option>
                  <option value="USD">🇺🇸 USD (US Dollar)</option>
                </select>
              </div>

              {calcResult && (
                <div style={{ display: 'flex', gap: '12px' }}>
                  <div style={{ flex: 1, background: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.25)', borderRadius: '8px', padding: '12px 16px' }}>
                    <div style={{ fontSize: '0.7rem', color: '#93C5FD', fontWeight: 800, textTransform: 'uppercase' }}>Nominal USD</div>
                    <div style={{ fontSize: '1.3rem', fontWeight: 900, color: '#60A5FA' }}>
                      ${calcResult.nominal_usd.toLocaleString()}
                    </div>
                  </div>

                  <div style={{ flex: 1, background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.25)', borderRadius: '8px', padding: '12px 16px' }}>
                    <div style={{ fontSize: '0.7rem', color: '#6EE7B7', fontWeight: 800, textTransform: 'uppercase' }}>PPP Int$</div>
                    <div style={{ fontSize: '1.3rem', fontWeight: 900, color: '#34D399' }}>
                      ${calcResult.ppp_usd.toLocaleString()}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {calcResult && calcResult.nominal_usd > 0 && (
              <div style={{ fontSize: '0.8rem', color: '#94A3B8', borderTop: '1px solid rgba(255, 255, 255, 0.06)', paddingTop: '12px' }}>
                💡 <strong>Purchasing Power Factor:</strong> Inside {calcCurrency}, the domestic consumption value is{' '}
                <span style={{ color: '#FACC15', fontWeight: 800 }}>
                  {(calcResult.ppp_usd / calcResult.nominal_usd).toFixed(2)}x
                </span>{' '}
                higher than its nominal foreign exchange conversion value on international markets.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
