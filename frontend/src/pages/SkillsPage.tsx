import React, { useEffect, useState, useMemo } from 'react';
import { api } from '../services/api';
import { SkillLandscapePoint, SkillDetail } from '../types';
import { useMarket } from '../context/MarketContext';
import { ScientificDisclaimer } from '../components/ScientificDisclaimer';
import { SourceFooter } from '../components/SourceFooter';
import {
  Search,
  Filter,
  Layers,
  Zap,
  TrendingUp,
  Info,
  Sparkles,
  ArrowRight,
  Briefcase,
  Dna,
  CheckCircle2,
} from 'lucide-react';
import { AnimatePresence, motion } from 'framer-motion';
import {
  detailCrossfadeVariants,
  heroItemVariants,
  heroSequenceVariants,
} from '../utils/motionTokens';

interface SkillsPageProps {
  onNavigate?: (page: string) => void;
}

export const SkillsPage: React.FC<SkillsPageProps> = ({ onNavigate }) => {
  const { market, setMarket, isUSA, isIndia, currencySymbol } = useMarket();

  const [usaLandscape, setUsaLandscape] = useState<SkillLandscapePoint[]>([]);
  const [indiaSkills, setIndiaSkills] = useState<any[]>([]);
  const [search, setSearch] = useState<string>('');
  const [selectedCat, setSelectedCat] = useState<string>('All');
  const [activeSkill, setActiveSkill] = useState<string>('python');
  const [skillDetail, setSkillDetail] = useState<SkillDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    let isMounted = true;
    async function loadData() {
      setLoading(true);
      try {
        if (isUSA) {
          const res = await api.getSkillLandscape();
          if (isMounted) setUsaLandscape(res);
          const det = await api.getSkillDetail('python');
          if (isMounted) {
            setActiveSkill('python');
            setSkillDetail(det);
          }
        } else {
          const res = await api.getIndiaSkills();
          if (isMounted) {
            setIndiaSkills(res.skills || []);
            setActiveSkill('python');
          }
          const det = await api.getIndiaSkillDetail('python');
          if (isMounted) {
            setSkillDetail(det);
          }
        }
      } catch (err) {
        console.error('Failed to load skills data', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadData();
    return () => {
      isMounted = false;
    };
  }, [market]);

  const handleSelectSkill = async (skillName: string) => {
    setActiveSkill(skillName);
    try {
      if (isUSA) {
        const det = await api.getSkillDetail(skillName);
        setSkillDetail(det);
      } else {
        const det = await api.getIndiaSkillDetail(skillName);
        setSkillDetail(det);
      }
    } catch (err) {
      console.error('Failed to load skill detail', err);
    }
  };

  const categories = [
    'All',
    'AI / Machine Learning',
    'Cloud & DevOps',
    'Data & Analytics',
    'Web & Frontend',
    'Systems & Backend',
  ];

  const filteredUsaSkills = useMemo(() => {
    return usaLandscape.filter((s) => {
      const matchCat = selectedCat === 'All' || s.category === selectedCat;
      const matchSearch = s.skill.toLowerCase().includes(search.toLowerCase());
      return matchCat && matchSearch;
    });
  }, [usaLandscape, selectedCat, search]);

  const filteredIndiaSkills = useMemo(() => {
    return indiaSkills.filter((s) => {
      const name = s.display_name || s.skill || '';
      return name.toLowerCase().includes(search.toLowerCase());
    });
  }, [indiaSkills, search]);

  const detailTitle = isUSA
    ? (skillDetail?.skill || '')
    : (skillDetail?.display_name || skillDetail?.skill || '');

  const detailObservedMedian = isUSA
    ? (skillDetail?.median_salary !== undefined
        ? `$${Math.round(skillDetail.median_salary).toLocaleString()}`
        : (skillDetail?.median_with ? `$${Math.round(skillDetail.median_with).toLocaleString()}` : '$180,413'))
    : (skillDetail?.observed_median_salary_lpa !== undefined
        ? `₹${Number(skillDetail.observed_median_salary_lpa).toFixed(1)} LPA`
        : (skillDetail?.median_with_lpa ? `₹${Number(skillDetail.median_with_lpa).toFixed(1)} LPA` : '₹10.0 LPA'));

  const detailDemandPct = isUSA
    ? (skillDetail?.prevalence_pct ?? skillDetail?.prevalence ?? 0)
    : (skillDetail?.demand_percentage ?? skillDetail?.prevalence_pct ?? skillDetail?.prevalence ?? 0);

  const detailPostings = isUSA
    ? (skillDetail?.postings ?? 0)
    : (skillDetail?.posting_count ?? skillDetail?.postings ?? 0);

  const detailSalaryDiff = isUSA
    ? (skillDetail?.delta_vs_cohort !== undefined
        ? (skillDetail.delta_vs_cohort >= 0 ? `+$${Math.round(skillDetail.delta_vs_cohort).toLocaleString()}` : `-$${Math.round(Math.abs(skillDetail.delta_vs_cohort)).toLocaleString()}`)
        : (skillDetail?.delta !== undefined
            ? (skillDetail.delta >= 0 ? `+$${Math.round(skillDetail.delta).toLocaleString()}` : `-$${Math.round(Math.abs(skillDetail.delta)).toLocaleString()}`)
            : '+$0'))
    : (skillDetail?.observed_salary_difference_lpa !== undefined
        ? (skillDetail.observed_salary_difference_lpa >= 0 ? `+₹${Number(skillDetail.observed_salary_difference_lpa).toFixed(1)} LPA` : `-₹${Number(Math.abs(skillDetail.observed_salary_difference_lpa)).toFixed(1)} LPA`)
        : (skillDetail?.delta_lpa !== undefined ? `+₹${Number(skillDetail.delta_lpa).toFixed(1)} LPA` : '+₹0.0 LPA'));

  const detailRoles: string[] = isUSA
    ? (skillDetail?.roles || skillDetail?.associated_roles || [])
    : (skillDetail?.associated_roles || skillDetail?.roles || []);

  const detailArchetypes: string[] = isUSA
    ? (skillDetail?.archetypes || skillDetail?.associated_archetypes || [])
    : (skillDetail?.associated_archetypes || skillDetail?.archetypes || []);

  const detailCombos: string[] = isUSA
    ? (skillDetail?.combos || skillDetail?.cooccurring_skills || [])
    : (skillDetail?.cooccurring_skills || skillDetail?.combos || []);

  if (loading) {
    return (
      <div style={{ padding: '60px 0', textAlign: 'center', color: '#94A3B8' }}>
        <div className="ji-spinner" style={{ margin: '0 auto 16px' }} />
        <p>Loading {market} skill intelligence...</p>
      </div>
    );
  }

  const primaryAccent = '#F59E0B';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
      {/* Header */}
      <motion.div variants={heroSequenceVariants} initial="hidden" animate="visible">
        <motion.div
          variants={heroItemVariants}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '4px 12px',
            borderRadius: '9999px',
            background: 'rgba(245, 158, 11, 0.12)',
            border: '1px solid rgba(245, 158, 11, 0.3)',
            marginBottom: '12px',
          }}
        >
          <Sparkles size={14} style={{ color: primaryAccent }} />
          <span
            style={{
              fontSize: '0.75rem',
              fontWeight: 700,
              letterSpacing: '0.08em',
              color: '#FDE68A',
              textTransform: 'uppercase',
            }}
          >
            {isUSA ? 'USA SKILL TAXONOMY · 82 COMPETENCIES' : 'INDIA SKILL TAXONOMY · 284 COMPETENCIES'}
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
          Which skills stand out?
        </motion.h1>
        <motion.p
          variants={heroItemVariants}
          style={{ fontSize: '1rem', color: '#94A3B8', maxWidth: '720px', margin: 0, lineHeight: 1.5 }}
        >
          Explore skills that frequently appear in job postings and how their observed salary levels
          compare. All comparisons reflect observational data associations.
        </motion.p>
      </motion.div>

      {/* Search & Category Filter */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '14px',
          background: 'rgba(21, 23, 31, 0.75)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          borderRadius: '16px',
          padding: '16px 20px',
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            background: 'rgba(255, 255, 255, 0.04)',
            border: '1px solid rgba(255, 255, 255, 0.12)',
            borderRadius: '8px',
            padding: '8px 12px',
            width: '320px',
          }}
        >
          <Search size={15} style={{ color: '#64748B', marginRight: '8px' }} />
          <input
            type="text"
            placeholder={isUSA ? 'Search 82 skills (e.g. Python, AWS, Docker)...' : 'Search skills (e.g. Spark, React, Java)...'}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
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

        {isUSA && (
          <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
            {categories.map((cat) => {
              const isSel = selectedCat === cat;
              return (
                <button
                  key={cat}
                  type="button"
                  onClick={() => setSelectedCat(cat)}
                  style={{
                    padding: '6px 12px',
                    borderRadius: '8px',
                    border: isSel ? '1px solid #F59E0B' : '1px solid rgba(255, 255, 255, 0.08)',
                    background: isSel ? 'rgba(245, 158, 11, 0.2)' : 'rgba(255, 255, 255, 0.02)',
                    color: isSel ? '#FFFFFF' : '#94A3B8',
                    fontSize: '0.78rem',
                    fontWeight: isSel ? 700 : 500,
                    cursor: 'pointer',
                  }}
                >
                  {cat}
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* Main Dual Grid: Skills List/Cards on Left, Skill Detail on Right */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1.25fr 0.95fr',
          gap: '24px',
          alignItems: 'start',
        }}
      >
        {/* LEFT: SKILLS TABLE / CARDS */}
        <div
          style={{
            background: 'rgba(21, 23, 31, 0.75)',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            borderRadius: '18px',
            padding: '24px',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#FFFFFF', margin: 0 }}>
              Skill Demand & Observed Salary Table
            </h3>
            <span style={{ fontSize: '0.75rem', color: '#64748B' }}>
              Click any skill to inspect detail
            </span>
          </div>

          <div
            style={{
              maxHeight: '520px',
              overflowY: 'auto',
              border: '1px solid rgba(255, 255, 255, 0.06)',
              borderRadius: '12px',
            }}
          >
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.84rem' }}>
              <thead>
                <tr style={{ background: 'rgba(255, 255, 255, 0.04)', borderBottom: '1px solid rgba(255, 255, 255, 0.08)' }}>
                  <th style={{ padding: '12px 14px', color: '#94A3B8', fontWeight: 600 }}>Skill</th>
                  <th style={{ padding: '12px 14px', color: '#94A3B8', fontWeight: 600 }}>Demand</th>
                  <th style={{ padding: '12px 14px', color: '#94A3B8', fontWeight: 600 }}>Observed Median</th>
                  <th style={{ padding: '12px 14px', color: '#94A3B8', fontWeight: 600 }}>Observed Salary Diff</th>
                </tr>
              </thead>
              <tbody>
                {isUSA
                  ? filteredUsaSkills.map((s) => {
                      const isSelected = activeSkill.toLowerCase() === s.skill.toLowerCase();
                      const delta = s.delta_vs_median ?? (s.median_salary ? s.median_salary - 180413 : 0);
                      const isPos = delta >= 0;

                      return (
                        <tr
                          key={s.skill}
                          onClick={() => handleSelectSkill(s.skill)}
                          style={{
                            cursor: 'pointer',
                            background: isSelected ? 'rgba(245, 158, 11, 0.14)' : 'transparent',
                            borderBottom: '1px solid rgba(255, 255, 255, 0.04)',
                            transition: 'background 0.12s ease',
                          }}
                        >
                          <td style={{ padding: '12px 14px', color: '#FFFFFF', fontWeight: isSelected ? 700 : 500 }}>
                            {s.skill}
                          </td>
                          <td style={{ padding: '12px 14px', color: '#CBD5E1' }}>
                            {s.prevalence_pct.toFixed(1)}%
                          </td>
                          <td style={{ padding: '12px 14px', color: '#FFFFFF', fontWeight: 600 }}>
                            ${Math.round(s.median_salary || 180000).toLocaleString()}
                          </td>
                          <td style={{ padding: '12px 14px', color: isPos ? '#34D399' : '#F87171', fontWeight: 600 }}>
                            {isPos ? '+' : ''}${Math.round(delta).toLocaleString()}
                          </td>
                        </tr>
                      );
                    })
                  : filteredIndiaSkills.map((s) => {
                      const isSelected = activeSkill.toLowerCase() === (s.skill || '').toLowerCase() || activeSkill.toLowerCase() === (s.display_name || '').toLowerCase();
                      const prev = s.demand_percentage !== undefined ? s.demand_percentage : (s.prevalence_pct || 0);
                      const obsMed = s.observed_median_salary_lpa !== undefined ? s.observed_median_salary_lpa : 10.0;
                      const delta = s.observed_salary_difference_lpa !== undefined ? s.observed_salary_difference_lpa : 0.0;
                      const isPos = delta >= 0;

                      return (
                        <tr
                          key={s.skill}
                          onClick={() => handleSelectSkill(s.skill)}
                          style={{
                            cursor: 'pointer',
                            background: isSelected ? 'rgba(249, 115, 22, 0.14)' : 'transparent',
                            borderBottom: '1px solid rgba(255, 255, 255, 0.04)',
                            transition: 'background 0.12s ease',
                          }}
                        >
                          <td style={{ padding: '12px 14px', color: '#FFFFFF', fontWeight: isSelected ? 700 : 500 }}>
                            {s.display_name || s.skill}
                          </td>
                          <td style={{ padding: '12px 14px', color: '#CBD5E1' }}>
                            {prev.toFixed(1)}%
                          </td>
                          <td style={{ padding: '12px 14px', color: '#FFFFFF', fontWeight: 600 }}>
                            ₹{obsMed.toFixed(1)} LPA
                          </td>
                          <td style={{ padding: '12px 14px', color: isPos ? '#34D399' : '#F87171', fontWeight: 600 }}>
                            {isPos ? '+' : ''}₹{delta.toFixed(1)} LPA
                          </td>
                        </tr>
                      );
                    })}
              </tbody>
            </table>
          </div>
        </div>

        {/* RIGHT: SKILL DETAIL PANEL (Section 8) */}
        <AnimatePresence mode="wait">
          {skillDetail && (
            <motion.div
              key={activeSkill}
              variants={detailCrossfadeVariants}
              initial="initial"
              animate="animate"
              exit="exit"
              style={{
                background: 'rgba(21, 23, 31, 0.85)',
                border: '1px solid rgba(245, 158, 11, 0.35)',
                borderRadius: '18px',
                padding: '28px',
                display: 'flex',
                flexDirection: 'column',
                gap: '20px',
              }}
            >
            <div>
              <div style={{ fontSize: '0.72rem', color: '#F59E0B', fontWeight: 800, textTransform: 'uppercase', marginBottom: '4px' }}>
                SELECTED SKILL PROFILE
              </div>
              <h2 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: 0 }}>
                {detailTitle}
              </h2>
            </div>

            {/* Plain-English Observation Callout */}
            <div
              style={{
                background: 'rgba(255, 255, 255, 0.03)',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                borderRadius: '12px',
                padding: '16px',
              }}
            >
              <p style={{ fontSize: '0.88rem', color: '#E2E8F0', lineHeight: 1.6, margin: 0 }}>
                Postings containing this competency in the analyzed dataset had an observed median salary of{' '}
                <strong style={{ color: '#FFFFFF' }}>
                  {detailObservedMedian}
                </strong>
                .
              </p>
            </div>

            {/* Quick Metrics */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '14px', borderRadius: '10px', border: '1px solid rgba(255, 255, 255, 0.06)' }}>
                <span style={{ fontSize: '0.72rem', color: '#94A3B8', fontWeight: 600 }}>DEMAND PREVALENCE</span>
                <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#F59E0B', marginTop: '2px' }}>
                  {detailDemandPct.toFixed(1)}%
                </div>
                <span style={{ fontSize: '0.72rem', color: '#64748B' }}>
                  {detailPostings.toLocaleString()} postings
                </span>
              </div>

              <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '14px', borderRadius: '10px', border: '1px solid rgba(255, 255, 255, 0.06)' }}>
                <span style={{ fontSize: '0.72rem', color: '#94A3B8', fontWeight: 600 }}>OBSERVED SALARY DIFF</span>
                <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#34D399', marginTop: '2px' }}>
                  {detailSalaryDiff}
                </div>
                <span style={{ fontSize: '0.72rem', color: '#64748B' }}>vs cohort median</span>
              </div>
            </div>

            {/* Associated Roles */}
            <div>
              <div style={{ fontSize: '0.78rem', color: '#94A3B8', fontWeight: 700, textTransform: 'uppercase', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Briefcase size={14} style={{ color: '#38BDF8' }} />
                <span>Associated Roles</span>
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {detailRoles.length > 0 ? (
                  detailRoles.map((r: string) => (
                    <span
                      key={r}
                      style={{
                        padding: '4px 10px',
                        borderRadius: '8px',
                        background: 'rgba(56, 189, 248, 0.12)',
                        border: '1px solid rgba(56, 189, 248, 0.25)',
                        color: '#BAE6FD',
                        fontSize: '0.78rem',
                        fontWeight: 600,
                      }}
                    >
                      {r}
                    </span>
                  ))
                ) : (
                  <span style={{ color: '#64748B', fontSize: '0.8rem', fontStyle: 'italic' }}>
                    No prominent role clustering observed
                  </span>
                )}
              </div>
            </div>

            {/* Associated Archetypes */}
            <div>
              <div style={{ fontSize: '0.78rem', color: '#94A3B8', fontWeight: 700, textTransform: 'uppercase', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Dna size={14} style={{ color: '#EC4899' }} />
                <span>Associated Market Archetypes</span>
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {detailArchetypes.length > 0 ? (
                  detailArchetypes.map((a: string) => (
                    <span
                      key={a}
                      style={{
                        padding: '4px 10px',
                        borderRadius: '8px',
                        background: 'rgba(236, 72, 153, 0.12)',
                        border: '1px solid rgba(236, 72, 153, 0.25)',
                        color: '#FBCFE8',
                        fontSize: '0.78rem',
                        fontWeight: 600,
                      }}
                    >
                      {a}
                    </span>
                  ))
                ) : (
                  <span style={{ color: '#64748B', fontSize: '0.8rem', fontStyle: 'italic' }}>
                    Generalist cross-archetype distribution
                  </span>
                )}
              </div>
            </div>

            {/* Common Co-occurring Skills */}
            <div>
              <div style={{ fontSize: '0.78rem', color: '#94A3B8', fontWeight: 700, textTransform: 'uppercase', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Layers size={14} style={{ color: '#F59E0B' }} />
                <span>Frequently Co-Occurring Skills</span>
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {detailCombos.length > 0 ? (
                  detailCombos.map((c: string) => (
                    <span
                      key={c}
                      style={{
                        padding: '4px 10px',
                        borderRadius: '8px',
                        background: 'rgba(245, 158, 11, 0.12)',
                        border: '1px solid rgba(245, 158, 11, 0.25)',
                        color: '#FDE68A',
                        fontSize: '0.78rem',
                        fontWeight: 600,
                      }}
                    >
                      + {c}
                    </span>
                  ))
                ) : (
                  <span style={{ color: '#64748B', fontSize: '0.8rem', fontStyle: 'italic' }}>
                    No recurring pairs in dataset
                  </span>
                )}
              </div>
            </div>

            {/* Non-Causal Scientific Notice */}
            <div
              style={{
                background: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid rgba(255, 255, 255, 0.06)',
                borderRadius: '8px',
                padding: '10px 12px',
                fontSize: '0.74rem',
                color: '#64748B',
                lineHeight: 1.45,
              }}
            >
              ℹ <strong>Non-Causal Note:</strong> Having a skill does not directly cause salary to increase.
              These values represent observational differences across job postings specifying this competency.
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>

      <ScientificDisclaimer />
      <SourceFooter />
    </div>
  );
};
