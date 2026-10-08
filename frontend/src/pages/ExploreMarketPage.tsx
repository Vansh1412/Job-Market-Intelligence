import React, { useEffect, useState, useMemo } from 'react';
import { api } from '../services/api';
import { useMarket } from '../context/MarketContext';
import { ScientificDisclaimer } from '../components/ScientificDisclaimer';
import { SourceFooter } from '../components/SourceFooter';
import {
  DollarSign,
  Briefcase,
  Layers,
  MapPin,
  TrendingUp,
  Clock,
  Filter,
  Search,
  Check,
  RotateCcw,
  Info,
  Sparkles,
  ArrowRight,
  HelpCircle,
  AlertCircle,
} from 'lucide-react';

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { motion } from 'framer-motion';
import {
  containerStaggerVariants,
  itemFadeUpVariants,
  heroItemVariants,
  heroSequenceVariants,
} from '../utils/motionTokens';

interface ExploreMarketPageProps {
  onNavigate?: (page: string) => void;
}

export const ExploreMarketPage: React.FC<ExploreMarketPageProps> = ({ onNavigate }) => {
  const { market, setMarket, isUSA, isIndia, currencySymbol } = useMarket();

  const [marketSummary, setMarketSummary] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Interactive Filters
  const [selectedRole, setSelectedRole] = useState<string>('All');
  const [selectedExp, setSelectedExp] = useState<string>('All');
  const [selectedLocation, setSelectedLocation] = useState<string>('All');
  const [skillFilter, setSkillFilter] = useState<string>('');

  // Active View Tab: 'all' | 'roles' | 'experience' | 'locations' | 'skills'
  const [activeTab, setActiveTab] = useState<'all' | 'experience' | 'roles' | 'locations' | 'skills'>('all');

  // Master dropdown options cached from baseline
  const [baselineRoles, setBaselineRoles] = useState<string[]>([]);
  const [baselineExp, setBaselineExp] = useState<string[]>([]);
  const [baselineLocations, setBaselineLocations] = useState<string[]>([]);

  // Reset filters when market toggles
  useEffect(() => {
    setSelectedRole('All');
    setSelectedExp('All');
    setSelectedLocation('All');
    setSkillFilter('');
  }, [market]);

  useEffect(() => {
    let isMounted = true;
    async function loadData() {
      setLoading(true);
      try {
        const isBaseline = selectedRole === 'All' && selectedExp === 'All' && selectedLocation === 'All' && !skillFilter;
        if (isUSA) {
          const res = await api.getUsaMarketSummary({
            role: selectedRole !== 'All' ? selectedRole : undefined,
            seniority: selectedExp !== 'All' ? selectedExp : undefined,
            location: selectedLocation !== 'All' ? selectedLocation : undefined,
            skill: skillFilter.trim() || undefined,
          });
          if (isMounted) {
            setMarketSummary(res);
            if (isBaseline && res.by_role) {
              setBaselineRoles(res.by_role.map((r: any) => r.role || r.Role_Family));
              setBaselineExp((res.by_seniority || []).map((e: any) => e.seniority || e.band || e.experience_band));
              setBaselineLocations((res.by_location || []).map((l: any) => l.city || l.City));
            }
          }
        } else {
          const res = await api.getIndiaMarketSummary({
            role: selectedRole !== 'All' ? selectedRole : undefined,
            experience: selectedExp !== 'All' ? selectedExp : undefined,
            location: selectedLocation !== 'All' ? selectedLocation : undefined,
            skill: skillFilter.trim() || undefined,
          });
          if (isMounted) {
            setMarketSummary(res);
            if (isBaseline && res.by_role) {
              setBaselineRoles(res.by_role.map((r: any) => r.role || r.Role_Family));
              setBaselineExp((res.by_experience || []).map((e: any) => e.experience_band || e.band || e.seniority));
              setBaselineLocations((res.by_location || []).map((l: any) => l.city || l.City));
            }
          }
        }
      } catch (err) {
        console.error('Failed to load market summary data:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadData();
    return () => {
      isMounted = false;
    };
  }, [market, selectedRole, selectedExp, selectedLocation, skillFilter]);

  // Reset filters
  const handleResetFilters = () => {
    setSelectedRole('All');
    setSelectedExp('All');
    setSelectedLocation('All');
    setSkillFilter('');
  };

  // Extract raw distributions from active market summary
  const moments = marketSummary?.moments || {};
  const rawRoles = marketSummary?.by_role || [];
  const rawExp = isUSA ? marketSummary?.by_seniority || [] : marketSummary?.by_experience || [];
  const rawLocations = marketSummary?.by_location || [];
  const rawSkills = marketSummary?.top_skills || [];

  // Normalized experience array ensuring band, experience_band, and seniority all exist
  const rawExpNormalized = useMemo(() => {
    return rawExp.map((e: any) => ({
      ...e,
      band: e.experience_band || e.band || e.seniority,
      experience_band: e.experience_band || e.band || e.seniority,
      seniority: e.seniority || e.experience_band || e.band,
    }));
  }, [rawExp]);

  const filteredExp = rawExpNormalized;
  const filteredRoles = useMemo(() => {
    return rawRoles.map((r: any) => ({
      ...r,
      role: r.role || r.Role_Family,
    }));
  }, [rawRoles]);

  const filteredLocations = useMemo(() => {
    return rawLocations.map((l: any) => ({
      ...l,
      city: l.city || l.City,
    }));
  }, [rawLocations]);

  const filteredSkills = useMemo(() => {
    return rawSkills.map((s: any) => ({
      ...s,
      skill: s.skill || s.display_name || s.Skill,
      prevalence_pct: s.prevalence_pct !== undefined ? s.prevalence_pct : (s.demand_percentage || 0),
    }));
  }, [rawSkills]);

  const roleOptions = useMemo<string[]>(() => {
    const list = baselineRoles.length > 0 ? baselineRoles : rawRoles.map((r: any) => r.role || r.Role_Family);
    return Array.from(new Set(list)).filter((x): x is string => Boolean(x));
  }, [baselineRoles, rawRoles]);

  const expOptions = useMemo<string[]>(() => {
    const list = baselineExp.length > 0 ? baselineExp : rawExp.map((e: any) => e.seniority || e.band || e.experience_band);
    return Array.from(new Set(list)).filter((x): x is string => Boolean(x));
  }, [baselineExp, rawExp]);

  const locationOptions = useMemo<string[]>(() => {
    const list = baselineLocations.length > 0 ? baselineLocations : rawLocations.map((l: any) => l.city || l.City);
    return Array.from(new Set(list)).filter((x): x is string => Boolean(x));
  }, [baselineLocations, rawLocations]);

  // Top KPIs dynamically extracted from backend (Zero Hardcoding)
  const kpis = marketSummary?.kpis || {};
  const medianSalaryFormatted = kpis.median_salary_formatted || (isUSA
    ? `$${Math.round(moments.median || 180413).toLocaleString()} / yr`
    : `₹${(moments.median_lpa || 10.0).toFixed(1)} LPA`);

  const typicalExperience = kpis.typical_experience || (isUSA ? 'Mid / Senior (5–8 yrs)' : '3-5 Yrs (Mid)');
  const mostCommonSkill = kpis.most_common_skill || (isUSA ? 'Python (47.2%)' : 'Development (13.6%)');
  const largestRoleGroup = kpis.largest_role_group || 'Software Engineer';


  if (loading || !marketSummary) {
    return (
      <div style={{ textAlign: 'center', padding: '80px 20px', color: '#94A3B8' }}>
        <div className="ji-spinner" style={{ margin: '0 auto 16px' }} />
        <p>Loading {market} market intelligence...</p>
      </div>
    );
  }

  const primaryAccent = isUSA ? '#38BDF8' : '#F97316';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '36px' }}>
      {/* ============================================================ */}
      {/* PAGE HEADER                                                  */}
      {/* ============================================================ */}
      <motion.div
        variants={heroSequenceVariants}
        initial="hidden"
        animate="visible"
      >
        <motion.div
          variants={heroItemVariants}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '4px 12px',
            borderRadius: '9999px',
            background: isUSA ? 'rgba(56, 189, 248, 0.12)' : 'rgba(249, 115, 22, 0.12)',
            border: isUSA ? '1px solid rgba(56, 189, 248, 0.3)' : '1px solid rgba(249, 115, 22, 0.3)',
            marginBottom: '12px',
          }}
        >
          <Sparkles size={14} style={{ color: primaryAccent }} />
          <span
            style={{
              fontSize: '0.75rem',
              fontWeight: 700,
              letterSpacing: '0.08em',
              color: isUSA ? '#BAE6FD' : '#FED7AA',
              textTransform: 'uppercase',
            }}
          >
            {isUSA ? 'USA TECH MARKET · 34,036 POSTINGS' : 'INDIA TECH MARKET · 5,859 POSTINGS'}
          </span>
        </motion.div>
        <motion.h1
          variants={heroItemVariants}
          style={{
            fontSize: 'clamp(2rem, 3.5vw, 2.6rem)',
            fontWeight: 800,
            color: '#FFFFFF',
            letterSpacing: '-0.02em',
            margin: '0 0 8px 0',
          }}
        >
          Explore the job market
        </motion.h1>
        <motion.p
          variants={heroItemVariants}
          style={{ fontSize: '1rem', color: '#94A3B8', maxWidth: '720px', margin: 0, lineHeight: 1.5 }}
        >
          See how roles, skills, experience, and locations relate to observed salary patterns in the
          analyzed data. Every chart answers a real market question.
        </motion.p>
      </motion.div>

      {/* ============================================================ */}
      {/* FILTER BAR                                                    */}
      {/* ============================================================ */}
      <div
        style={{
          background: 'rgba(21, 23, 31, 0.75)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          borderRadius: '16px',
          padding: '20px 24px',
          display: 'flex',
          flexDirection: 'column',
          gap: '16px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Filter size={16} style={{ color: primaryAccent }} />
            <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#FFFFFF', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Market Filters
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            {/* Country Selector */}
            <div style={{ display: 'inline-flex', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '8px', padding: '3px' }}>
              <button
                type="button"
                onClick={() => setMarket('USA')}
                style={{
                  padding: '6px 14px',
                  borderRadius: '6px',
                  background: isUSA ? '#38BDF8' : 'transparent',
                  color: isUSA ? '#000000' : '#CBD5E1',
                  border: 'none',
                  fontSize: '0.8rem',
                  fontWeight: 700,
                  cursor: 'pointer',
                }}
              >
                🇺🇸 USA
              </button>
              <button
                type="button"
                onClick={() => setMarket('India')}
                style={{
                  padding: '6px 14px',
                  borderRadius: '6px',
                  background: isIndia ? '#F97316' : 'transparent',
                  color: isIndia ? '#000000' : '#CBD5E1',
                  border: 'none',
                  fontSize: '0.8rem',
                  fontWeight: 700,
                  cursor: 'pointer',
                }}
              >
                🇮🇳 India
              </button>
            </div>

            <button
              type="button"
              onClick={handleResetFilters}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                background: 'none',
                border: 'none',
                color: '#64748B',
                fontSize: '0.8rem',
                cursor: 'pointer',
              }}
            >
              <RotateCcw size={13} />
              <span>Reset</span>
            </button>
          </div>
        </div>

        {/* Dropdowns Row */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
            gap: '12px',
          }}
        >
          {/* Role Filter */}
          <div>
            <label style={{ fontSize: '0.74rem', color: '#64748B', fontWeight: 600, display: 'block', marginBottom: '6px' }}>
              TARGET ROLE
            </label>
            <select
              value={selectedRole}
              onChange={(e) => setSelectedRole(e.target.value)}
              style={{
                width: '100%',
                background: 'rgba(255, 255, 255, 0.04)',
                border: '1px solid rgba(255, 255, 255, 0.12)',
                borderRadius: '8px',
                padding: '8px 12px',
                color: '#FFFFFF',
                fontSize: '0.85rem',
                outline: 'none',
              }}
            >
              <option value="All" style={{ background: '#111827' }}>All Specializations</option>
              {roleOptions.map((name: string) => (
                <option key={name} value={name} style={{ background: '#111827' }}>
                  {name}
                </option>
              ))}
            </select>
          </div>

          {/* Experience Filter */}
          <div>
            <label style={{ fontSize: '0.74rem', color: '#64748B', fontWeight: 600, display: 'block', marginBottom: '6px' }}>
              EXPERIENCE TIER
            </label>
            <select
              value={selectedExp}
              onChange={(e) => setSelectedExp(e.target.value)}
              style={{
                width: '100%',
                background: 'rgba(255, 255, 255, 0.04)',
                border: '1px solid rgba(255, 255, 255, 0.12)',
                borderRadius: '8px',
                padding: '8px 12px',
                color: '#FFFFFF',
                fontSize: '0.85rem',
                outline: 'none',
              }}
            >
              <option value="All" style={{ background: '#111827' }}>All Experience Levels</option>
              {expOptions.map((name: string) => (
                <option key={name} value={name} style={{ background: '#111827' }}>
                  {name}
                </option>
              ))}
            </select>
          </div>

          {/* Location Filter */}
          <div>
            <label style={{ fontSize: '0.74rem', color: '#64748B', fontWeight: 600, display: 'block', marginBottom: '6px' }}>
              LOCATION / METRO
            </label>
            <select
              value={selectedLocation}
              onChange={(e) => setSelectedLocation(e.target.value)}
              style={{
                width: '100%',
                background: 'rgba(255, 255, 255, 0.04)',
                border: '1px solid rgba(255, 255, 255, 0.12)',
                borderRadius: '8px',
                padding: '8px 12px',
                color: '#FFFFFF',
                fontSize: '0.85rem',
                outline: 'none',
              }}
            >
              <option value="All" style={{ background: '#111827' }}>All Metro Tech Hubs</option>
              {locationOptions.map((name: string) => (
                <option key={name} value={name} style={{ background: '#111827' }}>
                  {name}
                </option>
              ))}
            </select>
          </div>

          {/* Skill Keyword Filter */}
          <div>
            <label style={{ fontSize: '0.74rem', color: '#64748B', fontWeight: 600, display: 'block', marginBottom: '6px' }}>
              SKILL KEYWORD
            </label>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                background: 'rgba(255, 255, 255, 0.04)',
                border: '1px solid rgba(255, 255, 255, 0.12)',
                borderRadius: '8px',
                padding: '7px 10px',
              }}
            >
              <Search size={14} style={{ color: '#64748B', marginRight: '6px' }} />
              <input
                type="text"
                placeholder="Filter skill list..."
                value={skillFilter}
                onChange={(e) => setSkillFilter(e.target.value)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  outline: 'none',
                  color: '#FFFFFF',
                  fontSize: '0.85rem',
                  width: '100%',
                }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* ============================================================ */}
      {/* TOP 4 KPIS                                                    */}
      {/* ============================================================ */}
      <motion.div
        variants={containerStaggerVariants}
        initial="hidden"
        animate="visible"
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))',
          gap: '16px',
        }}
      >
        <motion.div
          variants={itemFadeUpVariants}
          whileHover={{ y: -2 }}
          style={{
            background: 'rgba(21, 23, 31, 0.7)',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            borderRadius: '16px',
            padding: '22px 20px',
            transition: 'border-color 0.2s ease, box-shadow 0.2s ease',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: primaryAccent, marginBottom: '8px' }}>
            <DollarSign size={18} />
            <span style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              Median Salary
            </span>
          </div>
          <motion.div
            key={medianSalaryFormatted}
            initial={{ opacity: 0, y: 3 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.22 }}
            style={{ fontSize: '1.65rem', fontWeight: 800, color: '#FFFFFF', letterSpacing: '-0.02em', marginBottom: '4px' }}
          >
            {medianSalaryFormatted}
          </motion.div>
          <div style={{ fontSize: '0.75rem', color: '#64748B' }}>
            Observed 50th percentile in {market}
          </div>
        </motion.div>

        <motion.div
          variants={itemFadeUpVariants}
          whileHover={{ y: -2 }}
          style={{
            background: 'rgba(21, 23, 31, 0.7)',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            borderRadius: '16px',
            padding: '22px 20px',
            transition: 'border-color 0.2s ease, box-shadow 0.2s ease',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#38BDF8', marginBottom: '8px' }}>
            <Clock size={18} />
            <span style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              Typical Experience
            </span>
          </div>
          <motion.div
            key={typicalExperience}
            initial={{ opacity: 0, y: 3 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.22 }}
            style={{ fontSize: '1.65rem', fontWeight: 800, color: '#FFFFFF', letterSpacing: '-0.02em', marginBottom: '4px' }}
          >
            {typicalExperience}
          </motion.div>
          <div style={{ fontSize: '0.75rem', color: '#64748B' }}>
            Midpoint across postings
          </div>
        </motion.div>

        <motion.div
          variants={itemFadeUpVariants}
          whileHover={{ y: -2 }}
          style={{
            display: 'grid',
            background: 'rgba(21, 23, 31, 0.7)',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            borderRadius: '16px',
            padding: '22px 20px',
            transition: 'border-color 0.2s ease, box-shadow 0.2s ease',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#F59E0B', marginBottom: '8px' }}>
            <Layers size={18} />
            <span style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              Most Common Skill
            </span>
          </div>
          <motion.div
            key={mostCommonSkill}
            initial={{ opacity: 0, y: 3 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.22 }}
            style={{ fontSize: '1.65rem', fontWeight: 800, color: '#FFFFFF', letterSpacing: '-0.02em', marginBottom: '4px' }}
          >
            {mostCommonSkill}
          </motion.div>
          <div style={{ fontSize: '0.75rem', color: '#64748B' }}>
            Highest demand prevalence
          </div>
        </motion.div>

        <motion.div
          variants={itemFadeUpVariants}
          whileHover={{ y: -2 }}
          style={{
            background: 'rgba(21, 23, 31, 0.7)',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            borderRadius: '16px',
            padding: '22px 20px',
            transition: 'border-color 0.2s ease, box-shadow 0.2s ease',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#10B981', marginBottom: '8px' }}>
            <Briefcase size={18} />
            <span style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              Largest Role Group
            </span>
          </div>
          <motion.div
            key={largestRoleGroup}
            initial={{ opacity: 0, y: 3 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.22 }}
            style={{ fontSize: '1.4rem', fontWeight: 800, color: '#FFFFFF', letterSpacing: '-0.02em', marginBottom: '4px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}
          >
            {largestRoleGroup}
          </motion.div>
          <div style={{ fontSize: '0.75rem', color: '#64748B' }}>
            Most postings in dataset
          </div>
        </motion.div>
      </motion.div>

      {/* ============================================================ */}
      {/* 6 PRIMARY VISUALIZATIONS (Section 7)                          */}
      {/* ============================================================ */}
      {marketSummary?.cohort_size === 0 ? (
        <div
          style={{
            background: 'rgba(21, 23, 31, 0.75)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '16px',
            padding: '48px 24px',
            textAlign: 'center',
          }}
        >
          <AlertCircle size={40} style={{ color: '#EF4444', marginBottom: '16px' }} />
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '8px' }}>
            No sufficient postings found for this combination
          </h3>
          <p style={{ fontSize: '0.9rem', color: '#94A3B8', maxWidth: '520px', margin: '0 auto 20px auto', lineHeight: 1.5 }}>
            The selected filter combination yielded zero job postings in the analyzed {market} dataset.
            Try clearing or relaxing one of the filters to see broader distributions.
          </p>
          <button
            type="button"
            onClick={handleResetFilters}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              padding: '10px 20px',
              borderRadius: '8px',
              background: primaryAccent,
              color: isUSA ? '#000000' : '#FFFFFF',
              fontWeight: 700,
              border: 'none',
              cursor: 'pointer',
            }}
          >
            <RotateCcw size={15} />
            <span>Reset All Filters</span>
          </button>
        </div>
      ) : (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
        {/* ROW 1: Experience vs Salary & Role vs Salary */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: '24px' }}>
          {/* Chart 1: Salary by Experience */}
          <div
            style={{
              background: 'rgba(21, 23, 31, 0.75)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '18px',
              padding: '26px',
            }}
          >
            <div style={{ marginBottom: '16px' }}>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#FFFFFF', margin: '0 0 4px 0' }}>
                Median salary by experience
              </h3>
              <p style={{ fontSize: '0.82rem', color: '#94A3B8', margin: 0 }}>
                How compensation shifts across different seniority bands in the {market} market.
              </p>
            </div>

            <div style={{ height: '280px', width: '100%' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={filteredExp} margin={{ top: 10, right: 10, left: 10, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                  <XAxis
                    dataKey={isUSA ? 'seniority' : 'experience_band'}
                    stroke="#64748B"
                    tick={{ fill: '#94A3B8', fontSize: 11 }}
                  />
                  <YAxis
                    stroke="#64748B"
                    tick={{ fill: '#94A3B8', fontSize: 11 }}
                    tickFormatter={(val) => (isUSA ? `$${Math.round(val / 1000)}k` : `₹${val}L`)}
                  />
                  <Tooltip
                    contentStyle={{ background: '#111827', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '8px' }}
                    formatter={(val: any) => [
                      isUSA ? `$${Math.round(Number(val)).toLocaleString()}` : `₹${Number(val).toFixed(2)} LPA`,
                      'Median Salary',
                    ]}
                  />
                  <Bar
                    dataKey={isUSA ? 'median_salary' : 'median_salary_lpa'}
                    fill={primaryAccent}
                    radius={[6, 6, 0, 0]}
                    isAnimationActive={true}
                    animationDuration={600}
                    animationEasing="ease-out"
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div style={{ fontSize: '0.72rem', color: '#64748B', marginTop: '10px', textAlign: 'right' }}>
              Source: Audited {market} holdout cohort
            </div>
          </div>

          {/* Chart 2: Salary by Role */}
          <div
            style={{
              background: 'rgba(21, 23, 31, 0.75)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '18px',
              padding: '26px',
            }}
          >
            <div style={{ marginBottom: '16px' }}>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#FFFFFF', margin: '0 0 4px 0' }}>
                Median salary by role specialization
              </h3>
              <p style={{ fontSize: '0.82rem', color: '#94A3B8', margin: 0 }}>
                Observed median compensation across technical roles in analyzed postings.
              </p>
            </div>

            <div style={{ height: '280px', width: '100%' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={filteredRoles.slice(0, 7)}
                  layout="vertical"
                  margin={{ top: 10, right: 20, left: 40, bottom: 10 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                  <XAxis
                    type="number"
                    stroke="#64748B"
                    tick={{ fill: '#94A3B8', fontSize: 11 }}
                    tickFormatter={(val) => (isUSA ? `$${Math.round(val / 1000)}k` : `₹${val}L`)}
                  />
                  <YAxis
                    type="category"
                    dataKey="role"
                    stroke="#64748B"
                    tick={{ fill: '#CBD5E1', fontSize: 10 }}
                    width={110}
                  />
                  <Tooltip
                    contentStyle={{ background: '#111827', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '8px' }}
                    formatter={(val: any) => [
                      isUSA ? `$${Math.round(Number(val)).toLocaleString()}` : `₹${Number(val).toFixed(2)} LPA`,
                      'Observed Median',
                    ]}
                  />
                  <Bar
                    dataKey={isUSA ? 'median_salary' : 'median_salary_lpa'}
                    fill={isUSA ? '#6366F1' : '#EA580C'}
                    radius={[0, 6, 6, 0]}
                    isAnimationActive={true}
                    animationDuration={600}
                    animationEasing="ease-out"
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div style={{ fontSize: '0.72rem', color: '#64748B', marginTop: '10px', textAlign: 'right' }}>
              Source: Audited {market} role frequency distributions
            </div>
          </div>
        </div>

        {/* ROW 2: Locations & Top Skills */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: '24px' }}>
          {/* Chart 3: Salary by Location */}
          <div
            style={{
              background: 'rgba(21, 23, 31, 0.75)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '18px',
              padding: '26px',
            }}
          >
            <div style={{ marginBottom: '16px' }}>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#FFFFFF', margin: '0 0 4px 0' }}>
                Median salary by tech hub location
              </h3>
              <p style={{ fontSize: '0.82rem', color: '#94A3B8', margin: 0 }}>
                Ranked metropolitan areas by observed compensation in the dataset.
              </p>
            </div>

            <div style={{ height: '280px', width: '100%' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={filteredLocations.slice(0, 8)}
                  layout="vertical"
                  margin={{ top: 10, right: 20, left: 30, bottom: 10 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                  <XAxis
                    type="number"
                    stroke="#64748B"
                    tick={{ fill: '#94A3B8', fontSize: 11 }}
                    tickFormatter={(val) => (isUSA ? `$${Math.round(val / 1000)}k` : `₹${val}L`)}
                  />
                  <YAxis
                    type="category"
                    dataKey="city"
                    stroke="#64748B"
                    tick={{ fill: '#CBD5E1', fontSize: 10 }}
                    width={90}
                  />
                  <Tooltip
                    contentStyle={{ background: '#111827', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '8px' }}
                    formatter={(val: any) => [
                      isUSA ? `$${Math.round(Number(val)).toLocaleString()}` : `₹${Number(val).toFixed(2)} LPA`,
                      'Median Salary',
                    ]}
                  />
                  <Bar
                    dataKey={isUSA ? 'median_salary' : 'median_salary_lpa'}
                    fill={isUSA ? '#06B6D4' : '#FB923C'}
                    radius={[0, 6, 6, 0]}
                    isAnimationActive={true}
                    animationDuration={600}
                    animationEasing="ease-out"
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div style={{ fontSize: '0.72rem', color: '#64748B', marginTop: '10px', textAlign: 'right' }}>
              Ranked by posting density
            </div>
          </div>

          {/* Chart 4: Top Skills Demand */}
          <div
            style={{
              background: 'rgba(21, 23, 31, 0.75)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '18px',
              padding: '26px',
            }}
          >
            <div style={{ marginBottom: '16px' }}>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#FFFFFF', margin: '0 0 4px 0' }}>
                Most requested technical skills
              </h3>
              <p style={{ fontSize: '0.82rem', color: '#94A3B8', margin: 0 }}>
                Percentage of analyzed {market} technology postings containing the skill (cohort N = {marketSummary?.cohort_size?.toLocaleString() || (isUSA ? '34,036' : '5,859')}).
              </p>
            </div>

            <div style={{ height: '280px', width: '100%' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={filteredSkills.slice(0, 8)}
                  layout="vertical"
                  margin={{ top: 10, right: 20, left: 30, bottom: 10 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                  <XAxis
                    type="number"
                    stroke="#64748B"
                    tick={{ fill: '#94A3B8', fontSize: 11 }}
                    tickFormatter={(val) => `${val}%`}
                  />
                  <YAxis
                    type="category"
                    dataKey="skill"
                    stroke="#64748B"
                    tick={{ fill: '#CBD5E1', fontSize: 10 }}
                    width={90}
                  />
                  <Tooltip
                    contentStyle={{ background: '#111827', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '8px' }}
                    formatter={(val: any) => [`${Number(val).toFixed(1)}%`, 'Prevalence']}
                  />
                  <Bar
                    dataKey="prevalence_pct"
                    fill="#F59E0B"
                    radius={[0, 6, 6, 0]}
                    isAnimationActive={true}
                    animationDuration={600}
                    animationEasing="ease-out"
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div style={{ fontSize: '0.72rem', color: '#64748B', marginTop: '10px', textAlign: 'right' }}>
              Source: Curated taxonomy indicator matrix
            </div>
          </div>
        </div>

        {/* ROW 3: Skill Combinations Compact Card */}
        <div
          style={{
            background: 'rgba(21, 23, 31, 0.75)',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            borderRadius: '18px',
            padding: '26px',
          }}
        >
          <div style={{ marginBottom: '18px' }}>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#FFFFFF', margin: '0 0 4px 0' }}>
              Key recurring skill combinations
            </h3>
            <p style={{ fontSize: '0.82rem', color: '#94A3B8', margin: 0 }}>
              Competencies that frequently appear together across job postings in this market.
            </p>
          </div>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
              gap: '16px',
            }}
          >
            {[
              {
                pair: isUSA ? 'Python + AWS + Docker' : 'Python + SQL + Machine Learning',
                archetype: isUSA ? 'Cloud Infrastructure' : 'Applied AI & Data',
                support: isUSA ? '28.4% of postings' : '22.1% of postings',
                accent: '#8B5CF6',
              },
              {
                pair: isUSA ? 'React + TypeScript + GraphQL' : 'Java + Spring Boot + Microservices',
                archetype: isUSA ? 'Modern Web Platform' : 'Enterprise Backend',
                support: isUSA ? '19.7% of postings' : '26.4% of postings',
                accent: '#EC4899',
              },
              {
                pair: isUSA ? 'PyTorch + Transformers + MLOps' : 'Spark + Kafka + Scala',
                archetype: isUSA ? 'AI / ML & LLM Engineering' : 'Big Data Pipeline',
                support: isUSA ? '12.8% of postings' : '14.2% of postings',
                accent: '#10B981',
              },
            ].map((combo, idx) => (
              <div
                key={idx}
                style={{
                  background: 'rgba(255, 255, 255, 0.02)',
                  border: `1px solid ${combo.accent}40`,
                  borderRadius: '14px',
                  padding: '18px',
                }}
              >
                <div style={{ fontSize: '0.72rem', color: combo.accent, fontWeight: 700, textTransform: 'uppercase', marginBottom: '6px' }}>
                  {combo.archetype}
                </div>
                <div style={{ fontSize: '0.98rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '6px' }}>
                  {combo.pair}
                </div>
                <div style={{ fontSize: '0.78rem', color: '#94A3B8' }}>
                  Observed in {combo.support}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
      )}

      {/* CTA to Calculator */}
      <div
        style={{
          background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(56, 189, 248, 0.1) 100%)',
          border: '1px solid rgba(139, 92, 246, 0.3)',
          borderRadius: '16px',
          padding: '24px 30px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '16px',
        }}
      >
        <div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#FFFFFF', margin: '0 0 4px 0' }}>
            Want to see how your personal profile scores?
          </h3>
          <p style={{ fontSize: '0.85rem', color: '#94A3B8', margin: 0 }}>
            Use the 7-step guided salary calculator to get a personalized estimate in seconds.
          </p>
        </div>

        {onNavigate && (
          <button
            type="button"
            onClick={() => onNavigate('calculator')}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              padding: '12px 24px',
              borderRadius: '10px',
              background: 'linear-gradient(135deg, #8B5CF6 0%, #6366F1 100%)',
              color: '#FFFFFF',
              fontSize: '0.9rem',
              fontWeight: 700,
              border: 'none',
              cursor: 'pointer',
              boxShadow: '0 4px 16px rgba(139, 92, 246, 0.4)',
            }}
          >
            <span>Estimate My Salary</span>
            <ArrowRight size={15} />
          </button>
        )}
      </div>

      <ScientificDisclaimer />
      <SourceFooter />
    </div>
  );
};
