import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Building2,
  Search,
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  HelpCircle,
  ExternalLink,
  RotateCcw,
  Info,
  Scale,
  Globe,
  MapPin,
  FileText,
  ChevronRight,
  ChevronLeft,
  X,
  Layers,
  Sparkles,
  ArrowRight,
  AlertCircle
} from 'lucide-react';
import { api } from '../services/api';
import {
  EmployerProfile,
  EmployerResolutionRequest,
  EmployerResolutionResponse,
  EntityMatchCandidate,
  ResolutionMatchType,
  EntityReviewStatus,
  EmployerCategory,
  EmployerVerificationStatus
} from '../types';

type EmployerTab = 'resolve' | 'registry' | 'standards';

const MARKET_METADATA: Record<string, { name: string; flag: string; authority: string; idType: string; placeholder: string; example: string }> = {
  IN: {
    name: 'India',
    flag: '🇮🇳',
    authority: 'MCA',
    idType: 'CIN (Corporate Identification Number)',
    placeholder: 'e.g. U72200KA1981PLC013115',
    example: 'U72200KA1981PLC013115'
  },
  US: {
    name: 'United States',
    flag: '🇺🇸',
    authority: 'SEC',
    idType: 'SEC CIK (Central Index Key)',
    placeholder: 'e.g. 0001018724 or CIK0001018724',
    example: '0001018724'
  },
  UK: {
    name: 'United Kingdom',
    flag: '🇬🇧',
    authority: 'COMPANIES_HOUSE',
    idType: 'Companies House CRN',
    placeholder: 'e.g. 02868397 or SC123456',
    example: '02868397'
  },
  AU: {
    name: 'Australia',
    flag: '🇦🇺',
    authority: 'ASIC',
    idType: 'ABN / ACN (11 digits / 9 digits)',
    placeholder: 'e.g. 33004085616',
    example: '33004085616'
  },
  SG: {
    name: 'Singapore',
    flag: '🇸🇬',
    authority: 'ACRA',
    idType: 'ACRA UEN (Unique Entity Number)',
    placeholder: 'e.g. 200812345M or T12LL1234A',
    example: '200812345M'
  }
};

const SAMPLE_QUERIES: { label: string; name: string; market: string; auth: string; id: string }[] = [
  { label: 'Infosys (IN / MCA)', name: 'Infosys Limited', market: 'IN', auth: 'MCA', id: 'L85110KA1981PLC013115' },
  { label: 'Google (US / SEC)', name: 'Google LLC', market: 'US', auth: 'SEC', id: '0001288776' },
  { label: 'Arm (UK / CRN)', name: 'Arm Limited', market: 'UK', auth: 'COMPANIES_HOUSE', id: '02557590' },
  { label: 'Atlassian (AU / ASIC)', name: 'Atlassian Pty Ltd', market: 'AU', auth: 'ASIC', id: '62102443916' },
  { label: 'Grab (SG / ACRA)', name: 'Grab Holdings', market: 'SG', auth: 'ACRA', id: '201812345M' }
];

