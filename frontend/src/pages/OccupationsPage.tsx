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
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { PageHero } from '../components/PageHero';
import { api } from '../services/api';
import {
  ClassificationSystem,
  NationalOccupation,
  CanonicalOccupation,
  CrossMarketComparisonResult,
} from '../types';

type ActiveTab = 'concordance' | 'explorer' | 'canonical';

const MARKET_FLAGS: Record<string, string> = {
  UK: '🇬🇧',
  US: '🇺🇸',
  AU: '🇦🇺',
  SG: '🇸🇬',
  IN: '🇮🇳',
  INT: '🌐',
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

  // Initial Load: classifications and canonical concepts
  useEffect(() => {
    setLoading(true);
    Promise.all([api.getClassifications(), api.getCanonicalOccupations()])
      .then(([classData, canonicalData]) => {
        setClassifications(classData);
        setCanonicalList(canonicalData);
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

                          <div style={{ textAlign: 'right' }}>
                            <span
                              style={{
                                fontSize: '0.85rem',
                                fontWeight: 800,
                                padding: '3px 8px',
                                borderRadius: '6px',
                                background: Number(match.confidence_score) >= 0.95 ? 'rgba(34, 197, 94, 0.2)' : 'rgba(234, 179, 8, 0.2)',
                                color: Number(match.confidence_score) >= 0.95 ? '#4ADE80' : '#FACC15',
                              }}
                            >
                              {Math.round(Number(match.confidence_score) * 100)}% CONFIDENCE
                            </span>
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
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span style={{ fontSize: '0.78rem', fontWeight: 800, padding: '2px 8px', borderRadius: '4px', background: 'rgba(59, 130, 246, 0.15)', color: '#93C5FD' }}>
                      CODE {occ.occupation_code}
                    </span>
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
    </div>
  );
};
