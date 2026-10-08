import React, { useEffect, useState, useMemo } from 'react';
import { api } from '../services/api';
import { PredictionOptions, PredictionResult, SkillItem } from '../types';
import { useMarket } from '../context/MarketContext';
import { ScientificDisclaimer } from '../components/ScientificDisclaimer';
import { SourceFooter } from '../components/SourceFooter';
import {
  Sparkles,
  ArrowRight,
  ArrowLeft,
  Check,
  CheckCircle2,
  AlertTriangle,
  RotateCcw,
  Search,
  Briefcase,
  MapPin,
  Clock,
  Layers,
  Award,
  Zap,
  Info,
  TrendingUp,
  Globe,
  Sliders,
  HelpCircle,
  ChevronDown,
  ChevronUp,
  Compass,
  GitCompare,
  X,
} from 'lucide-react';
import { AnimatePresence, motion } from 'framer-motion';
import {
  wizardSlideVariants,
  resultRevealVariants,
  itemFadeUpVariants,
} from '../utils/motionTokens';

interface PredictorPageProps {
  onNavigate?: (page: string) => void;
}

export const PredictorPage: React.FC<PredictorPageProps> = ({ onNavigate }) => {
  const { market, setMarket, isUSA, isIndia, currencySymbol, formatSalary } = useMarket();

  // Wizard Step: 1 (Country) to 7 (Result)
  const [step, setStep] = useState<number>(1);
  const [direction, setDirection] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(true);
  const [analyzing, setAnalyzing] = useState<boolean>(false);
  const [options, setOptions] = useState<PredictionOptions | null>(null);

  // Evaluator Mode Accordion
  const [showEvaluatorDetails, setShowEvaluatorDetails] = useState<boolean>(false);

  // -------------------------------------------------------------
  // USER INPUT STATE
  // -------------------------------------------------------------
  // USA Inputs
  const [usaRole, setUsaRole] = useState<string>('ML / AI Engineer');
  const [usaExpYears, setUsaExpYears] = useState<number>(5);
  const [usaCity, setUsaCity] = useState<string>('San Francisco');
  const [usaWorkMode, setUsaWorkMode] = useState<'Remote' | 'Hybrid' | 'On-site'>('Remote');
  const [usaSkills, setUsaSkills] = useState<string[]>([
    'skill_python',
    'skill_machine_learning',
    'skill_aws',
  ]);

  // India Inputs
  const [indiaRole, setIndiaRole] = useState<string>('Data Engineer');
  const [indiaExpYears, setIndiaExpYears] = useState<number>(5);
  const [indiaCity, setIndiaCity] = useState<string>('Bengaluru');
  const [indiaWorkMode, setIndiaWorkMode] = useState<string>('Hybrid');
  const [indiaSkills, setIndiaSkills] = useState<string[]>([
    'skill_python',
    'skill_spark',
    'skill_sql',
    'skill_aws',
  ]);

  // Search & Filter State
  const [roleSearch, setRoleSearch] = useState<string>('');
  const [citySearch, setCitySearch] = useState<string>('');
  const [skillSearch, setSkillSearch] = useState<string>('');
  const [skillCategory, setSkillCategory] = useState<string>('All');

  // Prediction Result
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [predictionError, setPredictionError] = useState<string | null>(null);

  // Helper: map experience years to USA seniority
  const usaSeniority = useMemo(() => {
    if (usaExpYears <= 2) return 'Entry';
    if (usaExpYears <= 5) return 'Mid';
    if (usaExpYears <= 9) return 'Senior';
    if (usaExpYears <= 14) return 'Lead';
    return 'Principal';
  }, [usaExpYears]);

  // Helper: human readable skill label
  const formatSkillLabel = (rawName: string) => {
    let cleaned = rawName.replace(/^skill_/, '');
    cleaned = cleaned.replace(/_/g, ' ');
    // Title Case acronyms
    if (cleaned.toLowerCase() === 'sql') return 'SQL';
    if (cleaned.toLowerCase() === 'aws') return 'AWS';
    if (cleaned.toLowerCase() === 'gcp') return 'GCP';
    if (cleaned.toLowerCase() === 'etl') return 'ETL';
    if (cleaned.toLowerCase() === 'api') return 'API';
    if (cleaned.toLowerCase() === 'ci cd') return 'CI/CD';
    if (cleaned.toLowerCase() === 'mlops') return 'MLOps';
    if (cleaned.toLowerCase() === 'ai') return 'AI';
    if (cleaned.toLowerCase() === 'llm') return 'LLM';
    return cleaned
      .split(' ')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  // Load options for current market
  useEffect(() => {
    let isMounted = true;
    async function loadOptions() {
      setLoading(true);
      setResult(null);
      setPredictionError(null);
      try {
        if (isUSA) {
          const opts = await api.getUsaOptions();
          if (isMounted) setOptions(opts);
        } else {
          const opts = await api.getIndiaOptions();
          if (isMounted) setOptions(opts);
        }
      } catch (err) {
        console.error('Failed to load market options:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadOptions();
    return () => {
      isMounted = false;
    };
  }, [market]);

  // Active skills based on market
  const activeSkills = isUSA ? usaSkills : indiaSkills;

  const toggleSkill = (rawKey: string) => {
    if (isUSA) {
      setUsaSkills((prev) =>
        prev.includes(rawKey) ? prev.filter((s) => s !== rawKey) : [...prev, rawKey]
      );
    } else {
      setIndiaSkills((prev) =>
        prev.includes(rawKey) ? prev.filter((s) => s !== rawKey) : [...prev, rawKey]
      );
    }
  };

  // Filtered skills list
  const filteredSkills = useMemo(() => {
    const list = options?.skills || [];
    return list.filter((s) => {
      const matchSearch =
        s.name.toLowerCase().includes(skillSearch.toLowerCase()) ||
        (s.raw_key && s.raw_key.toLowerCase().includes(skillSearch.toLowerCase()));
      const matchCategory =
        skillCategory === 'All' || !s.category || s.category === skillCategory;
      return matchSearch && matchCategory;
    });
  }, [options, skillSearch, skillCategory]);

  // Categories extracted from skills
  const availableCategories = useMemo(() => {
    const cats = new Set<string>();
    cats.add('All');
    (options?.skills || []).forEach((s) => {
      if (s.category) cats.add(s.category);
    });
    return Array.from(cats);
  }, [options]);

  // Execute prediction when transitioning to Step 7
  const runPrediction = async () => {
    setAnalyzing(true);
    setPredictionError(null);
    setStep(7);
    try {
      if (isUSA) {
        const res = await api.predictUsaSalary({
          role_family: usaRole,
          seniority: usaSeniority,
          city_clean: usaCity,
          is_remote: usaWorkMode === 'Remote',
          selected_skills: usaSkills,
        });
        setResult(res);
      } else {
        const res = await api.predictIndiaSalary({
          normalized_role: indiaRole,
          experience_midpoint_years: Number(indiaExpYears),
          experience_range_years: 2.0,
          city_grouped: indiaCity,
          work_mode: indiaWorkMode,
          selected_skills: indiaSkills,
        });
        setResult(res);
      }
    } catch (err: any) {
      console.error('Prediction failed:', err);
      setPredictionError(err?.message || 'Unable to generate salary estimate from the market model. Please verify your inputs and try again.');
    } finally {
      // Smooth experience feel
      setTimeout(() => {
        setAnalyzing(false);
      }, 350);
    }
  };

  const WIZARD_STEPS = [
    { num: 1, label: 'Country' },
    { num: 2, label: 'Role' },
    { num: 3, label: 'Experience' },
    { num: 4, label: 'Location' },
    { num: 5, label: 'Skills' },
    { num: 6, label: 'Work Mode' },
    { num: 7, label: 'Result' },
  ];

  return (
    <div style={{ maxWidth: '960px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '32px' }}>
      {/* Wizard Header Bar */}
      <div style={{ textAlign: 'center', marginBottom: '8px' }}>
        <div
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
          <Sparkles size={14} style={{ color: isUSA ? '#38BDF8' : '#F97316' }} />
          <span
            style={{
              fontSize: '0.75rem',
              fontWeight: 700,
              letterSpacing: '0.08em',
              color: isUSA ? '#BAE6FD' : '#FED7AA',
              textTransform: 'uppercase',
            }}
          >
            {isUSA ? 'USA Labor Market Model' : 'India Labor Market Model'}
          </span>
        </div>
        <h1
          style={{
            fontSize: 'clamp(1.8rem, 3.5vw, 2.5rem)',
            fontWeight: 800,
            color: '#FFFFFF',
            letterSpacing: '-0.02em',
            margin: '0 0 8px 0',
          }}
        >
          {step === 7 ? 'Your Salary Estimate' : 'Estimate Your Salary'}
        </h1>
        <p style={{ fontSize: '0.95rem', color: '#94A3B8', margin: 0 }}>
          {step === 7
            ? 'Based on patterns learned from thousands of real job postings.'
            : 'A guided 6-step assessment powered by certified machine-learning market models.'}
        </p>
      </div>

      {/* Progress Indicator */}
      <div
        style={{
          background: 'rgba(21, 23, 31, 0.8)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          borderRadius: '16px',
          padding: '16px 20px',
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            position: 'relative',
          }}
        >
          {/* Interpolated Progress Bar Line */}
          <div
            style={{
              position: 'absolute',
              top: '16px',
              left: '8%',
              right: '8%',
              height: '2px',
              background: 'rgba(255, 255, 255, 0.08)',
              zIndex: 1,
            }}
          >
            <div
              style={{
                height: '100%',
                width: `${((Math.min(step, 6) - 1) / 5) * 100}%`,
                background: isUSA ? '#38BDF8' : '#F97316',
                transition: 'width 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
              }}
            />
          </div>

          {WIZARD_STEPS.map((s) => {
            const isCompleted = step > s.num;
            const isCurrent = step === s.num;
            const accentColor = isUSA ? '#38BDF8' : '#F97316';

            return (
              <div
                key={s.num}
                onClick={() => {
                  if (s.num < step || s.num === 1) {
                    setDirection(s.num > step ? 1 : -1);
                    setStep(s.num);
                  }
                }}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: '6px',
                  cursor: s.num <= step ? 'pointer' : 'default',
                  flex: 1,
                  position: 'relative',
                  zIndex: 2,
                }}
              >
                <div
                  style={{
                    width: '32px',
                    height: '32px',
                    borderRadius: '50%',
                    background: isCurrent
                      ? accentColor
                      : isCompleted
                      ? 'rgba(255, 255, 255, 0.15)'
                      : 'rgba(255, 255, 255, 0.04)',
                    border: isCurrent
                      ? `2px solid #FFFFFF`
                      : isCompleted
                      ? `1px solid ${accentColor}`
                      : '1px solid rgba(255, 255, 255, 0.1)',
                    color: isCurrent ? '#000000' : isCompleted ? accentColor : '#64748B',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontWeight: 700,
                    fontSize: '0.8rem',
                    transition: 'all 0.2s ease',
                    boxShadow: isCurrent ? `0 0 14px ${accentColor}80` : 'none',
                  }}
                >
                  {isCompleted ? <Check size={16} /> : s.num}
                </div>
                <span
                  style={{
                    fontSize: '0.72rem',
                    fontWeight: isCurrent ? 700 : 500,
                    color: isCurrent ? '#FFFFFF' : isCompleted ? '#CBD5E1' : '#64748B',
                    textAlign: 'center',
                  }}
                >
                  {s.label}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* ============================================================ */}
      {/* WIZARD CONTAINER CARD                                         */}
      {/* ============================================================ */}
      <div
        style={{
          background: 'rgba(15, 23, 42, 0.75)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          borderRadius: '20px',
          padding: '36px 32px',
          backdropFilter: 'blur(20px)',
          minHeight: '440px',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
        }}
      >
        <AnimatePresence mode="wait" custom={direction}>
          <motion.div
            key={step}
            custom={direction}
            variants={wizardSlideVariants}
            initial="enter"
            animate="center"
            exit="exit"
            style={{ width: '100%', flex: 1 }}
          >
            {/* STEP 1: COUNTRY SELECTION */}
            {step === 1 && (
          <div>
            <div style={{ marginBottom: '24px' }}>
              <span style={{ fontSize: '0.8rem', color: '#94A3B8', fontWeight: 600 }}>STEP 1 OF 6</span>
              <h2 style={{ fontSize: '1.45rem', fontWeight: 800, color: '#FFFFFF', margin: '4px 0 8px 0' }}>
                Where are you looking for work?
              </h2>
              <p style={{ fontSize: '0.9rem', color: '#94A3B8', margin: 0 }}>
                Your estimate uses a model trained specifically for this market. Currencies and models
                remain strictly isolated.
              </p>
            </div>

            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
                gap: '20px',
                marginTop: '16px',
              }}
            >
              {/* USA Card */}
              <div
                onClick={() => {
                  setMarket('USA');
                }}
                style={{
                  background: isUSA
                    ? 'linear-gradient(145deg, rgba(56, 189, 248, 0.16) 0%, rgba(15, 23, 42, 0.9) 100%)'
                    : 'rgba(21, 23, 31, 0.6)',
                  border: isUSA ? '2px solid #38BDF8' : '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '16px',
                  padding: '28px',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  boxShadow: isUSA ? '0 8px 24px rgba(56, 189, 248, 0.25)' : 'none',
                }}
              >
                <div style={{ fontSize: '2.5rem', marginBottom: '12px' }}>🇺🇸</div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#FFFFFF', marginBottom: '6px' }}>
                  United States
                </h3>
                <p style={{ fontSize: '0.85rem', color: '#94A3B8', lineHeight: 1.5, margin: '0 0 16px 0' }}>
                  Model trained on 34,036 US technology job postings. Outputs predictions in USD ($ / year).
                </p>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.78rem', color: '#38BDF8', fontWeight: 600 }}>
                  <CheckCircle2 size={15} />
                  <span>XGBoost Architecture · 123 Features</span>
                </div>
              </div>

              {/* India Card */}
              <div
                onClick={() => {
                  setMarket('India');
                }}
                style={{
                  background: isIndia
                    ? 'linear-gradient(145deg, rgba(249, 115, 22, 0.16) 0%, rgba(15, 23, 42, 0.9) 100%)'
                    : 'rgba(21, 23, 31, 0.6)',
                  border: isIndia ? '2px solid #F97316' : '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '16px',
                  padding: '28px',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  boxShadow: isIndia ? '0 8px 24px rgba(249, 115, 22, 0.25)' : 'none',
                }}
              >
                <div style={{ fontSize: '2.5rem', marginBottom: '12px' }}>🇮🇳</div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#FFFFFF', marginBottom: '6px' }}>
                  India
                </h3>
                <p style={{ fontSize: '0.85rem', color: '#94A3B8', lineHeight: 1.5, margin: '0 0 16px 0' }}>
                  Model trained on 5,859 Indian technology job postings. Outputs predictions in INR (₹ LPA).
                </p>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.78rem', color: '#F97316', fontWeight: 600 }}>
                  <CheckCircle2 size={15} />
                  <span>HistGradientBoosting · 290 Features</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* STEP 2: ROLE SELECTION */}
        {step === 2 && (
          <div>
            <div style={{ marginBottom: '20px' }}>
              <span style={{ fontSize: '0.8rem', color: '#94A3B8', fontWeight: 600 }}>STEP 2 OF 6</span>
              <h2 style={{ fontSize: '1.45rem', fontWeight: 800, color: '#FFFFFF', margin: '4px 0 8px 0' }}>
                What kind of role are you targeting?
              </h2>
              <p style={{ fontSize: '0.9rem', color: '#94A3B8', margin: 0 }}>
                Select the role category that most closely matches your target position.
              </p>
            </div>

            {/* Search Input */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                background: 'rgba(255, 255, 255, 0.04)',
                border: '1px solid rgba(255, 255, 255, 0.12)',
                borderRadius: '10px',
                padding: '10px 14px',
                marginBottom: '16px',
              }}
            >
              <Search size={16} style={{ color: '#94A3B8', marginRight: '10px' }} />
              <input
                type="text"
                placeholder="Search roles (e.g. Software Engineer, Machine Learning, Data Analyst)..."
                value={roleSearch}
                onChange={(e) => setRoleSearch(e.target.value)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  outline: 'none',
                  color: '#FFFFFF',
                  fontSize: '0.9rem',
                  width: '100%',
                }}
              />
            </div>

            {/* Selectable Roles Grid */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
                gap: '10px',
                maxHeight: '280px',
                overflowY: 'auto',
                padding: '4px',
              }}
            >
              {options?.roles
                ?.filter((r) => r.toLowerCase().includes(roleSearch.toLowerCase()))
                .map((r) => {
                  const isSelected = isUSA ? usaRole === r : indiaRole === r;
                  const activeColor = isUSA ? '#38BDF8' : '#F97316';

                  return (
                    <button
                      key={r}
                      type="button"
                      onClick={() => (isUSA ? setUsaRole(r) : setIndiaRole(r))}
                      style={{
                        padding: '14px 16px',
                        borderRadius: '12px',
                        border: isSelected ? `2px solid ${activeColor}` : '1px solid rgba(255, 255, 255, 0.08)',
                        background: isSelected ? `${activeColor}20` : 'rgba(255, 255, 255, 0.03)',
                        color: isSelected ? '#FFFFFF' : '#CBD5E1',
                        cursor: 'pointer',
                        textAlign: 'left',
                        fontWeight: isSelected ? 700 : 500,
                        fontSize: '0.9rem',
                        transition: 'all 0.15s ease',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                      }}
                    >
                      <span>{r}</span>
                      {isSelected && <Check size={16} style={{ color: activeColor }} />}
                    </button>
                  );
                })}
            </div>
          </div>
        )}

        {/* STEP 3: EXPERIENCE LEVEL */}
        {step === 3 && (
          <div>
            <div style={{ marginBottom: '24px' }}>
              <span style={{ fontSize: '0.8rem', color: '#94A3B8', fontWeight: 600 }}>STEP 3 OF 6</span>
              <h2 style={{ fontSize: '1.45rem', fontWeight: 800, color: '#FFFFFF', margin: '4px 0 8px 0' }}>
                How much experience do you have?
              </h2>
              <p style={{ fontSize: '0.9rem', color: '#94A3B8', margin: 0 }}>
                Years of relevant professional experience.
              </p>
            </div>

            {/* Large Experience Indicator */}
            <div
              style={{
                textAlign: 'center',
                padding: '24px 0',
                background: 'rgba(255, 255, 255, 0.02)',
                borderRadius: '16px',
                border: '1px solid rgba(255, 255, 255, 0.06)',
                marginBottom: '28px',
              }}
            >
              <div
                style={{
                  fontSize: '3rem',
                  fontWeight: 900,
                  color: isUSA ? '#38BDF8' : '#F97316',
                  fontFamily: 'var(--font-mono)',
                  marginBottom: '4px',
                }}
              >
                {isUSA ? `${usaExpYears} years` : `${indiaExpYears} years`}
              </div>
              <div style={{ fontSize: '0.88rem', color: '#94A3B8' }}>
                {isUSA ? `Mapped Seniority Tier: ${usaSeniority}` : 'Continuous Midpoint Experience'}
              </div>
            </div>

            {/* Slider */}
            <div style={{ padding: '0 12px', marginBottom: '28px' }}>
              <input
                type="range"
                min="0"
                max="20"
                step="1"
                value={isUSA ? usaExpYears : indiaExpYears}
                onChange={(e) => {
                  const val = parseInt(e.target.value, 10);
                  if (isUSA) setUsaExpYears(val);
                  else setIndiaExpYears(val);
                }}
                style={{
                  width: '100%',
                  height: '8px',
                  borderRadius: '4px',
                  accentColor: isUSA ? '#38BDF8' : '#F97316',
                  cursor: 'pointer',
                }}
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', color: '#64748B', fontSize: '0.78rem', marginTop: '6px' }}>
                <span>0 years</span>
                <span>5 years</span>
                <span>10 years</span>
                <span>15 years</span>
                <span>20+ years</span>
              </div>
            </div>

            {/* Quick Experience Preset Chips */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', justifyContent: 'center' }}>
              {[
                { label: '0–2 years (Entry)', val: 1 },
                { label: '3–5 years (Mid)', val: 4 },
                { label: '6–10 years (Senior)', val: 8 },
                { label: '11–15 years (Lead)', val: 12 },
                { label: '16+ years (Principal)', val: 18 },
              ].map((b) => {
                const currentVal = isUSA ? usaExpYears : indiaExpYears;
                const isSelected =
                  (b.val === 1 && currentVal <= 2) ||
                  (b.val === 4 && currentVal >= 3 && currentVal <= 5) ||
                  (b.val === 8 && currentVal >= 6 && currentVal <= 10) ||
                  (b.val === 12 && currentVal >= 11 && currentVal <= 15) ||
                  (b.val === 18 && currentVal >= 16);

                return (
                  <button
                    key={b.label}
                    type="button"
                    onClick={() => {
                      if (isUSA) setUsaExpYears(b.val);
                      else setIndiaExpYears(b.val);
                    }}
                    style={{
                      padding: '8px 16px',
                      borderRadius: '20px',
                      border: isSelected ? (isUSA ? '1px solid #38BDF8' : '1px solid #F97316') : '1px solid rgba(255, 255, 255, 0.1)',
                      background: isSelected ? (isUSA ? 'rgba(56, 189, 248, 0.18)' : 'rgba(249, 115, 22, 0.18)') : 'rgba(255, 255, 255, 0.03)',
                      color: isSelected ? '#FFFFFF' : '#94A3B8',
                      fontSize: '0.85rem',
                      fontWeight: isSelected ? 700 : 500,
                      cursor: 'pointer',
                    }}
                  >
                    {b.label}
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* STEP 4: LOCATION */}
        {step === 4 && (
          <div>
            <div style={{ marginBottom: '20px' }}>
              <span style={{ fontSize: '0.8rem', color: '#94A3B8', fontWeight: 600 }}>STEP 4 OF 6</span>
              <h2 style={{ fontSize: '1.45rem', fontWeight: 800, color: '#FFFFFF', margin: '4px 0 8px 0' }}>
                Where would you work?
              </h2>
              <p style={{ fontSize: '0.9rem', color: '#94A3B8', margin: 0 }}>
                Select your primary metro area or metropolitan tech hub supported by the market model.
              </p>
            </div>

            {/* City Search */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                background: 'rgba(255, 255, 255, 0.04)',
                border: '1px solid rgba(255, 255, 255, 0.12)',
                borderRadius: '10px',
                padding: '10px 14px',
                marginBottom: '16px',
              }}
            >
              <Search size={16} style={{ color: '#94A3B8', marginRight: '10px' }} />
              <input
                type="text"
                placeholder={isUSA ? 'Search US tech hubs (e.g. San Francisco, New York, Austin)...' : 'Search Indian tech hubs (e.g. Bengaluru, Hyderabad, Pune)...'}
                value={citySearch}
                onChange={(e) => setCitySearch(e.target.value)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  outline: 'none',
                  color: '#FFFFFF',
                  fontSize: '0.9rem',
                  width: '100%',
                }}
              />
            </div>

            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
                gap: '10px',
                maxHeight: '280px',
                overflowY: 'auto',
                padding: '4px',
              }}
            >
              {(options?.cities || options?.locations || [])
                .filter((c: string) => c.toLowerCase().includes(citySearch.toLowerCase()))
                .map((c: string) => {
                  const isSelected = isUSA ? usaCity === c : indiaCity === c;
                  const activeColor = isUSA ? '#38BDF8' : '#F97316';

                  return (
                    <button
                      key={c}
                      type="button"
                      onClick={() => (isUSA ? setUsaCity(c) : setIndiaCity(c))}
                      style={{
                        padding: '12px 16px',
                        borderRadius: '10px',
                        border: isSelected ? `2px solid ${activeColor}` : '1px solid rgba(255, 255, 255, 0.08)',
                        background: isSelected ? `${activeColor}20` : 'rgba(255, 255, 255, 0.03)',
                        color: isSelected ? '#FFFFFF' : '#CBD5E1',
                        cursor: 'pointer',
                        textAlign: 'left',
                        fontWeight: isSelected ? 700 : 500,
                        fontSize: '0.88rem',
                        transition: 'all 0.15s ease',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                      }}
                    >
                      <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <MapPin size={14} style={{ color: isSelected ? activeColor : '#64748B' }} />
                        <span>{c}</span>
                      </span>
                      {isSelected && <Check size={15} style={{ color: activeColor }} />}
                    </button>
                  );
                })}
            </div>
          </div>
        )}

        {/* STEP 5: SKILLS */}
        {step === 5 && (
          <div>
            <div style={{ marginBottom: '18px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <span style={{ fontSize: '0.8rem', color: '#94A3B8', fontWeight: 600 }}>STEP 5 OF 6</span>
                  <h2 style={{ fontSize: '1.45rem', fontWeight: 800, color: '#FFFFFF', margin: '4px 0 6px 0' }}>
                    Which skills do you have?
                  </h2>
                  <p style={{ fontSize: '0.9rem', color: '#94A3B8', margin: 0 }}>
                    Select your core tools and competencies. Selected: <strong>{activeSkills.length}</strong>
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => (isUSA ? setUsaSkills([]) : setIndiaSkills([]))}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: '#94A3B8',
                    fontSize: '0.8rem',
                    cursor: 'pointer',
                    textDecoration: 'underline',
                  }}
                >
                  Clear all
                </button>
              </div>
            </div>

            {/* Currently Selected Chips */}
            {activeSkills.length > 0 && (
              <div
                style={{
                  display: 'flex',
                  flexWrap: 'wrap',
                  gap: '6px',
                  marginBottom: '16px',
                  padding: '12px',
                  background: 'rgba(255, 255, 255, 0.02)',
                  borderRadius: '12px',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                }}
              >
                {activeSkills.map((k) => (
                  <span
                    key={k}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '6px',
                      padding: '4px 10px',
                      borderRadius: '16px',
                      background: isUSA ? 'rgba(56, 189, 248, 0.2)' : 'rgba(249, 115, 22, 0.2)',
                      border: isUSA ? '1px solid #38BDF8' : '1px solid #F97316',
                      color: '#FFFFFF',
                      fontSize: '0.8rem',
                      fontWeight: 600,
                    }}
                  >
                    <span>{formatSkillLabel(k)}</span>
                    <button
                      type="button"
                      onClick={() => toggleSkill(k)}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: '#FFFFFF',
                        cursor: 'pointer',
                        padding: 0,
                        display: 'flex',
                      }}
                    >
                      <X size={13} />
                    </button>
                  </span>
                ))}
              </div>
            )}

            {/* Search & Category Filter */}
            <div style={{ display: 'flex', gap: '10px', marginBottom: '14px', flexWrap: 'wrap' }}>
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  background: 'rgba(255, 255, 255, 0.04)',
                  border: '1px solid rgba(255, 255, 255, 0.12)',
                  borderRadius: '10px',
                  padding: '8px 12px',
                  flex: 1,
                  minWidth: '220px',
                }}
              >
                <Search size={15} style={{ color: '#94A3B8', marginRight: '8px' }} />
                <input
                  type="text"
                  placeholder="Search skills (e.g. Python, SQL, AWS, React, Docker)..."
                  value={skillSearch}
                  onChange={(e) => setSkillSearch(e.target.value)}
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

              {availableCategories.length > 2 && (
                <div style={{ display: 'flex', gap: '6px', overflowX: 'auto', paddingBottom: '4px' }}>
                  {availableCategories.map((cat) => (
                    <button
                      key={cat}
                      type="button"
                      onClick={() => setSkillCategory(cat)}
                      style={{
                        padding: '6px 12px',
                        borderRadius: '8px',
                        border:
                          skillCategory === cat
                            ? isUSA
                              ? '1px solid #38BDF8'
                              : '1px solid #F97316'
                            : '1px solid rgba(255, 255, 255, 0.08)',
                        background:
                          skillCategory === cat
                            ? isUSA
                              ? 'rgba(56, 189, 248, 0.2)'
                              : 'rgba(249, 115, 22, 0.2)'
                            : 'rgba(255, 255, 255, 0.02)',
                        color: skillCategory === cat ? '#FFFFFF' : '#94A3B8',
                        fontSize: '0.78rem',
                        cursor: 'pointer',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {cat}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Selectable Skill Chips */}
            <div
              style={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: '8px',
                maxHeight: '240px',
                overflowY: 'auto',
                padding: '4px',
              }}
            >
              {filteredSkills.map((s) => {
                const rawKey = s.raw_key || s.id || `skill_${s.name.toLowerCase()}`;
                const isSelected = activeSkills.includes(rawKey) || activeSkills.includes(s.name.toLowerCase());
                const activeColor = isUSA ? '#38BDF8' : '#F97316';

                return (
                  <button
                    key={rawKey}
                    type="button"
                    onClick={() => toggleSkill(rawKey)}
                    style={{
                      padding: '7px 14px',
                      borderRadius: '20px',
                      border: isSelected ? `1px solid ${activeColor}` : '1px solid rgba(255, 255, 255, 0.1)',
                      background: isSelected ? `${activeColor}25` : 'rgba(255, 255, 255, 0.03)',
                      color: isSelected ? '#FFFFFF' : '#CBD5E1',
                      fontSize: '0.82rem',
                      fontWeight: isSelected ? 700 : 500,
                      cursor: 'pointer',
                      transition: 'all 0.12s ease',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '6px',
                    }}
                  >
                    <span>{formatSkillLabel(s.name)}</span>
                    {isSelected && <Check size={14} style={{ color: activeColor }} />}
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* STEP 6: WORK MODE */}
        {step === 6 && (
          <div>
            <div style={{ marginBottom: '24px' }}>
              <span style={{ fontSize: '0.8rem', color: '#94A3B8', fontWeight: 600 }}>STEP 6 OF 6</span>
              <h2 style={{ fontSize: '1.45rem', fontWeight: 800, color: '#FFFFFF', margin: '4px 0 8px 0' }}>
                What is your preferred work mode?
              </h2>
              <p style={{ fontSize: '0.9rem', color: '#94A3B8', margin: 0 }}>
                This helps us understand how your profile compares with similar job postings in the
                selected market.
              </p>
            </div>

            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
                gap: '16px',
                marginTop: '16px',
              }}
            >
              {['Remote', 'Hybrid', 'On-site'].map((mode) => {
                const currentMode = isUSA ? usaWorkMode : indiaWorkMode;
                const isSelected = currentMode === mode || (mode === 'On-site' && currentMode === 'Onsite');
                const activeColor = isUSA ? '#38BDF8' : '#F97316';

                return (
                  <div
                    key={mode}
                    onClick={() => {
                      if (isUSA) setUsaWorkMode(mode as any);
                      else setIndiaWorkMode(mode === 'On-site' ? 'Onsite' : mode);
                    }}
                    style={{
                      background: isSelected ? `${activeColor}18` : 'rgba(21, 23, 31, 0.6)',
                      border: isSelected ? `2px solid ${activeColor}` : '1px solid rgba(255, 255, 255, 0.1)',
                      borderRadius: '16px',
                      padding: '24px',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                    }}
                  >
                    <div style={{ fontSize: '1.8rem', marginBottom: '8px' }}>
                      {mode === 'Remote' ? '🏠' : mode === 'Hybrid' ? '🏢' : '📍'}
                    </div>
                    <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '6px' }}>
                      {mode}
                    </h3>
                    <p style={{ fontSize: '0.82rem', color: '#94A3B8', lineHeight: 1.5, margin: 0 }}>
                      {mode === 'Remote'
                        ? '100% remote work flexibility across any approved location.'
                        : mode === 'Hybrid'
                        ? 'Balanced blend of in-office collaboration and remote focus.'
                        : 'Dedicated presence at the regional company headquarters.'}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* STEP 7: RESULT SCREEN */}
        {step === 7 && (
          <div>
            {analyzing ? (
              <motion.div
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.2 }}
                style={{ textAlign: 'center', padding: '60px 20px', color: '#94A3B8' }}
              >
                <div className="ji-spinner" style={{ margin: '0 auto 16px' }} />
                <h3 style={{ color: '#FFFFFF', fontSize: '1.2rem', marginBottom: '6px' }}>
                  Analyzing your profile...
                </h3>
                <p style={{ fontSize: '0.88rem', margin: 0 }}>
                  Evaluating experience, location factors, and {activeSkills.length} selected skills against
                  the {market} model.
                </p>
              </motion.div>
            ) : predictionError ? (
              <div style={{ textAlign: 'center', padding: '48px 24px', background: 'rgba(239, 68, 68, 0.08)', borderRadius: '16px', border: '1px solid rgba(239, 68, 68, 0.3)' }}>
                <AlertTriangle size={36} style={{ color: '#EF4444', margin: '0 auto 12px auto' }} />
                <h3 style={{ color: '#FFFFFF', fontSize: '1.2rem', marginBottom: '6px' }}>Estimation Error</h3>
                <p style={{ color: '#94A3B8', fontSize: '0.88rem', maxWidth: '480px', margin: '0 auto 20px auto', lineHeight: 1.5 }}>
                  {predictionError}
                </p>
                <button
                  type="button"
                  onClick={runPrediction}
                  style={{
                    padding: '10px 20px',
                    borderRadius: '8px',
                    background: isUSA ? '#38BDF8' : '#F97316',
                    color: isUSA ? '#000000' : '#FFFFFF',
                    fontWeight: 700,
                    border: 'none',
                    cursor: 'pointer',
                  }}
                >
                  Retry Prediction
                </button>
              </div>
            ) : result ? (
              <motion.div
                variants={resultRevealVariants}
                initial="hidden"
                animate="visible"
                style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}
              >
                {/* 1. Main Headline & Big Number */}
                <div
                  style={{
                    background: 'linear-gradient(145deg, rgba(21, 23, 31, 0.95) 0%, rgba(15, 23, 42, 0.9) 100%)',
                    border: isUSA ? '2px solid rgba(56, 189, 248, 0.5)' : '2px solid rgba(249, 115, 22, 0.5)',
                    borderRadius: '20px',
                    padding: '36px',
                    textAlign: 'center',
                    boxShadow: isUSA ? '0 12px 36px rgba(56, 189, 248, 0.15)' : '0 12px 36px rgba(249, 115, 22, 0.15)',
                  }}
                >
                  <span
                    style={{
                      fontSize: '0.8rem',
                      fontWeight: 800,
                      letterSpacing: '0.1em',
                      color: isUSA ? '#38BDF8' : '#F97316',
                      textTransform: 'uppercase',
                    }}
                  >
                    ESTIMATED ANNUAL SALARY
                  </span>

                  <div
                    style={{
                      fontSize: 'clamp(2.8rem, 6vw, 4rem)',
                      fontWeight: 900,
                      color: '#FFFFFF',
                      letterSpacing: '-0.03em',
                      margin: '10px 0 6px 0',
                      fontFamily: 'var(--font-mono)',
                    }}
                  >
                    {result.predicted_salary_display}
                  </div>

                  {isIndia && result.predicted_salary_inr_display && (
                    <div style={{ fontSize: '1.1rem', color: '#CBD5E1', fontWeight: 600, marginBottom: '10px' }}>
                      ≈ {result.predicted_salary_inr_display} / annum
                    </div>
                  )}

                  <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', color: '#94A3B8' }}>
                    <Info size={15} style={{ color: isUSA ? '#38BDF8' : '#F97316' }} />
                    <span>Model estimate based on your profile inputs</span>
                  </div>
                </div>

                {/* 2. Result Interpretation */}
                <div
                  style={{
                    background: 'rgba(255, 255, 255, 0.03)',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    borderRadius: '14px',
                    padding: '18px 22px',
                  }}
                >
                  <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#FFFFFF', margin: '0 0 6px 0' }}>
                    How should I read this?
                  </h4>
                  <p style={{ fontSize: '0.88rem', color: '#94A3B8', lineHeight: 1.6, margin: 0 }}>
                    This is an estimate based on patterns learned from the job-market data used to train
                    JobIntel ({market} model). It is not a guaranteed offer or salary. Individual
                    compensation varies based on negotiation, company stage, equity, and performance.
                  </p>
                </div>

                {/* 3. Why This Estimate Panel */}
                <div
                  style={{
                    background: 'rgba(21, 23, 31, 0.7)',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    borderRadius: '16px',
                    padding: '24px',
                  }}
                >
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#FFFFFF', marginBottom: '16px' }}>
                    Why this estimate?
                  </h3>

                  <div
                    style={{
                      display: 'grid',
                      gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                      gap: '16px',
                    }}
                  >
                    <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '14px', borderRadius: '12px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
                      <div style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 700, textTransform: 'uppercase', marginBottom: '4px' }}>
                        Experience ({isUSA ? `${usaExpYears} yrs` : `${indiaExpYears} yrs`})
                      </div>
                      <div style={{ fontSize: '0.85rem', color: '#E2E8F0', lineHeight: 1.5 }}>
                        Experience level is one of the strongest predictive signals in the {market} model.
                      </div>
                    </div>

                    <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '14px', borderRadius: '12px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
                      <div style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 700, textTransform: 'uppercase', marginBottom: '4px' }}>
                        Role ({isUSA ? usaRole : indiaRole})
                      </div>
                      <div style={{ fontSize: '0.85rem', color: '#E2E8F0', lineHeight: 1.5 }}>
                        Baseline compensation distribution for this specialization in the analyzed data.
                      </div>
                    </div>

                    <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '14px', borderRadius: '12px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
                      <div style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 700, textTransform: 'uppercase', marginBottom: '4px' }}>
                        Location ({isUSA ? usaCity : indiaCity})
                      </div>
                      <div style={{ fontSize: '0.85rem', color: '#E2E8F0', lineHeight: 1.5 }}>
                        Adjusted for metropolitan market demand and hiring density.
                      </div>
                    </div>

                    <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '14px', borderRadius: '12px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
                      <div style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 700, textTransform: 'uppercase', marginBottom: '4px' }}>
                        Skills ({activeSkills.length} selected)
                      </div>
                      <div style={{ fontSize: '0.85rem', color: '#E2E8F0', lineHeight: 1.5 }}>
                        Profiles containing your selected competencies tend to appear at higher observed
                        salary levels in this dataset.
                      </div>
                    </div>
                  </div>
                </div>

                {/* 4. Closest Skill Pattern / Archetype Match */}
                {result.archetype && (
                  <div
                    style={{
                      background: result.archetype.archetype_available
                        ? 'linear-gradient(145deg, rgba(236, 72, 153, 0.1) 0%, rgba(15, 23, 42, 0.8) 100%)'
                        : 'rgba(255, 255, 255, 0.03)',
                      border: result.archetype.archetype_available
                        ? '1px solid rgba(236, 72, 153, 0.35)'
                        : '1px solid rgba(255, 255, 255, 0.08)',
                      borderRadius: '16px',
                      padding: '24px',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px' }}>
                      <div>
                        <span style={{ fontSize: '0.74rem', fontWeight: 800, color: result.archetype.archetype_available ? '#F472B6' : '#94A3B8', textTransform: 'uppercase' }}>
                          {result.archetype.archetype_available ? 'YOUR CLOSEST SKILL PATTERN' : 'SKILL PATTERN / ARCHETYPE'}
                        </span>
                        <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#FFFFFF', margin: '4px 0 6px 0' }}>
                          {result.archetype.name}
                        </h3>
                        <p style={{ fontSize: '0.88rem', color: '#CBD5E1', margin: '0 0 12px 0', maxWidth: '640px' }}>
                          {result.archetype.archetype_available
                            ? 'Your selected skills resemble this recurring skill pattern found in the analyzed job postings.'
                            : result.archetype.definition || 'The learned archetype taxonomy is defined for skill-bearing job postings. Add at least one technical skill to receive an archetype classification.'}
                        </p>
                      </div>

                      {result.archetype.archetype_available && onNavigate && (
                        <button
                          type="button"
                          onClick={() => onNavigate('archetypes')}
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '6px',
                            padding: '8px 16px',
                            borderRadius: '8px',
                            background: 'rgba(236, 72, 153, 0.18)',
                            border: '1px solid rgba(236, 72, 153, 0.4)',
                            color: '#FBCFE8',
                            fontSize: '0.82rem',
                            fontWeight: 700,
                            cursor: 'pointer',
                          }}
                        >
                          <span>Explore this archetype</span>
                          <ArrowRight size={14} />
                        </button>
                      )}
                    </div>
                  </div>
                )}

                {/* 5. Uncertainty & Holdout Error Margin */}
                <div
                  style={{
                    background: 'rgba(21, 23, 31, 0.7)',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    borderRadius: '16px',
                    padding: '24px',
                  }}
                >
                  <h4 style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF', margin: '0 0 10px 0' }}>
                    How confident should I be?
                  </h4>
                  <div style={{ fontSize: '0.88rem', color: '#94A3B8', lineHeight: 1.6, marginBottom: '14px' }}>
                    Historical model performance:
                    <strong style={{ color: '#FFFFFF' }}>
                      {isUSA ? ' Holdout MAE: $36,381' : ' Holdout MAE: ₹3.71 LPA'}
                    </strong>
                    . This means predictions in the authoritative holdout evaluation were typically off by
                    roughly this amount on average.
                  </div>

                  {/* India High-Salary Warning Notice */}
                  {isIndia &&
                    (result.predicted_salary_lpa || result.predicted_salary || 0) >= 20.0 && (
                      <div
                        style={{
                          background: 'rgba(234, 179, 8, 0.12)',
                          border: '1px solid rgba(234, 179, 8, 0.35)',
                          borderRadius: '10px',
                          padding: '14px 16px',
                          display: 'flex',
                          gap: '12px',
                          alignItems: 'flex-start',
                        }}
                      >
                        <AlertTriangle size={20} style={{ color: '#EAB308', flexShrink: 0, marginTop: '2px' }} />
                        <div style={{ fontSize: '0.82rem', color: '#FEF08A', lineHeight: 1.5 }}>
                          {(result.predicted_salary_lpa || result.predicted_salary || 0) >= 40.0 ? (
                            <>
                              <strong>High uncertainty notice: </strong>
                              For the ≥₹40 LPA subgroup, historical holdout MAE was about ₹31.12 LPA.
                              Treat this estimate as directional rather than precise due to thin upper-tail
                              sample density.
                            </>
                          ) : (
                            <>
                              <strong>Important notice: </strong>
                              Predictions become less reliable at higher salary levels. For postings at or
                              above ₹20 LPA, historical holdout MAE was about ₹8.06 LPA.
                            </>
                          )}
                        </div>
                      </div>
                    )}
                </div>

                {/* 6. Technical Evaluator Accordion */}
                <div
                  style={{
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    borderRadius: '12px',
                    background: 'rgba(15, 23, 42, 0.5)',
                    overflow: 'hidden',
                  }}
                >
                  <button
                    type="button"
                    onClick={() => setShowEvaluatorDetails((prev) => !prev)}
                    style={{
                      width: '100%',
                      padding: '14px 20px',
                      background: 'none',
                      border: 'none',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      color: '#CBD5E1',
                      fontSize: '0.85rem',
                      fontWeight: 600,
                      cursor: 'pointer',
                    }}
                  >
                    <span>Technical Evaluator Mode (Model details & metrics)</span>
                    {showEvaluatorDetails ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                  </button>

                  {showEvaluatorDetails && (
                    <div
                      style={{
                        padding: '16px 20px',
                        borderTop: '1px solid rgba(255, 255, 255, 0.08)',
                        background: 'rgba(0, 0, 0, 0.2)',
                        fontSize: '0.8rem',
                        color: '#94A3B8',
                        lineHeight: 1.6,
                      }}
                    >
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '12px' }}>
                        <div>
                          <span style={{ color: '#64748B' }}>Architecture: </span>
                          <strong style={{ color: '#FFFFFF' }}>
                            {isUSA ? 'XGBoost Regressor (123 features)' : 'HistGradientBoosting (290 features)'}
                          </strong>
                        </div>
                        <div>
                          <span style={{ color: '#64748B' }}>Cohort Size: </span>
                          <strong style={{ color: '#FFFFFF' }}>
                            {isUSA ? '34,036 rows' : '5,859 rows'}
                          </strong>
                        </div>
                        <div>
                          <span style={{ color: '#64748B' }}>Holdout R²: </span>
                          <strong style={{ color: '#FFFFFF' }}>{isUSA ? '0.4233' : '0.5798'}</strong>
                        </div>
                        <div>
                          <span style={{ color: '#64748B' }}>Median Absolute Error: </span>
                          <strong style={{ color: '#FFFFFF' }}>
                            {isUSA ? '$26,384.22' : '₹2.08 LPA'}
                          </strong>
                        </div>
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#64748B' }}>
                        Certified SSOT Artifact Hashes: Verified in ModelRegistry singleton. No model
                        retraining occurred during user inference.
                      </div>
                    </div>
                  )}
                </div>

                {/* 7. Result Action Buttons */}
                <div
                  style={{
                    display: 'flex',
                    flexWrap: 'wrap',
                    gap: '12px',
                    justifyContent: 'center',
                    paddingTop: '12px',
                  }}
                >
                  {onNavigate && (
                    <>
                      <button
                        type="button"
                        onClick={() => onNavigate('explore')}
                        style={{
                          padding: '12px 20px',
                          borderRadius: '10px',
                          background: 'rgba(255, 255, 255, 0.05)',
                          border: '1px solid rgba(255, 255, 255, 0.12)',
                          color: '#FFFFFF',
                          fontSize: '0.88rem',
                          fontWeight: 600,
                          cursor: 'pointer',
                        }}
                      >
                        Explore Similar Profiles
                      </button>

                      <button
                        type="button"
                        onClick={() => onNavigate('skills')}
                        style={{
                          padding: '12px 20px',
                          borderRadius: '10px',
                          background: 'rgba(255, 255, 255, 0.05)',
                          border: '1px solid rgba(255, 255, 255, 0.12)',
                          color: '#FFFFFF',
                          fontSize: '0.88rem',
                          fontWeight: 600,
                          cursor: 'pointer',
                        }}
                      >
                        See Skills
                      </button>

                      <button
                        type="button"
                        onClick={() => onNavigate('comparison')}
                        style={{
                          padding: '12px 20px',
                          borderRadius: '10px',
                          background: 'rgba(255, 255, 255, 0.05)',
                          border: '1px solid rgba(255, 255, 255, 0.12)',
                          color: '#FFFFFF',
                          fontSize: '0.88rem',
                          fontWeight: 600,
                          cursor: 'pointer',
                        }}
                      >
                        Compare USA & India
                      </button>
                    </>
                  )}

                  <button
                    type="button"
                    onClick={() => {
                      setDirection(-1);
                      setStep(1);
                      window.scrollTo({ top: 0, behavior: 'smooth' });
                    }}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '8px',
                      padding: '12px 22px',
                      borderRadius: '10px',
                      background: isUSA ? '#38BDF8' : '#F97316',
                      border: 'none',
                      color: '#000000',
                      fontSize: '0.88rem',
                      fontWeight: 700,
                      cursor: 'pointer',
                    }}
                  >
                    <RotateCcw size={15} />
                    <span>Start Again</span>
                  </button>
                </div>
              </motion.div>
            ) : null}
          </div>
        )}
          </motion.div>
        </AnimatePresence>

        {/* Wizard Navigation Footer for Steps 1 through 6 */}
        {step < 7 && (
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginTop: '32px',
              borderTop: '1px solid rgba(255, 255, 255, 0.08)',
              paddingTop: '20px',
            }}
          >
            <button
              type="button"
              disabled={step === 1}
              onClick={() => {
                setDirection(-1);
                setStep((prev) => Math.max(1, prev - 1));
              }}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 20px',
                borderRadius: '8px',
                background: 'rgba(255, 255, 255, 0.04)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                color: step === 1 ? '#475569' : '#CBD5E1',
                cursor: step === 1 ? 'not-allowed' : 'pointer',
                fontSize: '0.85rem',
                fontWeight: 600,
              }}
            >
              <ArrowLeft size={16} />
              <span>Back</span>
            </button>

            {step < 6 ? (
              <motion.button
                id="wizard-continue-btn"
                type="button"
                whileHover={{ scale: 1.015 }}
                whileTap={{ scale: 0.985 }}
                onClick={() => {
                  setDirection(1);
                  setStep((prev) => Math.min(6, prev + 1));
                }}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '10px 24px',
                  borderRadius: '8px',
                  background: isUSA ? '#38BDF8' : '#F97316',
                  border: 'none',
                  color: '#000000',
                  fontWeight: 700,
                  fontSize: '0.88rem',
                  cursor: 'pointer',
                }}
              >
                <span>Continue</span>
                <ArrowRight size={16} />
              </motion.button>
            ) : (
              <motion.button
                id="predict-submit-btn"
                type="button"
                whileHover={{ scale: 1.02, boxShadow: '0 12px 30px rgba(139, 92, 246, 0.6)' }}
                whileTap={{ scale: 0.98 }}
                onClick={() => {
                  setDirection(1);
                  runPrediction();
                }}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '12px 28px',
                  borderRadius: '10px',
                  background: 'linear-gradient(135deg, #8B5CF6 0%, #6366F1 100%)',
                  border: 'none',
                  color: '#FFFFFF',
                  fontWeight: 800,
                  fontSize: '0.95rem',
                  cursor: 'pointer',
                  boxShadow: '0 8px 24px rgba(139, 92, 246, 0.45)',
                }}
              >
                <Sparkles size={17} />
                <span>Calculate My Salary</span>
              </motion.button>
            )}
          </div>
        )}
      </div>

      <ScientificDisclaimer />
      <SourceFooter />
    </div>
  );
};