export const EmployersPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<EmployerTab>('resolve');

  // Resolution Form States
  const [candidateName, setCandidateName] = useState<string>('');
  const [marketId, setMarketId] = useState<string>('');
  const [statutoryAuthority, setStatutoryAuthority] = useState<string>('');
  const [statutoryIdentifier, setStatutoryIdentifier] = useState<string>('');
  const [resolving, setResolving] = useState<boolean>(false);
  const [resolutionResult, setResolutionResult] = useState<EmployerResolutionResponse | null>(null);
  const [resolutionError, setResolutionError] = useState<string | null>(null);

  // Registry States
  const [employers, setEmployers] = useState<EmployerProfile[]>([]);
  const [registryLoading, setRegistryLoading] = useState<boolean>(false);
  const [registryError, setRegistryError] = useState<string | null>(null);
  const [registryPage, setRegistryPage] = useState<number>(0);
  const [registryMarketFilter, setRegistryMarketFilter] = useState<string>('ALL');
  const pageSize = 10;

  // Detail Modal State
  const [selectedEmployer, setSelectedEmployer] = useState<EmployerProfile | null>(null);
  const [detailLoading, setDetailLoading] = useState<boolean>(false);

  // Auto-set authority hint when market changes
  const handleMarketChange = (newMarket: string) => {
    setMarketId(newMarket);
    if (newMarket && MARKET_METADATA[newMarket]) {
      setStatutoryAuthority(MARKET_METADATA[newMarket].authority);
    } else {
      setStatutoryAuthority('');
    }
  };

  // Submit Resolution
  const handleResolve = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const trimmedName = candidateName.trim();
    if (!trimmedName) {
      setResolutionError('Company or employer candidate name is required.');
      return;
    }

    setResolving(true);
    setResolutionError(null);

    const payload: EmployerResolutionRequest = {
      candidate_name: trimmedName,
      market_id: marketId || null,
      statutory_identifier: statutoryIdentifier.trim() || null,
      statutory_authority: statutoryAuthority || null,
    };

    try {
      const res = await api.resolveEmployer(payload);
      setResolutionResult(res);
    } catch (err: any) {
      setResolutionError(err?.message || 'Failed to resolve employer identity. Check network connection.');
      setResolutionResult(null);
    } finally {
      setResolving(false);
    }
  };

  // Reset Search
  const handleReset = () => {
    setCandidateName('');
    setMarketId('');
    setStatutoryAuthority('');
    setStatutoryIdentifier('');
    setResolutionResult(null);
    setResolutionError(null);
  };

  // Apply Sample
  const handleApplySample = (sample: typeof SAMPLE_QUERIES[0]) => {
    setCandidateName(sample.name);
    setMarketId(sample.market);
    setStatutoryAuthority(sample.auth);
    setStatutoryIdentifier(sample.id);
    setResolutionResult(null);
    setResolutionError(null);
  };

  // Load Registry
  const loadRegistry = async (page: number) => {
    setRegistryLoading(true);
    setRegistryError(null);
    try {
      const data = await api.getEmployers({ limit: pageSize, offset: page * pageSize });
      setEmployers(data || []);
    } catch (err: any) {
      setRegistryError(err?.message || 'Failed to load employer registry.');
    } finally {
      setRegistryLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'registry') {
      loadRegistry(registryPage);
    }
  }, [activeTab, registryPage]);

  // Open detail view
  const handleViewEmployerDetail = async (companyId: string) => {
    setDetailLoading(true);
    try {
      const profile = await api.getEmployerDetail(companyId);
      setSelectedEmployer(profile);
    } catch (err) {
      // If fetching by ID fails, check if we already have it in employers list
      const existing = employers.find(e => e.company_id === companyId);
      if (existing) {
        setSelectedEmployer(existing);
      } else {
        alert(`Employer profile '${companyId}' details could not be retrieved from the server.`);
      }
    } finally {
      setDetailLoading(false);
    }
  };

  // Filtered employers
  const filteredEmployers = employers.filter(emp => {
    if (registryMarketFilter === 'ALL') return true;
    return emp.headquarters_country === registryMarketFilter || emp.operating_markets?.includes(registryMarketFilter);
  });

  return (
    <div style={{ color: '#E2E8F0', paddingBottom: '60px' }}>
      {/* 1. Header & Context */}
      <section style={{ marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
          <div
            style={{
              width: '40px',
              height: '40px',
              borderRadius: '12px',
              background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.25) 0%, rgba(99, 102, 241, 0.25) 100%)',
              border: '1px solid rgba(139, 92, 246, 0.4)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 24px rgba(139, 92, 246, 0.35)',
            }}
          >
            <Building2 size={22} color="#A78BFA" />
          </div>
          <div>
            <h1 style={{ fontSize: '2rem', fontWeight: 800, margin: 0, color: '#FFFFFF', letterSpacing: '-0.02em' }}>
              Employer Intelligence
            </h1>
            <p style={{ margin: 0, fontSize: '0.95rem', color: '#94A3B8' }}>
              Explore employer identities, legal entities, organizational relationships, and evidence-backed company intelligence across global markets.
            </p>
          </div>
        </div>

        {/* Market Jurisdiction Badges */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '16px' }}>
          {Object.entries(MARKET_METADATA).map(([code, meta]) => (
            <span
              key={code}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                padding: '4px 10px',
                borderRadius: '8px',
                fontSize: '0.8rem',
                background: 'rgba(255, 255, 255, 0.04)',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                color: '#CBD5E1',
              }}
            >
              <span>{meta.flag}</span>
              <strong style={{ color: '#F1F5F9' }}>{meta.name}</strong>
              <span style={{ color: '#64748B' }}>({meta.authority})</span>
            </span>
          ))}
        </div>
      </section>

      {/* 2. Core Governance Principle Card */}
      <div
        style={{
          background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.4) 0%, rgba(15, 23, 42, 0.6) 100%)',
          border: '1px solid rgba(139, 92, 246, 0.2)',
          borderRadius: '12px',
          padding: '16px 20px',
          marginBottom: '28px',
          display: 'flex',
          alignItems: 'flex-start',
          gap: '14px',
        }}
      >
        <Scale size={20} color="#A78BFA" style={{ flexShrink: 0, marginTop: '2px' }} />
        <div style={{ fontSize: '0.88rem', lineHeight: '1.5', color: '#CBD5E1' }}>
          <strong style={{ color: '#F8FAFC' }}>JOBINTEL Legal Identity Standard: </strong>
          Corporate brands, operating subsidiaries, and parent corporations are distinct legal entities. A common trading name or brand does not constitute evidence of legal unity. Automatic resolution is granted only when exact statutory identifiers align without sovereign jurisdiction conflicts or duplicate registry collisions.
        </div>
      </div>

      {/* 3. Navigation Tabs */}
      <div
        style={{
          display: 'flex',
          gap: '8px',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
          marginBottom: '24px',
          paddingBottom: '2px',
        }}
      >
        <button
          onClick={() => setActiveTab('resolve')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '10px 18px',
            borderRadius: '8px 8px 0 0',
            background: activeTab === 'resolve' ? 'rgba(139, 92, 246, 0.15)' : 'transparent',
            border: 'none',
            borderBottom: activeTab === 'resolve' ? '2px solid #8B5CF6' : '2px solid transparent',
            color: activeTab === 'resolve' ? '#FFFFFF' : '#94A3B8',
            fontWeight: 600,
            fontSize: '0.9rem',
            cursor: 'pointer',
            transition: 'all 0.15s ease',
          }}
        >
          <Search size={16} />
          Entity Resolution & Verification
        </button>

        <button
          onClick={() => setActiveTab('registry')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '10px 18px',
            borderRadius: '8px 8px 0 0',
            background: activeTab === 'registry' ? 'rgba(139, 92, 246, 0.15)' : 'transparent',
            border: 'none',
            borderBottom: activeTab === 'registry' ? '2px solid #8B5CF6' : '2px solid transparent',
            color: activeTab === 'registry' ? '#FFFFFF' : '#94A3B8',
            fontWeight: 600,
            fontSize: '0.9rem',
            cursor: 'pointer',
            transition: 'all 0.15s ease',
          }}
        >
          <Building2 size={16} />
          Employer Registry Explorer
        </button>

        <button
          onClick={() => setActiveTab('standards')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '10px 18px',
            borderRadius: '8px 8px 0 0',
            background: activeTab === 'standards' ? 'rgba(139, 92, 246, 0.15)' : 'transparent',
            border: 'none',
            borderBottom: activeTab === 'standards' ? '2px solid #8B5CF6' : '2px solid transparent',
            color: activeTab === 'standards' ? '#FFFFFF' : '#94A3B8',
            fontWeight: 600,
            fontSize: '0.9rem',
            cursor: 'pointer',
            transition: 'all 0.15s ease',
          }}
        >
          <ShieldCheck size={16} />
          Statutory Standards & Governance
        </button>
      </div>

      {/* ==================================================================== */}
      {/* TAB 1: ENTITY RESOLUTION & VERIFICATION                              */}
      {/* ==================================================================== */}
      {activeTab === 'resolve' && (
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.2 }}>
          {/* Search Form Card */}
          <div
            style={{
              background: 'rgba(15, 23, 42, 0.65)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '14px',
              padding: '24px',
              marginBottom: '28px',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px' }}>
              <div>
                <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: 0, color: '#F8FAFC' }}>
                  Resolve Corporate Legal Entity
                </h2>
                <p style={{ margin: '4px 0 0 0', fontSize: '0.85rem', color: '#94A3B8' }}>
                  Submit candidate identity attributes to query authoritative statutory registers.
                </p>
              </div>

              {/* Sample Queries */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
                <span style={{ fontSize: '0.78rem', color: '#64748B', fontWeight: 500 }}>Presets:</span>
                {SAMPLE_QUERIES.map((sample, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleApplySample(sample)}
                    style={{
                      background: 'rgba(255, 255, 255, 0.04)',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      borderRadius: '6px',
                      padding: '3px 8px',
                      fontSize: '0.75rem',
                      color: '#94A3B8',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.color = '#FFFFFF';
                      e.currentTarget.style.borderColor = '#8B5CF6';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.color = '#94A3B8';
                      e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
                    }}
                  >
                    {sample.label}
                  </button>
                ))}
              </div>
            </div>

            <form onSubmit={handleResolve}>
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
                  gap: '16px',
                  marginBottom: '20px',
                }}
              >
                {/* 1. Candidate Company Name (Required) */}
                <div style={{ gridColumn: 'span 2' }}>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#CBD5E1', marginBottom: '6px' }}>
                    Candidate Employer / Entity Name <span style={{ color: '#F43F5E' }}>*</span>
                  </label>
                  <input
                    type="text"
                    value={candidateName}
                    onChange={(e) => setCandidateName(e.target.value)}
                    placeholder="e.g. Google LLC, Infosys Limited, Arm Limited..."
                    required
                    style={{
                      width: '100%',
                      background: 'rgba(8, 9, 13, 0.8)',
                      border: '1px solid rgba(255, 255, 255, 0.12)',
                      borderRadius: '8px',
                      padding: '10px 14px',
                      color: '#FFFFFF',
                      fontSize: '0.92rem',
                      outline: 'none',
                      transition: 'border 0.2s',
                    }}
                    onFocus={(e) => (e.target.style.borderColor = '#8B5CF6')}
                    onBlur={(e) => (e.target.style.borderColor = 'rgba(255, 255, 255, 0.12)')}
                  />
                </div>

                {/* 2. Target Market / Jurisdiction */}
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#CBD5E1', marginBottom: '6px' }}>
                    Target Sovereign Market
                  </label>
                  <select
                    value={marketId}
                    onChange={(e) => handleMarketChange(e.target.value)}
                    style={{
                      width: '100%',
                      background: 'rgba(8, 9, 13, 0.8)',
                      border: '1px solid rgba(255, 255, 255, 0.12)',
                      borderRadius: '8px',
                      padding: '10px 14px',
                      color: '#FFFFFF',
                      fontSize: '0.92rem',
                      outline: 'none',
                    }}
                  >
                    <option value="">All Supported Markets (Cross-Border)</option>
                    <option value="IN">🇮🇳 India (IN)</option>
                    <option value="US">🇺🇸 United States (US)</option>
                    <option value="UK">🇬🇧 United Kingdom (UK)</option>
                    <option value="AU">🇦🇺 Australia (AU)</option>
                    <option value="SG">🇸🇬 Singapore (SG)</option>
                  </select>
                </div>

                {/* 3. Statutory Authority */}
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#CBD5E1', marginBottom: '6px' }}>
                    Statutory Authority
                  </label>
                  <select
                    value={statutoryAuthority}
                    onChange={(e) => setStatutoryAuthority(e.target.value)}
                    style={{
                      width: '100%',
                      background: 'rgba(8, 9, 13, 0.8)',
                      border: '1px solid rgba(255, 255, 255, 0.12)',
                      borderRadius: '8px',
                      padding: '10px 14px',
                      color: '#FFFFFF',
                      fontSize: '0.92rem',
                      outline: 'none',
                    }}
                  >
                    <option value="">Auto-Detect from Market / Identifier</option>
                    <option value="MCA">MCA (India Ministry of Corporate Affairs)</option>
                    <option value="SEC">SEC / EDGAR (US Securities & Exchange Commission)</option>
                    <option value="COMPANIES_HOUSE">Companies House (United Kingdom)</option>
                    <option value="ASIC">ASIC / ABR (Australian Business Register)</option>
                    <option value="ACRA">ACRA (Singapore Accounting & Regulatory Authority)</option>
                  </select>
                </div>

                {/* 4. Statutory Identifier (Optional) */}
                <div style={{ gridColumn: 'span 2' }}>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#CBD5E1', marginBottom: '6px' }}>
                    Statutory Registration Identifier <span style={{ color: '#64748B', fontWeight: 400 }}>(Optional - CIN, CIK, CRN, ABN, UEN)</span>
                  </label>
                  <input
                    type="text"
                    value={statutoryIdentifier}
                    onChange={(e) => setStatutoryIdentifier(e.target.value)}
                    placeholder={marketId && MARKET_METADATA[marketId] ? MARKET_METADATA[marketId].placeholder : 'e.g. CIK0001018724, CRN 02868397, ABN 33004085616...'}
                    style={{
                      width: '100%',
                      background: 'rgba(8, 9, 13, 0.8)',
                      border: '1px solid rgba(255, 255, 255, 0.12)',
                      borderRadius: '8px',
                      padding: '10px 14px',
                      color: '#FFFFFF',
                      fontSize: '0.92rem',
                      outline: 'none',
                    }}
                  />
                  <div style={{ fontSize: '0.78rem', color: '#64748B', marginTop: '4px' }}>
                    Providing an authoritative registration number allows exact sovereign identity verification without heuristic guesswork.
                  </div>
                </div>
              </div>

              {/* Submit & Reset Buttons */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <button
                  type="submit"
                  disabled={resolving || !candidateName.trim()}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '8px',
                    background: resolving || !candidateName.trim() ? 'rgba(139, 92, 246, 0.3)' : 'linear-gradient(135deg, #8B5CF6 0%, #6366F1 100%)',
                    border: 'none',
                    borderRadius: '8px',
                    padding: '10px 22px',
                    color: '#FFFFFF',
                    fontSize: '0.92rem',
                    fontWeight: 600,
                    cursor: resolving || !candidateName.trim() ? 'not-allowed' : 'pointer',
                    boxShadow: resolving || !candidateName.trim() ? 'none' : '0 0 20px rgba(139, 92, 246, 0.4)',
                    transition: 'all 0.2s',
                  }}
                >
                  {resolving ? (
                    <>
                      <RotateCcw size={16} className="animate-spin" />
                      Scanning Corporate Registries...
                    </>
                  ) : (
                    <>
                      <Search size={16} />
                      Resolve Legal Entity
                    </>
                  )}
                </button>

                <button
                  type="button"
                  onClick={handleReset}
                  style={{
                    background: 'transparent',
                    border: '1px solid rgba(255, 255, 255, 0.12)',
                    borderRadius: '8px',
                    padding: '10px 18px',
                    color: '#94A3B8',
                    fontSize: '0.9rem',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.color = '#FFFFFF')}
                  onMouseLeave={(e) => (e.currentTarget.style.color = '#94A3B8')}
                >
                  Clear Form
                </button>
              </div>
            </form>
          </div>

          {/* Error Message */}
          {resolutionError && (
            <div
              style={{
                background: 'rgba(244, 63, 94, 0.1)',
                border: '1px solid rgba(244, 63, 94, 0.3)',
                borderRadius: '10px',
                padding: '14px 18px',
                marginBottom: '24px',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                color: '#FECDD3',
                fontSize: '0.9rem',
              }}
            >
              <AlertCircle size={18} color="#F43F5E" />
              <span>{resolutionError}</span>
            </div>
          )}

          {/* ================================================================ */}
          {/* RESOLUTION RESULT DISPLAY                                        */}
          {/* ================================================================ */}
          {resolutionResult && (
            <motion.div
              initial={{ opacity: 0, scale: 0.99 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.25 }}
              style={{
                background: 'rgba(15, 23, 42, 0.75)',
                border:
                  resolutionResult.review_status === 'AUTOMATICALLY_RESOLVED'
                    ? '1px solid rgba(16, 185, 129, 0.4)'
                    : resolutionResult.review_status === 'MANUAL_REVIEW_REQUIRED'
                    ? '1px solid rgba(245, 158, 11, 0.4)'
                    : '1px solid rgba(148, 163, 184, 0.3)',
                borderRadius: '14px',
                padding: '24px',
                marginBottom: '28px',
                boxShadow: '0 12px 40px rgba(0, 0, 0, 0.4)',
              }}
            >
              {/* Result Header & Status Banner */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px', marginBottom: '20px' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
                    <h3 style={{ fontSize: '1.25rem', fontWeight: 700, margin: 0, color: '#F8FAFC' }}>
                      Resolution Verdict for "{resolutionResult.query_name}"
                    </h3>
                    {resolutionResult.query_market_id && (
                      <span
                        style={{
                          background: 'rgba(255, 255, 255, 0.08)',
                          padding: '2px 8px',
                          borderRadius: '6px',
                          fontSize: '0.8rem',
                          color: '#CBD5E1',
                        }}
                      >
                        Market: {resolutionResult.query_market_id}
                      </span>
                    )}
                  </div>
                  <div style={{ fontSize: '0.85rem', color: '#94A3B8' }}>
                    Query evaluated against registered sovereign corporate entities.
                  </div>
                </div>

                {/* Outcome Status Badge */}
                <div>
                  {resolutionResult.review_status === 'AUTOMATICALLY_RESOLVED' && (
                    <span
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '6px',
                        background: 'rgba(16, 185, 129, 0.15)',
                        border: '1px solid rgba(16, 185, 129, 0.4)',
                        color: '#34D399',
                        padding: '6px 14px',
                        borderRadius: '20px',
                        fontSize: '0.85rem',
                        fontWeight: 700,
                      }}
                    >
                      <CheckCircle2 size={16} />
                      AUTOMATICALLY RESOLVED
                    </span>
                  )}

                  {resolutionResult.review_status === 'MANUAL_REVIEW_REQUIRED' && (
                    <span
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '6px',
                        background: 'rgba(245, 158, 11, 0.15)',
                        border: '1px solid rgba(245, 158, 11, 0.4)',
                        color: '#FBBF24',
                        padding: '6px 14px',
                        borderRadius: '20px',
                        fontSize: '0.85rem',
                        fontWeight: 700,
                      }}
                    >
                      <AlertTriangle size={16} />
                      MANUAL REVIEW REQUIRED
                    </span>
                  )}

                  {resolutionResult.review_status === 'CONFIRMED_DISTINCT' && (
                    <span
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '6px',
                        background: 'rgba(148, 163, 184, 0.15)',
                        border: '1px solid rgba(148, 163, 184, 0.4)',
                        color: '#94A3B8',
                        padding: '6px 14px',
                        borderRadius: '20px',
                        fontSize: '0.85rem',
                        fontWeight: 700,
                      }}
                    >
                      <XCircle size={16} />
                      CONFIRMED DISTINCT (NO MATCH)
                    </span>
                  )}
                </div>
              </div>

              {/* Governance Caveat Notice */}
              <div
                style={{
                  background: 'rgba(8, 9, 13, 0.7)',
                  borderLeft: '3px solid #8B5CF6',
                  borderRadius: '0 8px 8px 0',
                  padding: '10px 14px',
                  marginBottom: '20px',
                  fontSize: '0.84rem',
                  color: '#CBD5E1',
                  lineHeight: '1.45',
                }}
              >
                <strong style={{ color: '#A78BFA' }}>Governance Policy: </strong>
                {resolutionResult.governance_caveat}
              </div>

              {/* Resolution Metadata Cards */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                  gap: '12px',
                  marginBottom: '24px',
                }}
              >
                <div style={{ background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.06)', borderRadius: '8px', padding: '12px' }}>
                  <div style={{ fontSize: '0.75rem', color: '#64748B', textTransform: 'uppercase', fontWeight: 600 }}>Match Classification</div>
                  <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#F1F5F9', marginTop: '4px' }}>
                    {resolutionResult.resolution_match_type}
                  </div>
                </div>

                <div style={{ background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.06)', borderRadius: '8px', padding: '12px' }}>
                  <div style={{ fontSize: '0.75rem', color: '#64748B', textTransform: 'uppercase', fontWeight: 600 }}>Resolved Entity ID</div>
                  <div style={{ fontSize: '0.95rem', fontWeight: 700, marginTop: '4px', color: resolutionResult.resolved_company_id ? '#34D399' : '#94A3B8' }}>
                    {resolutionResult.resolved_company_id || 'None (Unresolved)'}
                  </div>
                </div>

                <div style={{ background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.06)', borderRadius: '8px', padding: '12px' }}>
                  <div style={{ fontSize: '0.75rem', color: '#64748B', textTransform: 'uppercase', fontWeight: 600 }}>Entity Candidates Evaluated</div>
                  <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#F1F5F9', marginTop: '4px' }}>
                    {resolutionResult.candidates ? resolutionResult.candidates.length : 0} Candidates
                  </div>
                </div>
              </div>

              {/* Candidate Entities Breakdown */}
              {resolutionResult.candidates && resolutionResult.candidates.length > 0 ? (
                <div>
                  <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#F8FAFC', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Layers size={18} color="#A78BFA" />
                    Candidate Entity Evaluation & Evidence Details
                  </h4>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {resolutionResult.candidates.map((cand, idx) => (
                      <div
                        key={idx}
                        style={{
                          background: 'rgba(8, 9, 13, 0.65)',
                          border: '1px solid rgba(255, 255, 255, 0.08)',
                          borderRadius: '10px',
                          padding: '16px',
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '10px', marginBottom: '10px' }}>
                          <div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                              <span style={{ fontSize: '1rem', fontWeight: 700, color: '#FFFFFF' }}>
                                {cand.target_company_name}
                              </span>
                              <span
                                style={{
                                  background: 'rgba(255, 255, 255, 0.06)',
                                  borderRadius: '4px',
                                  padding: '2px 6px',
                                  fontSize: '0.75rem',
                                  color: '#94A3B8',
                                  fontFamily: 'monospace',
                                }}
                              >
                                {cand.target_company_id}
                              </span>
                              <span style={{ fontSize: '0.8rem', color: '#CBD5E1' }}>
                                {MARKET_METADATA[cand.target_market_id]?.flag} {cand.target_market_id}
                              </span>
                            </div>

                            {/* Badges */}
                            <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginTop: '6px' }}>
                              <span
                                style={{
                                  background: 'rgba(139, 92, 246, 0.15)',
                                  border: '1px solid rgba(139, 92, 246, 0.3)',
                                  borderRadius: '4px',
                                  padding: '2px 6px',
                                  fontSize: '0.72rem',
                                  color: '#C4B5FD',
                                  fontWeight: 600,
                                }}
                              >
                                {cand.match_type}
                              </span>

                              {cand.shared_brand_detected && (
                                <span
                                  style={{
                                    background: 'rgba(245, 158, 11, 0.15)',
                                    border: '1px solid rgba(245, 158, 11, 0.3)',
                                    borderRadius: '4px',
                                    padding: '2px 6px',
                                    fontSize: '0.72rem',
                                    color: '#FCD34D',
                                    fontWeight: 600,
                                  }}
                                >
                                  Shared Brand Detected
                                </span>
                              )}

                              {cand.is_subsidiary_relationship && (
                                <span
                                  style={{
                                    background: 'rgba(236, 72, 153, 0.15)',
                                    border: '1px solid rgba(236, 72, 153, 0.3)',
                                    borderRadius: '4px',
                                    padding: '2px 6px',
                                    fontSize: '0.72rem',
                                    color: '#F472B6',
                                    fontWeight: 600,
                                  }}
                                >
                                  Subsidiary Distinction
                                </span>
                              )}

                              {cand.requires_human_approval && (
                                <span
                                  style={{
                                    background: 'rgba(244, 63, 94, 0.15)',
                                    border: '1px solid rgba(244, 63, 94, 0.3)',
                                    borderRadius: '4px',
                                    padding: '2px 6px',
                                    fontSize: '0.72rem',
                                    color: '#FDA4AF',
                                    fontWeight: 600,
                                  }}
                                >
                                  Human Approval Required
                                </span>
                              )}
                            </div>
                          </div>

                          {/* Matching Score (Labeled with Disclaimer) */}
                          <div style={{ textAlign: 'right' }}>
                            <div style={{ fontSize: '0.75rem', color: '#94A3B8', textTransform: 'uppercase' }}>Normalized Matching Score</div>
                            <div style={{ fontSize: '1.15rem', fontWeight: 800, color: '#A78BFA' }}>
                              {(cand.similarity_score * 100).toFixed(1)}%
                            </div>
                            <div style={{ fontSize: '0.7rem', color: '#64748B' }}>
                              Lexical similarity score; not a calibrated probability.
                            </div>
                          </div>
                        </div>

                        {/* Evidence Summary */}
                        <div
                          style={{
                            background: 'rgba(255, 255, 255, 0.02)',
                            borderRadius: '6px',
                            padding: '10px 12px',
                            fontSize: '0.84rem',
                            color: '#CBD5E1',
                            lineHeight: '1.45',
                            marginTop: '8px',
                          }}
                        >
                          <strong style={{ color: '#E2E8F0' }}>Evidence Summary: </strong>
                          {cand.evidence_summary}
                        </div>

                        {/* Action Link to Profile */}
                        <div style={{ marginTop: '10px', display: 'flex', justifyContent: 'flex-end' }}>
                          <button
                            type="button"
                            onClick={() => handleViewEmployerDetail(cand.target_company_id)}
                            style={{
                              background: 'transparent',
                              border: 'none',
                              color: '#8B5CF6',
                              fontSize: '0.82rem',
                              fontWeight: 600,
                              cursor: 'pointer',
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '4px',
                              padding: 0,
                            }}
                          >
                            View Registered Profile <ChevronRight size={14} />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div
                  style={{
                    background: 'rgba(8, 9, 13, 0.5)',
                    borderRadius: '8px',
                    padding: '20px',
                    textAlign: 'center',
                    color: '#94A3B8',
                    fontSize: '0.88rem',
                  }}
                >
                  <Info size={24} color="#64748B" style={{ margin: '0 auto 8px auto', display: 'block' }} />
                  No candidate corporate entities matched this query. The submitted organization was classified as confirmed distinct from all registered employers.
                </div>
              )}
            </motion.div>
          )}
        </motion.div>
      )}

      {/* ==================================================================== */}
      {/* TAB 2: EMPLOYER REGISTRY EXPLORER                                    */}
      {/* ==================================================================== */}
      {activeTab === 'registry' && (
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.2 }}>
          <div
            style={{
              background: 'rgba(15, 23, 42, 0.65)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '14px',
              padding: '24px',
              marginBottom: '28px',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px', marginBottom: '20px' }}>
              <div>
                <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: 0, color: '#F8FAFC' }}>
                  Registered Corporate Employers
                </h2>
                <p style={{ margin: '4px 0 0 0', fontSize: '0.85rem', color: '#94A3B8' }}>
                  Browse verified corporate entities registered in the JOBINTEL sovereign registry.
                </p>
              </div>

              {/* Market Filter */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '0.85rem', color: '#94A3B8' }}>Filter by HQ:</span>
                <select
                  value={registryMarketFilter}
                  onChange={(e) => setRegistryMarketFilter(e.target.value)}
                  style={{
                    background: 'rgba(8, 9, 13, 0.8)',
                    border: '1px solid rgba(255, 255, 255, 0.12)',
                    borderRadius: '8px',
                    padding: '6px 12px',
                    color: '#FFFFFF',
                    fontSize: '0.85rem',
                    outline: 'none',
                  }}
                >
                  <option value="ALL">All Jurisdictions</option>
                  <option value="IN">🇮🇳 India (IN)</option>
                  <option value="US">🇺🇸 United States (US)</option>
                  <option value="UK">🇬🇧 United Kingdom (UK)</option>
                  <option value="AU">🇦🇺 Australia (AU)</option>
                  <option value="SG">🇸🇬 Singapore (SG)</option>
                </select>
              </div>
            </div>

            {/* Registry Content */}
            {registryLoading ? (
              <div style={{ textAlign: 'center', padding: '48px 0', color: '#94A3B8' }}>
                <RotateCcw size={28} className="animate-spin" style={{ margin: '0 auto 12px auto', display: 'block', color: '#8B5CF6' }} />
                <span>Loading registered employers from cloud registry...</span>
              </div>
            ) : registryError ? (
              <div
                style={{
                  background: 'rgba(244, 63, 94, 0.1)',
                  border: '1px solid rgba(244, 63, 94, 0.3)',
                  borderRadius: '10px',
                  padding: '20px',
                  textAlign: 'center',
                  color: '#FECDD3',
                }}
              >
                <AlertCircle size={24} color="#F43F5E" style={{ margin: '0 auto 8px auto', display: 'block' }} />
                <p style={{ margin: '0 0 12px 0' }}>{registryError}</p>
                <button
                  onClick={() => loadRegistry(registryPage)}
                  style={{
                    background: 'rgba(255, 255, 255, 0.1)',
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    borderRadius: '6px',
                    padding: '6px 14px',
                    color: '#FFFFFF',
                    fontSize: '0.82rem',
                    cursor: 'pointer',
                  }}
                >
                  Retry Request
                </button>
              </div>
            ) : filteredEmployers.length === 0 ? (
              <div
                style={{
                  background: 'rgba(8, 9, 13, 0.5)',
                  border: '1px dashed rgba(255, 255, 255, 0.12)',
                  borderRadius: '10px',
                  padding: '40px 24px',
                  textAlign: 'center',
                }}
              >
                <Building2 size={36} color="#64748B" style={{ margin: '0 auto 12px auto', display: 'block' }} />
                <h4 style={{ fontSize: '1rem', fontWeight: 600, color: '#F1F5F9', margin: '0 0 6px 0' }}>
                  No Employer Records In Registry
                </h4>
                <p style={{ fontSize: '0.85rem', color: '#94A3B8', maxWidth: '520px', margin: '0 auto', lineHeight: '1.5' }}>
                  The active staging environment currently contains 0 pre-seeded baseline employers in cloud container storage. Use the <strong>Entity Resolution</strong> tab to verify statutory identifiers live against authoritative sovereign registries.
                </p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {filteredEmployers.map((emp) => (
                  <div
                    key={emp.company_id}
                    style={{
                      background: 'rgba(8, 9, 13, 0.7)',
                      border: '1px solid rgba(255, 255, 255, 0.08)',
                      borderRadius: '10px',
                      padding: '16px 20px',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      flexWrap: 'wrap',
                      gap: '12px',
                    }}
                  >
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontSize: '1.05rem', fontWeight: 700, color: '#FFFFFF' }}>
                          {emp.company_name}
                        </span>
                        <span style={{ fontSize: '0.8rem', color: '#94A3B8' }}>
                          {MARKET_METADATA[emp.headquarters_country]?.flag} {emp.headquarters_country}
                        </span>
                      </div>
                      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginTop: '6px' }}>
                        <span style={{ fontSize: '0.75rem', color: '#A78BFA', background: 'rgba(139, 92, 246, 0.1)', padding: '2px 8px', borderRadius: '4px' }}>
                          {emp.company_category}
                        </span>
                        {emp.industry && (
                          <span style={{ fontSize: '0.75rem', color: '#94A3B8', background: 'rgba(255, 255, 255, 0.05)', padding: '2px 8px', borderRadius: '4px' }}>
                            {emp.industry}
                          </span>
                        )}
                      </div>
                    </div>

                    <button
                      onClick={() => setSelectedEmployer(emp)}
                      style={{
                        background: 'rgba(139, 92, 246, 0.15)',
                        border: '1px solid rgba(139, 92, 246, 0.3)',
                        borderRadius: '6px',
                        padding: '6px 14px',
                        color: '#C4B5FD',
                        fontSize: '0.85rem',
                        fontWeight: 600,
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                      }}
                    >
                      View Profile <ChevronRight size={14} />
                    </button>
                  </div>
                ))}

                {/* Pagination Controls */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '16px', paddingTop: '16px', borderTop: '1px solid rgba(255, 255, 255, 0.08)' }}>
                  <button
                    disabled={registryPage === 0}
                    onClick={() => setRegistryPage((p) => Math.max(0, p - 1))}
                    style={{
                      background: 'rgba(255, 255, 255, 0.05)',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      borderRadius: '6px',
                      padding: '6px 14px',
                      color: registryPage === 0 ? '#64748B' : '#FFFFFF',
                      fontSize: '0.85rem',
                      cursor: registryPage === 0 ? 'not-allowed' : 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                    }}
                  >
                    <ChevronLeft size={14} /> Previous
                  </button>

                  <span style={{ fontSize: '0.85rem', color: '#94A3B8' }}>
                    Page {registryPage + 1}
                  </span>

                  <button
                    disabled={employers.length < pageSize}
                    onClick={() => setRegistryPage((p) => p + 1)}
                    style={{
                      background: 'rgba(255, 255, 255, 0.05)',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      borderRadius: '6px',
                      padding: '6px 14px',
                      color: employers.length < pageSize ? '#64748B' : '#FFFFFF',
                      fontSize: '0.85rem',
                      cursor: employers.length < pageSize ? 'not-allowed' : 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                    }}
                  >
                    Next <ChevronRight size={14} />
                  </button>
                </div>
              </div>
            )}
          </div>
        </motion.div>
      )}

      {/* ==================================================================== */}
      {/* TAB 3: STATUTORY STANDARDS & GOVERNANCE                               */}
      {/* ==================================================================== */}
      {activeTab === 'standards' && (
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.2 }}>
          <div
            style={{
              background: 'rgba(15, 23, 42, 0.65)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '14px',
              padding: '28px',
              marginBottom: '28px',
            }}
          >
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: '0 0 8px 0', color: '#F8FAFC' }}>
              Sovereign Statutory Registers & Entity Governance
            </h2>
            <p style={{ margin: '0 0 24px 0', fontSize: '0.88rem', color: '#94A3B8', lineHeight: '1.5' }}>
              JOBINTEL enforces deterministic, evidence-backed corporate entity resolution. Unlike naive string-matching or heuristics, statutory identifiers are evaluated under strict rules of sovereign jurisdiction and corporate law.
            </p>

            {/* Standards Table */}
            <div style={{ overflowX: 'auto', marginBottom: '28px' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.12)', textAlign: 'left', color: '#94A3B8' }}>
                    <th style={{ padding: '10px 12px' }}>Jurisdiction</th>
                    <th style={{ padding: '10px 12px' }}>Statutory Authority</th>
                    <th style={{ padding: '10px 12px' }}>Identifier Format</th>
                    <th style={{ padding: '10px 12px' }}>Validation & Collision Defense</th>
                  </tr>
                </thead>
                <tbody>
                  <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.06)' }}>
                    <td style={{ padding: '12px' }}>🇮🇳 India (IN)</td>
                    <td style={{ padding: '12px', fontWeight: 600, color: '#F1F5F9' }}>Ministry of Corporate Affairs (MCA) / ROC</td>
                    <td style={{ padding: '12px', fontFamily: 'monospace', color: '#A78BFA' }}>21-character CIN</td>
                    <td style={{ padding: '12px', color: '#CBD5E1' }}>Exact syntax match (L/U + digits + state + year + entity + digits). Cross-border matches require manual review.</td>
                  </tr>
                  <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.06)' }}>
                    <td style={{ padding: '12px' }}>🇺🇸 United States (US)</td>
                    <td style={{ padding: '12px', fontWeight: 600, color: '#F1F5F9' }}>Securities and Exchange Commission (SEC / EDGAR)</td>
                    <td style={{ padding: '12px', fontFamily: 'monospace', color: '#A78BFA' }}>10-digit CIK (Zero-padded)</td>
                    <td style={{ padding: '12px', color: '#CBD5E1' }}>Zero-padded normalization (0001018724). Must align with US sovereign jurisdiction.</td>
                  </tr>
                  <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.06)' }}>
                    <td style={{ padding: '12px' }}>🇬🇧 United Kingdom (UK)</td>
                    <td style={{ padding: '12px', fontWeight: 600, color: '#F1F5F9' }}>Companies House</td>
                    <td style={{ padding: '12px', fontFamily: 'monospace', color: '#A78BFA' }}>8-char CRN (8 digits or 2 letters + 6 digits)</td>
                    <td style={{ padding: '12px', color: '#CBD5E1' }}>Full token matching. Substring collisions strictly prohibited.</td>
                  </tr>
                  <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.06)' }}>
                    <td style={{ padding: '12px' }}>🇦🇺 Australia (AU)</td>
                    <td style={{ padding: '12px', fontWeight: 600, color: '#F1F5F9' }}>Australian Securities and Investments Commission (ASIC / ABR)</td>
                    <td style={{ padding: '12px', fontFamily: 'monospace', color: '#A78BFA' }}>11-digit ABN / 9-digit ACN</td>
                    <td style={{ padding: '12px', color: '#CBD5E1' }}>Strict digit validation. Conflict with non-AU jurisdiction blocks automatic match.</td>
                  </tr>
                  <tr>
                    <td style={{ padding: '12px' }}>🇸🇬 Singapore (SG)</td>
                    <td style={{ padding: '12px', fontWeight: 600, color: '#F1F5F9' }}>Accounting and Corporate Regulatory Authority (ACRA)</td>
                    <td style={{ padding: '12px', fontFamily: 'monospace', color: '#A78BFA' }}>9-10 character UEN</td>
                    <td style={{ padding: '12px', color: '#CBD5E1' }}>Exact format verification. Cross-entity duplicate tokens fail closed to manual review.</td>
                  </tr>
                </tbody>
              </table>
            </div>

            {/* Safety Rules Accordion / Cards */}
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#F8FAFC', marginBottom: '14px' }}>
              Entity Resolution Safety Invariants
            </h3>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '14px' }}>
              <div style={{ background: 'rgba(8, 9, 13, 0.6)', border: '1px solid rgba(255, 255, 255, 0.06)', borderRadius: '8px', padding: '16px' }}>
                <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#F1F5F9', marginBottom: '6px' }}>
                  1. Duplicate Identifier Collision Defense
                </div>
                <div style={{ fontSize: '0.82rem', color: '#94A3B8', lineHeight: '1.45' }}>
                  If a statutory token matches more than one distinct registered employer entity, the engine immediately fails closed to <code>MANUAL_REVIEW_REQUIRED</code> with <code>resolved_company_id: null</code>. Arbitrary entity merging is prohibited.
                </div>
              </div>

              <div style={{ background: 'rgba(8, 9, 13, 0.6)', border: '1px solid rgba(255, 255, 255, 0.06)', borderRadius: '8px', padding: '16px' }}>
                <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#F1F5F9', marginBottom: '6px' }}>
                  2. Parent vs Subsidiary Symmetrical Preservation
                </div>
                <div style={{ fontSize: '0.82rem', color: '#94A3B8', lineHeight: '1.45' }}>
                  A subsidiary (e.g. "Google India Private Limited") cannot be collapsed into its parent ("Google LLC"). Cross-tier legal distinctions are preserved as ambiguous candidates requiring explicit human authorization.
                </div>
              </div>

              <div style={{ background: 'rgba(8, 9, 13, 0.6)', border: '1px solid rgba(255, 255, 255, 0.06)', borderRadius: '8px', padding: '16px' }}>
                <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#F1F5F9', marginBottom: '6px' }}>
                  3. Similarity Score Statistical Honesty
                </div>
                <div style={{ fontSize: '0.82rem', color: '#94A3B8', lineHeight: '1.45' }}>
                  All lexical similarity metrics are reported strictly as matching scores. They are never labeled as probabilities or guarantees of corporate identity.
                </div>
              </div>

              <div style={{ background: 'rgba(8, 9, 13, 0.6)', border: '1px solid rgba(255, 255, 255, 0.06)', borderRadius: '8px', padding: '16px' }}>
                <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#F1F5F9', marginBottom: '6px' }}>
                  4. Zero Data Fabrication Standard
                </div>
                <div style={{ fontSize: '0.82rem', color: '#94A3B8', lineHeight: '1.45' }}>
                  JOBINTEL never fabricates employee headcounts, active vacancy volumes, hiring growth metrics, or employer skill distributions. When observations are unpublished, explicit unavailable states are presented.
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* ==================================================================== */}
      {/* 4. EMPLOYER DETAIL MODAL                                             */}
      {/* ==================================================================== */}
      <AnimatePresence>
        {selectedEmployer && (
          <div
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'rgba(0, 0, 0, 0.75)',
              backdropFilter: 'blur(8px)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 100,
              padding: '20px',
            }}
            onClick={() => setSelectedEmployer(null)}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              onClick={(e) => e.stopPropagation()}
              style={{
                background: 'rgba(15, 23, 42, 0.95)',
                border: '1px solid rgba(139, 92, 246, 0.3)',
                borderRadius: '16px',
                maxWidth: '680px',
                width: '100%',
                maxHeight: '90vh',
                overflowY: 'auto',
                padding: '28px',
                boxShadow: '0 24px 60px rgba(0, 0, 0, 0.6)',
              }}
            >
              {/* Modal Header */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <h3 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#FFFFFF', margin: 0 }}>
                      {selectedEmployer.company_name}
                    </h3>
                    <span style={{ fontSize: '0.85rem', color: '#CBD5E1' }}>
                      {MARKET_METADATA[selectedEmployer.headquarters_country]?.flag} {selectedEmployer.headquarters_country}
                    </span>
                  </div>
                  <div style={{ fontSize: '0.8rem', color: '#94A3B8', fontFamily: 'monospace', marginTop: '4px' }}>
                    ID: {selectedEmployer.company_id}
                  </div>
                </div>

                <button
                  onClick={() => setSelectedEmployer(null)}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: '#94A3B8',
                    cursor: 'pointer',
                    padding: '4px',
                  }}
                >
                  <X size={20} />
                </button>
              </div>

              {/* Classification Badges */}
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '20px' }}>
                <span style={{ background: 'rgba(139, 92, 246, 0.15)', border: '1px solid rgba(139, 92, 246, 0.3)', padding: '3px 10px', borderRadius: '6px', fontSize: '0.78rem', color: '#C4B5FD', fontWeight: 600 }}>
                  {selectedEmployer.company_category}
                </span>

                <span style={{ background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '3px 10px', borderRadius: '6px', fontSize: '0.78rem', color: '#34D399', fontWeight: 600 }}>
                  Status: {selectedEmployer.verification_status}
                </span>

                {selectedEmployer.industry && (
                  <span style={{ background: 'rgba(255, 255, 255, 0.05)', border: '1px solid rgba(255, 255, 255, 0.1)', padding: '3px 10px', borderRadius: '6px', fontSize: '0.78rem', color: '#CBD5E1' }}>
                    {selectedEmployer.industry}
                  </span>
                )}
              </div>

              {/* Official Website */}
              {selectedEmployer.official_website && (
                <div style={{ marginBottom: '20px', fontSize: '0.88rem' }}>
                  <a
                    href={selectedEmployer.official_website}
                    target="_blank"
                    rel="noreferrer"
                    style={{ color: '#8B5CF6', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
                  >
                    Official Corporate Website <ExternalLink size={14} />
                  </a>
                </div>
              )}

              {/* Operating Markets */}
              <div style={{ marginBottom: '20px' }}>
                <div style={{ fontSize: '0.8rem', color: '#94A3B8', textTransform: 'uppercase', fontWeight: 600, marginBottom: '6px' }}>Operating Markets</div>
                <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                  {selectedEmployer.operating_markets && selectedEmployer.operating_markets.length > 0 ? (
                    selectedEmployer.operating_markets.map((m) => (
                      <span key={m} style={{ background: 'rgba(255, 255, 255, 0.05)', padding: '2px 8px', borderRadius: '4px', fontSize: '0.8rem', color: '#E2E8F0' }}>
                        {MARKET_METADATA[m]?.flag} {m}
                      </span>
                    ))
                  ) : (
                    <span style={{ color: '#64748B', fontSize: '0.85rem' }}>No additional operating markets specified.</span>
                  )}
                </div>
              </div>

              {/* Verified Locations */}
              <div style={{ marginBottom: '20px' }}>
                <div style={{ fontSize: '0.8rem', color: '#94A3B8', textTransform: 'uppercase', fontWeight: 600, marginBottom: '6px' }}>Registered Locations</div>
                {selectedEmployer.locations && selectedEmployer.locations.length > 0 ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {selectedEmployer.locations.map((loc, idx) => (
                      <div key={idx} style={{ background: 'rgba(8, 9, 13, 0.6)', padding: '10px 14px', borderRadius: '8px', fontSize: '0.85rem', display: 'flex', justifyContent: 'space-between' }}>
                        <div>
                          <MapPin size={14} style={{ display: 'inline', marginRight: '6px', color: '#A78BFA' }} />
                          <strong>{loc.city}</strong>{loc.state_or_region ? `, ${loc.state_or_region}` : ''} ({loc.country_code})
                        </div>
                        <span style={{ color: '#94A3B8', fontSize: '0.78rem' }}>{loc.location_type}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div style={{ fontSize: '0.85rem', color: '#64748B' }}>Primary location at registered headquarters.</div>
                )}
              </div>

              {/* Source References */}
              <div style={{ marginBottom: '20px' }}>
                <div style={{ fontSize: '0.8rem', color: '#94A3B8', textTransform: 'uppercase', fontWeight: 600, marginBottom: '6px' }}>Statutory Sources & Provenance</div>
                {selectedEmployer.source_references && selectedEmployer.source_references.length > 0 ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {selectedEmployer.source_references.map((src, idx) => (
                      <div key={idx} style={{ background: 'rgba(8, 9, 13, 0.6)', padding: '10px 14px', borderRadius: '8px', fontSize: '0.82rem' }}>
                        <div style={{ fontWeight: 600, color: '#F1F5F9' }}>{src.source_name} ({src.source_organization})</div>
                        <div style={{ color: '#8B5CF6', wordBreak: 'break-all', marginTop: '2px' }}>
                          <a href={src.source_reference} target="_blank" rel="noreferrer" style={{ color: '#A78BFA' }}>
                            {src.source_reference}
                          </a>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div style={{ fontSize: '0.85rem', color: '#64748B' }}>Authoritative sovereign registry.</div>
                )}
              </div>

              {/* Data Transparency Disclosure */}
              <div
                style={{
                  background: 'rgba(255, 255, 255, 0.03)',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  borderRadius: '8px',
                  padding: '12px',
                  fontSize: '0.82rem',
                  color: '#94A3B8',
                  lineHeight: '1.45',
                }}
              >
                <strong style={{ color: '#CBD5E1' }}>Data Publication Disclosure: </strong>
                Workforce headcount, active vacancy counts, and hiring trends are not published for this legal entity. In accordance with JOBINTEL prediction realism standards, unsupported metrics are suppressed.
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
};
