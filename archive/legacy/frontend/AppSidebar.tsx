import React from 'react';
import {
  LayoutDashboard,
  BookOpen,
  DollarSign,
  Layers,
  Dna,
  Target,
  BarChart3,
  ShieldAlert,
  GitCompare,
  Lock,
  Cpu,
} from 'lucide-react';
import { useMarket } from '../context/MarketContext';

export type PageId =
  | 'overview'
  | 'methodology'
  | 'crossmarket'
  | 'salary'
  | 'skills'
  | 'archetypes'
  | 'predictor'
  | 'models'
  | 'errors';

interface AppSidebarProps {
  activePage: PageId;
  onSelectPage: (id: PageId) => void;
}

export const AppSidebar: React.FC<AppSidebarProps> = ({ activePage, onSelectPage }) => {
  const { isUSA, isIndia, market } = useMarket();

  const NAV_SECTIONS = [
    {
      title: 'OVERVIEW',
      items: [
        { id: 'overview' as PageId, label: 'Executive Overview', icon: LayoutDashboard, accentColor: '#8B5CF6' },
        { id: 'crossmarket' as PageId, label: 'USA vs India', icon: GitCompare, badge: 'SYNTHESIS', accentColor: '#38BDF8' },
        { id: 'methodology' as PageId, label: 'Research Methodology', icon: BookOpen, accentColor: '#6366F1' },
      ],
    },
    {
      title: 'MARKET INTELLIGENCE',
      items: [
        {
          id: 'salary' as PageId,
          label: isUSA ? 'Salary Intelligence' : 'India Salary Market',
          icon: DollarSign,
          accentColor: '#06B6D4',
        },
        { id: 'skills' as PageId, label: 'Skill Intelligence', icon: Layers, accentColor: '#F59E0B' },
        {
          id: 'archetypes' as PageId,
          label: 'Archetype Explorer',
          icon: Dna,
          badge: isUSA ? 'k=7' : 'k=6',
          accentColor: '#EC4899',
        },
      ],
    },
    {
      title: 'MACHINE LEARNING',
      items: [
        { id: 'predictor' as PageId, label: 'Guided Calculator', icon: Target, badge: 'LIVE', accentColor: '#10B981' },
        { id: 'models' as PageId, label: 'Model Benchmarks', icon: BarChart3, accentColor: '#8B5CF6' },
        { id: 'errors' as PageId, label: 'Error Stratification (RQ3)', icon: ShieldAlert, accentColor: '#F97316' },
      ],
    },
  ];

  return (
    <aside
      style={{
        width: '260px',
        borderRight: '1px solid rgba(255, 255, 255, 0.08)',
        background: 'rgba(10, 11, 15, 0.88)',
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        height: 'calc(100vh - 68px)',
        position: 'sticky',
        top: '68px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        padding: '20px 14px 16px 14px',
        flexShrink: 0,
      }}
    >
      {/* Navigation Sections */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
        {NAV_SECTIONS.map((sec) => (
          <div key={sec.title}>
            <div
              style={{
                fontSize: '0.67rem',
                fontWeight: 700,
                color: '#64748B',
                letterSpacing: '0.08em',
                textTransform: 'uppercase',
                padding: '0 12px 8px 12px',
              }}
            >
              {sec.title}
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              {sec.items.map((item) => {
                const IconComponent = item.icon;
                const isActive = activePage === item.id;

                return (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => onSelectPage(item.id)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      width: '100%',
                      padding: '9px 12px',
                      borderRadius: '8px',
                      border: isActive
                        ? `1px solid ${item.accentColor}40`
                        : '1px solid transparent',
                      background: isActive
                        ? `linear-gradient(90deg, ${item.accentColor}18 0%, rgba(255, 255, 255, 0.02) 100%)`
                        : 'transparent',
                      color: isActive ? '#F8FAFC' : '#94A3B8',
                      cursor: 'pointer',
                      textAlign: 'left',
                      transition: 'all 0.15s ease',
                      outline: 'none',
                    }}
                    onMouseEnter={(e) => {
                      if (!isActive) {
                        e.currentTarget.style.background = 'rgba(255, 255, 255, 0.04)';
                        e.currentTarget.style.color = '#E2E8F0';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (!isActive) {
                        e.currentTarget.style.background = 'transparent';
                        e.currentTarget.style.color = '#94A3B8';
                      }
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <IconComponent
                        size={17}
                        style={{
                          color: isActive ? item.accentColor : '#64748B',
                          transition: 'color 0.15s ease',
                          flexShrink: 0,
                        }}
                      />
                      <span
                        style={{
                          fontSize: '0.84rem',
                          fontWeight: isActive ? 600 : 500,
                          letterSpacing: '-0.01em',
                        }}
                      >
                        {item.label}
                      </span>
                    </div>

                    {item.badge && (
                      <span
                        style={{
                          fontSize: '0.62rem',
                          fontWeight: 700,
                          padding: '1px 6px',
                          borderRadius: '10px',
                          background: isActive
                            ? `${item.accentColor}30`
                            : 'rgba(255, 255, 255, 0.06)',
                          color: isActive ? item.accentColor : '#94A3B8',
                          border: `1px solid ${isActive ? item.accentColor + '50' : 'rgba(255, 255, 255, 0.08)'}`,
                          letterSpacing: '0.04em',
                        }}
                      >
                        {item.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Footer Info Box */}
      <div
        style={{
          padding: '12px',
          borderRadius: '8px',
          background: 'rgba(255, 255, 255, 0.02)',
          border: '1px solid rgba(255, 255, 255, 0.06)',
          display: 'flex',
          flexDirection: 'column',
          gap: '8px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Lock size={13} style={{ color: '#10B981' }} />
          <span style={{ fontSize: '0.72rem', fontWeight: 600, color: '#E2E8F0' }}>
            Zero-Leakage Certified
          </span>
        </div>
        <div style={{ fontSize: '0.68rem', color: '#64748B', lineHeight: 1.4 }}>
          {isUSA
            ? 'USA XGBoost Model & 7-cluster PCA frozen.'
            : 'India HGB Model & 6-cluster PCA frozen.'}
        </div>
      </div>
    </aside>
  );
};
