import React from 'react';
import {
  Sparkles,
  ArrowRight,
  Calculator,
  Compass,
  Layers,
  Dna,
  GitCompare,
  BookOpen,
  CheckCircle2,
  ShieldCheck,
  TrendingUp,
  Cpu,
  Database,
  BarChart3,
  HelpCircle,
  Award,
  Zap,
} from 'lucide-react';
import { useMarket } from '../context/MarketContext';

import { motion } from 'framer-motion';
import {
  heroSequenceVariants,
  heroItemVariants,
  containerStaggerVariants,
  itemFadeUpVariants,
} from '../utils/motionTokens';

interface HomePageProps {
  onNavigate: (
    page:
      | 'home'
      | 'calculator'
      | 'explore'
      | 'skills'
      | 'archetypes'
      | 'comparison'
      | 'howitworks'
  ) => void;
}

export const HomePage: React.FC<HomePageProps> = ({ onNavigate }) => {
  const { isUSA, isIndia, setMarket } = useMarket();

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '80px', paddingBottom: '40px' }}>
      {/* ============================================================ */}
      {/* HERO SECTION                                                  */}
      {/* ============================================================ */}
      <motion.section
        variants={heroSequenceVariants}
        initial="hidden"
        animate="visible"
        style={{
          position: 'relative',
          padding: '60px 20px 40px 20px',
          textAlign: 'center',
          maxWidth: '920px',
          margin: '0 auto',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        {/* Soft Radial Lighting Effect */}
        <div
          style={{
            position: 'absolute',
            top: '5%',
            left: '50%',
            transform: 'translateX(-50%)',
            width: '650px',
            height: '350px',
            background:
              'radial-gradient(circle, rgba(139, 92, 246, 0.15) 0%, rgba(56, 189, 248, 0.08) 50%, rgba(0, 0, 0, 0) 75%)',
            filter: 'blur(60px)',
            pointerEvents: 'none',
            zIndex: -1,
          }}
        />

        {/* 1. Eyebrow (0 -> 0.15s) */}
        <motion.div
          variants={heroItemVariants}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '6px 14px',
            borderRadius: '9999px',
            background: 'rgba(139, 92, 246, 0.1)',
            border: '1px solid rgba(139, 92, 246, 0.28)',
            marginBottom: '24px',
          }}
        >
          <Sparkles size={14} style={{ color: '#A78BFA' }} />
          <span
            style={{
              fontSize: '0.75rem',
              fontWeight: 800,
              letterSpacing: '0.12em',
              color: '#C4B5FD',
              textTransform: 'uppercase',
            }}
          >
            JOBINTEL
          </span>
          <span style={{ color: 'rgba(255,255,255,0.2)', fontSize: '0.8rem' }}>•</span>
          <span style={{ fontSize: '0.75rem', color: '#94A3B8', fontWeight: 500 }}>
            Market Intelligence Platform
          </span>
        </motion.div>

        {/* 2. Main Headline (0.10 -> 0.45s) */}
        <motion.h1
          variants={heroItemVariants}
          style={{
            fontSize: 'clamp(2.4rem, 5vw, 3.8rem)',
            fontWeight: 800,
            lineHeight: 1.12,
            letterSpacing: '-0.03em',
            color: '#FFFFFF',
            margin: '0 0 20px 0',
          }}
        >
          Know what your skills <br />
          <span
            style={{
              background: 'linear-gradient(135deg, #A78BFA 0%, #38BDF8 50%, #34D399 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            could be worth.
          </span>
        </motion.h1>

        {/* 3. Supporting Text (0.20 -> 0.50s) */}
        <motion.p
          variants={heroItemVariants}
          style={{
            fontSize: 'clamp(1rem, 2vw, 1.25rem)',
            color: '#94A3B8',
            lineHeight: 1.6,
            maxWidth: '680px',
            margin: '0 0 36px 0',
            fontWeight: 400,
          }}
        >
          Explore salary estimates, valuable skills, and job-market patterns across the USA and
          India powered by real job-market data.
        </motion.p>

        {/* 4 & 5. Primary & Secondary Call to Actions (0.30 -> 0.55s) */}
        <motion.div
          variants={heroItemVariants}
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '16px',
            justifyContent: 'center',
            alignItems: 'center',
          }}
        >
          <motion.button
            type="button"
            onClick={() => onNavigate('calculator')}
            whileHover={{ y: -2, scale: 1.015, boxShadow: '0 12px 34px rgba(139, 92, 246, 0.6)' }}
            whileTap={{ scale: 0.985 }}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '10px',
              padding: '16px 32px',
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #8B5CF6 0%, #6366F1 100%)',
              color: '#FFFFFF',
              fontSize: '1.05rem',
              fontWeight: 700,
              border: 'none',
              cursor: 'pointer',
              boxShadow: '0 8px 28px rgba(139, 92, 246, 0.45)',
              transition: 'all 0.15s ease',
            }}
          >
            <Calculator size={19} />
            <span>Estimate My Salary</span>
            <ArrowRight size={17} />
          </motion.button>

          <motion.button
            type="button"
            onClick={() => onNavigate('explore')}
            whileHover={{ y: -1.5, scale: 1.01, backgroundColor: 'rgba(255, 255, 255, 0.09)' }}
            whileTap={{ scale: 0.985 }}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '10px',
              padding: '16px 28px',
              borderRadius: '12px',
              background: 'rgba(255, 255, 255, 0.05)',
              color: '#F1F5F9',
              fontSize: '1.05rem',
              fontWeight: 600,
              border: '1px solid rgba(255, 255, 255, 0.14)',
              cursor: 'pointer',
              backdropFilter: 'blur(10px)',
              transition: 'all 0.15s ease',
            }}
          >
            <Compass size={19} style={{ color: '#38BDF8' }} />
            <span>Explore the Market</span>
          </motion.button>
        </motion.div>

        {/* 6. Hero Visual / Data Preview enters last (0.40 -> 0.70s) */}
        <motion.div
          variants={heroItemVariants}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '16px',
            marginTop: '32px',
            fontSize: '0.82rem',
            color: '#64748B',
          }}
        >
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span>🇺🇸</span> USA Market (34,036 postings)
          </span>
          <span>•</span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span>🇮🇳</span> India Market (5,859 postings)
          </span>
        </motion.div>
      </motion.section>

      {/* ============================================================ */}
      {/* 3 VALUE PROPOSITIONS                                          */}
      {/* ============================================================ */}
      <section style={{ maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
        <motion.div
          variants={containerStaggerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-40px' }}
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: '24px',
          }}
        >
          {/* Card 1: Salary Estimate */}
          <motion.div
            variants={itemFadeUpVariants}
            whileHover={{ y: -4, borderColor: 'rgba(139, 92, 246, 0.5)', boxShadow: '0 16px 36px rgba(139, 92, 246, 0.18)' }}
            onClick={() => onNavigate('calculator')}
            style={{
              background: 'linear-gradient(145deg, rgba(21, 23, 31, 0.8) 0%, rgba(16, 17, 22, 0.95) 100%)',
              border: '1px solid rgba(139, 92, 246, 0.22)',
              borderRadius: '20px',
              padding: '36px 30px',
              cursor: 'pointer',
              position: 'relative',
              transition: 'border-color 0.2s ease, box-shadow 0.2s ease',
            }}
          >
            <div
              style={{
                width: '52px',
                height: '52px',
                borderRadius: '14px',
                background: 'rgba(139, 92, 246, 0.15)',
                border: '1px solid rgba(139, 92, 246, 0.35)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '22px',
                color: '#A78BFA',
              }}
            >
              <Calculator size={26} />
            </div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '10px' }}>
              Estimate your salary
            </h3>
            <p style={{ fontSize: '0.92rem', color: '#94A3B8', lineHeight: 1.6, margin: '0 0 20px 0' }}>
              Tell us about your role, experience, location, and skills. JobIntel estimates an expected
              salary range from its trained job-market model.
            </p>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                color: '#C4B5FD',
                fontSize: '0.88rem',
                fontWeight: 600,
              }}
            >
              <span>Calculate now</span>
              <ArrowRight size={15} />
            </div>
          </motion.div>

          {/* Card 2: Understand Skills */}
          <motion.div
            variants={itemFadeUpVariants}
            whileHover={{ y: -4, borderColor: 'rgba(245, 158, 11, 0.5)', boxShadow: '0 16px 36px rgba(245, 158, 11, 0.18)' }}
            onClick={() => onNavigate('skills')}
            style={{
              background: 'linear-gradient(145deg, rgba(21, 23, 31, 0.8) 0%, rgba(16, 17, 22, 0.95) 100%)',
              border: '1px solid rgba(245, 158, 11, 0.22)',
              borderRadius: '20px',
              padding: '36px 30px',
              cursor: 'pointer',
              position: 'relative',
              transition: 'border-color 0.2s ease, box-shadow 0.2s ease',
            }}
          >
            <div
              style={{
                width: '52px',
                height: '52px',
                borderRadius: '14px',
                background: 'rgba(245, 158, 11, 0.15)',
                border: '1px solid rgba(245, 158, 11, 0.35)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '22px',
                color: '#FBBF24',
              }}
            >
              <Layers size={26} />
            </div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '10px' }}>
              Understand which skills matter
            </h3>
            <p style={{ fontSize: '0.92rem', color: '#94A3B8', lineHeight: 1.6, margin: '0 0 20px 0' }}>
              Explore skills and combinations that are associated with different salary levels in the
              analyzed job market without confusing causal claims.
            </p>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                color: '#FDE68A',
                fontSize: '0.88rem',
                fontWeight: 600,
              }}
            >
              <span>Explore skills</span>
              <ArrowRight size={15} />
            </div>
          </motion.div>

          {/* Card 3: Discover Patterns */}
          <motion.div
            variants={itemFadeUpVariants}
            whileHover={{ y: -4, borderColor: 'rgba(236, 72, 153, 0.5)', boxShadow: '0 16px 36px rgba(236, 72, 153, 0.18)' }}
            onClick={() => onNavigate('archetypes')}
            style={{
              background: 'linear-gradient(145deg, rgba(21, 23, 31, 0.8) 0%, rgba(16, 17, 22, 0.95) 100%)',
              border: '1px solid rgba(236, 72, 153, 0.22)',
              borderRadius: '20px',
              padding: '36px 30px',
              cursor: 'pointer',
              position: 'relative',
              transition: 'border-color 0.2s ease, box-shadow 0.2s ease',
            }}
          >
            <div
              style={{
                width: '52px',
                height: '52px',
                borderRadius: '14px',
                background: 'rgba(236, 72, 153, 0.15)',
                border: '1px solid rgba(236, 72, 153, 0.35)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '22px',
                color: '#F472B6',
              }}
            >
              <Dna size={26} />
            </div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '10px' }}>
              Discover job-market patterns
            </h3>
            <p style={{ fontSize: '0.92rem', color: '#94A3B8', lineHeight: 1.6, margin: '0 0 20px 0' }}>
              See recurring groups of skills that appear together across real job postings, uncovering
              unsupervised market clusters.
            </p>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                color: '#FBCFE8',
                fontSize: '0.88rem',
                fontWeight: 600,
              }}
            >
              <span>View archetypes</span>
              <ArrowRight size={15} />
            </div>
          </motion.div>
        </motion.div>
      </section>

      {/* ============================================================ */}
      {/* TRUST SECTION                                                 */}
      {/* ============================================================ */}
      <section
        style={{
          maxWidth: '1200px',
          margin: '0 auto',
          width: '100%',
          background: 'rgba(15, 23, 42, 0.5)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          borderRadius: '24px',
          padding: '48px 40px',
        }}
      >
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '40px',
            alignItems: 'center',
          }}
        >
          <div>
            <div
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                color: '#10B981',
                fontSize: '0.78rem',
                fontWeight: 700,
                letterSpacing: '0.08em',
                textTransform: 'uppercase',
                marginBottom: '12px',
              }}
            >
              <ShieldCheck size={16} />
              <span>Verified Data Foundation</span>
            </div>
            <h2
              style={{
                fontSize: '1.85rem',
                fontWeight: 800,
                color: '#FFFFFF',
                letterSpacing: '-0.02em',
                marginBottom: '16px',
                lineHeight: 1.25,
              }}
            >
              Built from real job-market data
            </h2>
            <p style={{ fontSize: '0.96rem', color: '#94A3B8', lineHeight: 1.65, margin: 0 }}>
              JobIntel analyzes thousands of job postings to identify salary patterns, skill
              combinations, and recurring market structures. Rather than guessing, our estimates are
              grounded in certified machine learning models trained on independent labor market cohorts.
            </p>
          </div>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(2, 1fr)',
              gap: '16px',
            }}
          >
            <div
              style={{
                background: 'rgba(21, 23, 31, 0.7)',
                border: '1px solid rgba(255, 255, 255, 0.06)',
                borderRadius: '16px',
                padding: '22px',
              }}
            >
              <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#38BDF8', marginBottom: '4px' }}>
                34,036
              </div>
              <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '4px' }}>
                USA Postings Analyzed
              </div>
              <div style={{ fontSize: '0.74rem', color: '#64748B' }}>
                123 predictors · XGBoost Holdout MAE $36,381
              </div>
            </div>

            <div
              style={{
                background: 'rgba(21, 23, 31, 0.7)',
                border: '1px solid rgba(255, 255, 255, 0.06)',
                borderRadius: '16px',
                padding: '22px',
              }}
            >
              <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#F97316', marginBottom: '4px' }}>
                5,859
              </div>
              <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '4px' }}>
                India Postings Analyzed
              </div>
              <div style={{ fontSize: '0.74rem', color: '#64748B' }}>
                290 predictors · HistGB Holdout MAE ₹3.71 LPA
              </div>
            </div>

            <div
              style={{
                background: 'rgba(21, 23, 31, 0.7)',
                border: '1px solid rgba(255, 255, 255, 0.06)',
                borderRadius: '16px',
                padding: '22px',
              }}
            >
              <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#EC4899', marginBottom: '4px' }}>
                13 Patterns
              </div>
              <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '4px' }}>
                Discovered Archetypes
              </div>
              <div style={{ fontSize: '0.74rem', color: '#64748B' }}>
                7 USA + 6 India PCA & K-Means Clusters
              </div>
            </div>

            <div
              style={{
                background: 'rgba(21, 23, 31, 0.7)',
                border: '1px solid rgba(255, 255, 255, 0.06)',
                borderRadius: '16px',
                padding: '22px',
              }}
            >
              <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#10B981', marginBottom: '4px' }}>
                0 FX
              </div>
              <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '4px' }}>
                Strict Isolation
              </div>
              <div style={{ fontSize: '0.74rem', color: '#64748B' }}>
                Never mixing USD & INR exchange rates
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================================ */}
      {/* HOW IT WORKS PREVIEW                                          */}
      {/* ============================================================ */}
      <section style={{ maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
        <div style={{ textAlign: 'center', marginBottom: '48px' }}>
          <span
            style={{
              fontSize: '0.75rem',
              fontWeight: 800,
              letterSpacing: '0.1em',
              color: '#38BDF8',
              textTransform: 'uppercase',
            }}
          >
            Simple Guided Journey
          </span>
          <h2
            style={{
              fontSize: '2.1rem',
              fontWeight: 800,
              color: '#FFFFFF',
              letterSpacing: '-0.02em',
              marginTop: '8px',
            }}
          >
            How JobIntel works
          </h2>
          <p style={{ fontSize: '0.98rem', color: '#94A3B8', maxWidth: '580px', margin: '12px auto 0' }}>
            We translate complex predictive modeling into three clear, transparent steps for every
            professional.
          </p>
        </div>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '24px',
            position: 'relative',
          }}
        >
          {/* Step 1 */}
          <div
            style={{
              background: 'rgba(21, 23, 31, 0.65)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '20px',
              padding: '36px 28px',
              position: 'relative',
            }}
          >
            <div
              style={{
                fontSize: '2.5rem',
                fontWeight: 900,
                color: 'rgba(139, 92, 246, 0.35)',
                lineHeight: 1,
                marginBottom: '16px',
                fontFamily: 'var(--font-mono)',
              }}
            >
              01
            </div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '10px' }}>
              Tell us about yourself
            </h3>
            <p style={{ fontSize: '0.9rem', color: '#94A3B8', lineHeight: 1.6, margin: 0 }}>
              Select your market (USA or India), role, years of experience, location, and technical
              skills using simple chips.
            </p>
          </div>

          {/* Step 2 */}
          <div
            style={{
              background: 'rgba(21, 23, 31, 0.65)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '20px',
              padding: '36px 28px',
              position: 'relative',
            }}
          >
            <div
              style={{
                fontSize: '2.5rem',
                fontWeight: 900,
                color: 'rgba(56, 189, 248, 0.35)',
                lineHeight: 1,
                marginBottom: '16px',
                fontFamily: 'var(--font-mono)',
              }}
            >
              02
            </div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '10px' }}>
              JobIntel analyzes your profile
            </h3>
            <p style={{ fontSize: '0.9rem', color: '#94A3B8', lineHeight: 1.6, margin: 0 }}>
              Our server-side regression model evaluates your background against thousands of audited
              postings in that specific market.
            </p>
          </div>

          {/* Step 3 */}
          <div
            style={{
              background: 'rgba(21, 23, 31, 0.65)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '20px',
              padding: '36px 28px',
              position: 'relative',
            }}
          >
            <div
              style={{
                fontSize: '2.5rem',
                fontWeight: 900,
                color: 'rgba(52, 211, 153, 0.35)',
                lineHeight: 1,
                marginBottom: '16px',
                fontFamily: 'var(--font-mono)',
              }}
            >
              03
            </div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '10px' }}>
              Explore your estimate & insights
            </h3>
            <p style={{ fontSize: '0.9rem', color: '#94A3B8', lineHeight: 1.6, margin: 0 }}>
              Receive an estimated annual salary, understand why it was produced, discover the skill
              archetype you resemble, and view error margins.
            </p>
          </div>
        </div>

        <div style={{ textAlign: 'center', marginTop: '36px' }}>
          <button
            type="button"
            onClick={() => onNavigate('howitworks')}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              padding: '12px 24px',
              borderRadius: '10px',
              background: 'rgba(255, 255, 255, 0.04)',
              border: '1px solid rgba(255, 255, 255, 0.12)',
              color: '#F1F5F9',
              fontSize: '0.92rem',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.08)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.04)';
            }}
          >
            <BookOpen size={16} style={{ color: '#38BDF8' }} />
            <span>See how it works (Methodology & Architecture)</span>
            <ArrowRight size={14} />
          </button>
        </div>
      </section>

      {/* ============================================================ */}
      {/* WHY JOBINTEL SECTION                                          */}
      {/* ============================================================ */}
      <section style={{ maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <h2
            style={{
              fontSize: '2rem',
              fontWeight: 800,
              color: '#FFFFFF',
              letterSpacing: '-0.02em',
            }}
          >
            Why use JobIntel?
          </h2>
          <p style={{ fontSize: '0.95rem', color: '#94A3B8', marginTop: '8px' }}>
            Built with strict analytical discipline to deliver trustworthy, transparent intelligence.
          </p>
        </div>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: '24px',
          }}
        >
          <div
            style={{
              background: 'rgba(21, 23, 31, 0.7)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '18px',
              padding: '30px',
            }}
          >
            <div
              style={{
                display: 'inline-flex',
                padding: '10px',
                borderRadius: '12px',
                background: 'rgba(56, 189, 248, 0.12)',
                color: '#38BDF8',
                marginBottom: '18px',
              }}
            >
              <Database size={22} />
            </div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '10px' }}>
              REAL DATA
            </h3>
            <p style={{ fontSize: '0.9rem', color: '#94A3B8', lineHeight: 1.6, margin: 0 }}>
              Built directly from 39,895 real job postings across the United States and India. Never
              fabricated, synthetically generated, or inflated.
            </p>
          </div>

          <div
            style={{
              background: 'rgba(21, 23, 31, 0.7)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '18px',
              padding: '30px',
            }}
          >
            <div
              style={{
                display: 'inline-flex',
                padding: '10px',
                borderRadius: '12px',
                background: 'rgba(249, 115, 22, 0.12)',
                color: '#F97316',
                marginBottom: '18px',
              }}
            >
              <GitCompare size={22} />
            </div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '10px' }}>
              MARKET-SPECIFIC
            </h3>
            <p style={{ fontSize: '0.9rem', color: '#94A3B8', lineHeight: 1.6, margin: 0 }}>
              USA and India operate on fundamentally different salary models, currencies, and
              taxonomies. We strictly isolate each market with zero foreign exchange rate conversion.
            </p>
          </div>

          <div
            style={{
              background: 'rgba(21, 23, 31, 0.7)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '18px',
              padding: '30px',
            }}
          >
            <div
              style={{
                display: 'inline-flex',
                padding: '10px',
                borderRadius: '12px',
                background: 'rgba(16, 185, 129, 0.12)',
                color: '#10B981',
                marginBottom: '18px',
              }}
            >
              <ShieldCheck size={22} />
            </div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '10px' }}>
              TRANSPARENT
            </h3>
            <p style={{ fontSize: '0.9rem', color: '#94A3B8', lineHeight: 1.6, margin: 0 }}>
              You can see how your estimate was produced, inspect historical test holdout errors, and
              view full model limitations on demand.
            </p>
          </div>
        </div>
      </section>

      {/* ============================================================ */}
      {/* EXPLORE MODULES / PRODUCT DIRECTORY (Section 28 Flow)         */}
      {/* ============================================================ */}
      <section
        style={{
          maxWidth: '1200px',
          margin: '0 auto',
          width: '100%',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
          gap: '20px',
        }}
      >
        <div
          onClick={() => onNavigate('calculator')}
          style={{
            background: 'rgba(139, 92, 246, 0.08)',
            border: '1px solid rgba(139, 92, 246, 0.3)',
            borderRadius: '16px',
            padding: '24px',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-2px)';
            e.currentTarget.style.borderColor = 'rgba(139, 92, 246, 0.6)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.borderColor = 'rgba(139, 92, 246, 0.3)';
          }}
        >
          <div style={{ fontSize: '0.75rem', fontWeight: 800, color: '#C4B5FD', textTransform: 'uppercase', marginBottom: '8px' }}>
            SALARY ESTIMATOR
          </div>
          <div style={{ fontSize: '1.15rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '12px' }}>
            How much could you earn?
          </div>
          <div style={{ color: '#A78BFA', fontSize: '0.85rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span>Start Salary Calculator</span>
            <ArrowRight size={14} />
          </div>
        </div>

        <div
          onClick={() => onNavigate('skills')}
          style={{
            background: 'rgba(245, 158, 11, 0.08)',
            border: '1px solid rgba(245, 158, 11, 0.3)',
            borderRadius: '16px',
            padding: '24px',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-2px)';
            e.currentTarget.style.borderColor = 'rgba(245, 158, 11, 0.6)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.borderColor = 'rgba(245, 158, 11, 0.3)';
          }}
        >
          <div style={{ fontSize: '0.75rem', fontWeight: 800, color: '#FDE68A', textTransform: 'uppercase', marginBottom: '8px' }}>
            SKILL INSIGHTS
          </div>
          <div style={{ fontSize: '1.15rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '12px' }}>
            What skills stand out?
          </div>
          <div style={{ color: '#F59E0B', fontSize: '0.85rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span>Explore Skills</span>
            <ArrowRight size={14} />
          </div>
        </div>

        <div
          onClick={() => onNavigate('archetypes')}
          style={{
            background: 'rgba(236, 72, 153, 0.08)',
            border: '1px solid rgba(236, 72, 153, 0.3)',
            borderRadius: '16px',
            padding: '24px',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-2px)';
            e.currentTarget.style.borderColor = 'rgba(236, 72, 153, 0.6)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.borderColor = 'rgba(236, 72, 153, 0.3)';
          }}
        >
          <div style={{ fontSize: '0.75rem', fontWeight: 800, color: '#FBCFE8', textTransform: 'uppercase', marginBottom: '8px' }}>
            MARKET TAXONOMY
          </div>
          <div style={{ fontSize: '1.15rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '12px' }}>
            What does the market look like?
          </div>
          <div style={{ color: '#EC4899', fontSize: '0.85rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span>Explore Archetypes</span>
            <ArrowRight size={14} />
          </div>
        </div>

        <div
          onClick={() => onNavigate('comparison')}
          style={{
            background: 'rgba(56, 189, 248, 0.08)',
            border: '1px solid rgba(56, 189, 248, 0.3)',
            borderRadius: '16px',
            padding: '24px',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-2px)';
            e.currentTarget.style.borderColor = 'rgba(56, 189, 248, 0.6)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.borderColor = 'rgba(56, 189, 248, 0.3)';
          }}
        >
          <div style={{ fontSize: '0.75rem', fontWeight: 800, color: '#BAE6FD', textTransform: 'uppercase', marginBottom: '8px' }}>
            CROSS-MARKET
          </div>
          <div style={{ fontSize: '1.15rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '12px' }}>
            USA vs India: Two Markets
          </div>
          <div style={{ color: '#38BDF8', fontSize: '0.85rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span>Compare Markets</span>
            <ArrowRight size={14} />
          </div>
        </div>
      </section>

      {/* ============================================================ */}
      {/* FINAL BOTTOM CALL TO ACTION BANNER                            */}
      {/* ============================================================ */}
      <section
        style={{
          maxWidth: '1200px',
          margin: '0 auto',
          width: '100%',
          background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.18) 0%, rgba(56, 189, 248, 0.1) 100%)',
          border: '1px solid rgba(139, 92, 246, 0.35)',
          borderRadius: '24px',
          padding: '48px 36px',
          textAlign: 'center',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '20px',
        }}
      >
        <h2 style={{ fontSize: '2.1rem', fontWeight: 800, color: '#FFFFFF', margin: 0 }}>
          Ready to discover your estimated compensation?
        </h2>
        <p style={{ fontSize: '1rem', color: '#CBD5E1', maxWidth: '600px', margin: 0, lineHeight: 1.6 }}>
          It takes less than 60 seconds to configure your profile and receive transparent, market-backed
          salary patterns.
        </p>
        <button
          type="button"
          onClick={() => onNavigate('calculator')}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '10px',
            padding: '16px 36px',
            borderRadius: '12px',
            background: 'linear-gradient(135deg, #8B5CF6 0%, #6366F1 100%)',
            color: '#FFFFFF',
            fontSize: '1.05rem',
            fontWeight: 700,
            border: 'none',
            cursor: 'pointer',
            boxShadow: '0 8px 24px rgba(139, 92, 246, 0.45)',
            marginTop: '8px',
          }}
        >
          <Calculator size={19} />
          <span>Estimate My Salary</span>
          <ArrowRight size={17} />
        </button>
      </section>
    </div>
  );
};
