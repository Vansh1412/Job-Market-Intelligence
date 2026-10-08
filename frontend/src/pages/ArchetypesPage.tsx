import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { ArchetypeItem } from '../types';
import { useMarket } from '../context/MarketContext';
import { ScientificDisclaimer } from '../components/ScientificDisclaimer';
import { SourceFooter } from '../components/SourceFooter';
import {
  Dna,
  ShieldAlert,
  CheckCircle2,
  TrendingUp,
  Layers,
  Award,
  Sparkles,
  ChevronDown,
  ChevronUp,
  Info,
  Briefcase,
  DollarSign,
  ArrowRight,
} from 'lucide-react';
import { AnimatePresence, motion } from 'framer-motion';
import {
  containerStaggerVariants,
  detailCrossfadeVariants,
  heroItemVariants,
  heroSequenceVariants,
  itemFadeUpVariants,
} from '../utils/motionTokens';

interface ArchetypesPageProps {
  onNavigate?: (page: string) => void;
}

export const ArchetypesPage: React.FC<ArchetypesPageProps> = ({ onNavigate }) => {
  const { market, setMarket, isUSA, isIndia, currencySymbol } = useMarket();

  const [archetypes, setArchetypes] = useState<ArchetypeItem[]>([]);
  const [selectedArch, setSelectedArch] = useState<ArchetypeItem | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [showTechnicalExpl, setShowTechnicalExpl] = useState<boolean>(false);

  useEffect(() => {
    let isMounted = true;
    async function loadArchetypes() {
      setLoading(true);
      try {
        if (isUSA) {
          const list = await api.getUsaArchetypes();
          if (isMounted) {
            setArchetypes(list);
            if (list.length > 0) setSelectedArch(list[5] || list[0]);
          }
        } else {
          const list = await api.getIndiaArchetypes();
          if (isMounted) {
            setArchetypes(list);
            if (list.length > 0) setSelectedArch(list[0]);
          }
        }
      } catch (err) {
        console.error('Failed to load archetypes', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadArchetypes();
    return () => {
      isMounted = false;
    };
  }, [market]);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '80px 20px', color: '#94A3B8' }}>
        <div className="ji-spinner" style={{ margin: '0 auto 16px' }} />
        <p>Loading {market} skill archetypes...</p>
      </div>
    );
  }

  const primaryAccent = '#EC4899';

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
            background: 'rgba(236, 72, 153, 0.12)',
            border: '1px solid rgba(236, 72, 153, 0.3)',
            marginBottom: '12px',
          }}
        >
          <Sparkles size={14} style={{ color: primaryAccent }} />
          <span
            style={{
              fontSize: '0.75rem',
              fontWeight: 700,
              letterSpacing: '0.08em',
              color: '#FBCFE8',
              textTransform: 'uppercase',
            }}
          >
            {isUSA ? 'UNSUPERVISED TAXONOMY · 7 SKILL ARCHETYPES' : 'UNSUPERVISED TAXONOMY · 6 SKILL ARCHETYPES'}
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
          How does the job market cluster?
        </motion.h1>
        <motion.p
          variants={heroItemVariants}
          style={{ fontSize: '1rem', color: '#94A3B8', maxWidth: '720px', margin: 0, lineHeight: 1.5 }}
        >
          JobIntel identifies recurring groups of skills that frequently appear together across job
          postings. These represent skill-based market patterns rather than formal occupations.
        </motion.p>
      </motion.div>

      {/* Main Grid: Archetype Cards on Left, Detail on Right */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1.2fr 1fr',
          gap: '24px',
          alignItems: 'start',
        }}
      >
        {/* LEFT: ARCHETYPE CARDS */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#FFFFFF', margin: 0 }}>
              {isUSA ? 'The 7 Discovered USA Skill Patterns' : 'The 6 Discovered India Skill Patterns'}
            </h3>
            <span style={{ fontSize: '0.75rem', color: '#64748B' }}>
              Select a card to inspect signature skills
            </span>
          </div>

          <motion.div
            variants={containerStaggerVariants}
            initial="initial"
            animate="animate"
            style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}
          >
            {archetypes.map((arch, idx) => {
              const isSel =
                selectedArch?.code === arch.code || selectedArch?.archetype_id === arch.archetype_id;
              const salaryDisplay = isUSA
                ? `$${Math.round(arch.median_salary || arch.typical_salary || 180000).toLocaleString()}`
                : `₹${(arch.median_salary_lpa || 12.0).toFixed(1)} LPA`;

              return (
                <motion.div
                  key={idx}
                  variants={itemFadeUpVariants}
                  whileHover={{ y: -2 }}
                  transition={{ duration: 0.15 }}
                  onClick={() => setSelectedArch(arch)}
                  style={{
                    background: isSel
                      ? `linear-gradient(145deg, rgba(20, 24, 38, 0.95) 0%, ${arch.color || '#EC4899'}18 100%)`
                      : 'rgba(15, 23, 42, 0.65)',
                    border: isSel
                      ? `2px solid ${arch.color || '#EC4899'}`
                      : '1px solid rgba(255, 255, 255, 0.08)',
                    borderRadius: '16px',
                    padding: '20px',
                    cursor: 'pointer',
                    boxShadow: isSel ? `0 8px 24px ${(arch.color || '#EC4899')}30` : 'none',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div
                        style={{
                          width: '10px',
                          height: '10px',
                          borderRadius: '50%',
                          background: arch.color || '#EC4899',
                        }}
                      />
                      <h4 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#FFFFFF', margin: 0 }}>
                        {arch.name}
                      </h4>
                    </div>

                    <span
                      style={{
                        fontSize: '0.95rem',
                        fontWeight: 800,
                        color: isUSA ? '#38BDF8' : '#F97316',
                        fontFamily: 'var(--font-mono)',
                      }}
                    >
                      {salaryDisplay}
                    </span>
                  </div>

                  <p style={{ fontSize: '0.84rem', color: '#94A3B8', lineHeight: 1.5, margin: '0 0 12px 0' }}>
                    {arch.definition || arch.desc || 'Postings centered around a common cluster of technical competencies.'}
                  </p>

                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {(arch.signature_skills || arch.top_skills || []).slice(0, 4).map((sk: string) => (
                        <span
                          key={sk}
                          style={{
                            padding: '3px 8px',
                            borderRadius: '6px',
                            background: 'rgba(255, 255, 255, 0.04)',
                            border: '1px solid rgba(255, 255, 255, 0.08)',
                            color: '#CBD5E1',
                            fontSize: '0.74rem',
                          }}
                        >
                          {sk}
                        </span>
                      ))}
                    </div>

                    <span style={{ fontSize: '0.75rem', color: '#64748B' }}>
                      {arch.postings ? `${arch.postings.toLocaleString()} postings` : 'Cluster support'}
                    </span>
                  </div>
                </motion.div>
              );
            })}
          </motion.div>
        </div>

        {/* RIGHT: ARCHETYPE DETAIL INSPECTION */}
        <AnimatePresence mode="wait">
          {selectedArch && (
            <motion.div
              key={selectedArch.code || selectedArch.name}
              variants={detailCrossfadeVariants}
              initial="initial"
              animate="animate"
              exit="exit"
              style={{
                background: 'rgba(21, 23, 31, 0.85)',
                border: `1px solid ${(selectedArch.color || '#EC4899')}40`,
                borderRadius: '20px',
                padding: '28px',
                display: 'flex',
                flexDirection: 'column',
                gap: '22px',
                position: 'sticky',
                top: '90px',
              }}
            >
            <div>
              <div style={{ fontSize: '0.74rem', color: selectedArch.color || '#EC4899', fontWeight: 800, textTransform: 'uppercase', marginBottom: '4px' }}>
                ARCHETYPE DETAIL VIEW
              </div>
              <h2 style={{ fontSize: '1.6rem', fontWeight: 900, color: '#FFFFFF', margin: '0 0 8px 0' }}>
                {selectedArch.name}
              </h2>
              <p style={{ fontSize: '0.88rem', color: '#CBD5E1', lineHeight: 1.6, margin: 0 }}>
                {selectedArch.definition || selectedArch.desc}
              </p>
            </div>

            {/* Metrics Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '14px', borderRadius: '12px', border: '1px solid rgba(255, 255, 255, 0.06)' }}>
                <span style={{ fontSize: '0.72rem', color: '#94A3B8', fontWeight: 600 }}>TYPICAL SALARY LEVEL</span>
                <div style={{ fontSize: '1.35rem', fontWeight: 800, color: '#FFFFFF', marginTop: '2px', fontFamily: 'var(--font-mono)' }}>
                  {isUSA
                    ? `$${Math.round(selectedArch.median_salary || selectedArch.typical_salary || 180000).toLocaleString()}`
                    : `₹${(selectedArch.median_salary_lpa || 12.0).toFixed(1)} LPA`}
                </div>
                <span style={{ fontSize: '0.72rem', color: '#64748B' }}>Observed median</span>
              </div>

              <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '14px', borderRadius: '12px', border: '1px solid rgba(255, 255, 255, 0.06)' }}>
                <span style={{ fontSize: '0.72rem', color: '#94A3B8', fontWeight: 600 }}>CLUSTER SIZE</span>
                <div style={{ fontSize: '1.35rem', fontWeight: 800, color: '#38BDF8', marginTop: '2px' }}>
                  {selectedArch.postings ? selectedArch.postings.toLocaleString() : 'N/A'}
                </div>
                <span style={{ fontSize: '0.72rem', color: '#64748B' }}>
                  {selectedArch.pct_cohort ? `${selectedArch.pct_cohort.toFixed(1)}% of cohort` : 'postings in dataset'}
                </span>
              </div>
            </div>

            {/* Top Signature Skills */}
            <div>
              <div style={{ fontSize: '0.78rem', color: '#94A3B8', fontWeight: 700, textTransform: 'uppercase', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Layers size={14} style={{ color: '#F59E0B' }} />
                <span>Top Signature Skills in Pattern</span>
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {(selectedArch.signature_skills || selectedArch.top_skills || []).map((s: string) => (
                  <span
                    key={s}
                    style={{
                      padding: '5px 12px',
                      borderRadius: '8px',
                      background: 'rgba(245, 158, 11, 0.14)',
                      border: '1px solid rgba(245, 158, 11, 0.3)',
                      color: '#FDE68A',
                      fontSize: '0.8rem',
                      fontWeight: 600,
                    }}
                  >
                    {s}
                  </span>
                ))}
              </div>
            </div>

            {/* Common Roles Represented */}
            <div>
              <div style={{ fontSize: '0.78rem', color: '#94A3B8', fontWeight: 700, textTransform: 'uppercase', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Briefcase size={14} style={{ color: '#38BDF8' }} />
                <span>Common Associated Roles</span>
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {(selectedArch.top_roles || ['Software Engineer', 'Senior Developer', 'Architect']).map((r: string) => (
                  <span
                    key={r}
                    style={{
                      padding: '5px 12px',
                      borderRadius: '8px',
                      background: 'rgba(56, 189, 248, 0.12)',
                      border: '1px solid rgba(56, 189, 248, 0.25)',
                      color: '#BAE6FD',
                      fontSize: '0.8rem',
                      fontWeight: 600,
                    }}
                  >
                    {r}
                  </span>
                ))}
              </div>
            </div>

            {/* Specialized Sample Notice for India Big Data & SAP */}
            {isIndia &&
              (selectedArch.name.includes('Big Data') || selectedArch.name.includes('SAP')) && (
                <div
                  style={{
                    fontSize: '0.75rem',
                    color: '#FBBF24',
                    background: 'rgba(251, 191, 36, 0.08)',
                    border: '1px solid rgba(251, 191, 36, 0.25)',
                    padding: '8px 12px',
                    borderRadius: '8px',
                    lineHeight: 1.45,
                  }}
                >
                  ℹ <strong>Sample Size Advisory:</strong> Specialized archetype with smaller empirical
                  sample (N={selectedArch.name.includes('SAP') ? 125 : 198} postings in cohort). Error
                  margin expands proportionally due to lower holdout density.
                </div>
              )}

            {/* Expandable Technical Explanation */}
            <div
              style={{
                border: '1px solid rgba(255, 255, 255, 0.08)',
                borderRadius: '12px',
                background: 'rgba(0, 0, 0, 0.25)',
                overflow: 'hidden',
              }}
            >
              <button
                type="button"
                onClick={() => setShowTechnicalExpl((prev) => !prev)}
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  background: 'none',
                  border: 'none',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  color: '#CBD5E1',
                  fontSize: '0.82rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                <span>How was this group discovered? (Clustering methodology)</span>
                {showTechnicalExpl ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
              </button>

              {showTechnicalExpl && (
                <div
                  style={{
                    padding: '14px 16px',
                    borderTop: '1px solid rgba(255, 255, 255, 0.08)',
                    fontSize: '0.78rem',
                    color: '#94A3B8',
                    lineHeight: 1.6,
                  }}
                >
                  PCA + KMeans clustering was applied to the selected skill matrix. The number of
                  clusters was selected using multiple separation and stability criteria.
                  <br /><br />
                  For USA: K=7 clusters across 15 continuous PCA dimensions (Mean Adjusted Rand Index ARI = 0.7901 across resamples).
                  <br />
                  For India: K=6 clusters across 15 Centered Covariance PCA dimensions (Mean ARI = 0.8035 across resamples).
                </div>
              )}
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
