import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Calculator,
  Compass,
  Layers,
  Dna,
  GitCompare,
  BookOpen,
  Home,
  Menu,
  X,
  Sparkles,
  ArrowRight,
} from 'lucide-react';
import { MarketSwitcher } from './MarketSwitcher';
import { useMarket } from '../context/MarketContext';

export type NavigationPage =
  | 'home'
  | 'calculator'
  | 'explore'
  | 'skills'
  | 'archetypes'
  | 'comparison'
  | 'howitworks';

interface AppHeaderProps {
  activePage: NavigationPage;
  onSelectPage: (page: NavigationPage) => void;
}

export const AppHeader: React.FC<AppHeaderProps> = ({ activePage, onSelectPage }) => {
  const { isUSA, isIndia } = useMarket();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const NAV_ITEMS: { id: NavigationPage; label: string; icon: React.ComponentType<{ size: number }> }[] = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'calculator', label: 'Salary Calculator', icon: Calculator },
    { id: 'explore', label: 'Explore Market', icon: Compass },
    { id: 'skills', label: 'Skills', icon: Layers },
    { id: 'archetypes', label: 'Archetypes', icon: Dna },
    { id: 'comparison', label: 'USA vs India', icon: GitCompare },
    { id: 'howitworks', label: 'How It Works', icon: BookOpen },
  ];

  const handleNavClick = (id: NavigationPage) => {
    onSelectPage(id);
    setMobileMenuOpen(false);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <>
      <header
        style={{
          height: '70px',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
          background: 'rgba(8, 9, 13, 0.94)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          position: 'sticky',
          top: 0,
          zIndex: 50,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 24px',
        }}
      >
        {/* Brand Logo & Name */}
        <div
          onClick={() => handleNavClick('home')}
          style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }}
        >
          <div
            style={{
              width: '36px',
              height: '36px',
              borderRadius: '10px',
              background: 'linear-gradient(135deg, #8B5CF6 0%, #6366F1 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 20px rgba(139, 92, 246, 0.45)',
            }}
          >
            <span style={{ color: '#FFFFFF', fontSize: '18px', fontWeight: 900 }}>◆</span>
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span
                style={{
                  fontSize: '1.15rem',
                  fontWeight: 900,
                  letterSpacing: '0.04em',
                  color: '#FFFFFF',
                  fontFamily: 'var(--font-sans)',
                }}
              >
                JOBINTEL
              </span>
            </div>
            <div
              style={{
                fontSize: '0.68rem',
                color: '#94A3B8',
                fontWeight: 500,
                letterSpacing: '0.04em',
              }}
            >
              Understand your worth
            </div>
          </div>
        </div>

        {/* Desktop Top Navigation Links */}
        <nav
          className="desktop-nav"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
          }}
        >
          {NAV_ITEMS.map((item) => {
            const isActive = activePage === item.id;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => handleNavClick(item.id)}
                style={{
                  position: 'relative',
                  background: 'transparent',
                  border: 'none',
                  borderRadius: '8px',
                  padding: '7px 12px',
                  color: isActive ? '#FFFFFF' : '#94A3B8',
                  fontSize: '0.82rem',
                  fontWeight: isActive ? 700 : 500,
                  cursor: 'pointer',
                  transition: 'color 0.15s ease',
                  whiteSpace: 'nowrap',
                }}
                onMouseEnter={(e) => {
                  if (!isActive) e.currentTarget.style.color = '#FFFFFF';
                }}
                onMouseLeave={(e) => {
                  if (!isActive) e.currentTarget.style.color = '#94A3B8';
                }}
              >
                {isActive && (
                  <motion.div
                    layoutId="active-nav-pill"
                    style={{
                      position: 'absolute',
                      inset: 0,
                      background: 'rgba(255, 255, 255, 0.08)',
                      border: '1px solid rgba(255, 255, 255, 0.14)',
                      borderRadius: '8px',
                      zIndex: 0,
                    }}
                    transition={{ type: 'spring', stiffness: 500, damping: 38 }}
                  />
                )}
                <span style={{ position: 'relative', zIndex: 1 }}>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Right Action Cluster: Market Switcher + Primary CTA */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          {/* Market Switcher */}
          <MarketSwitcher />

          {/* Primary CTA: "Estimate My Salary" */}
          <button
            type="button"
            className="desktop-header-cta"
            onClick={() => handleNavClick('calculator')}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              padding: '9px 18px',
              borderRadius: '9px',
              background: 'linear-gradient(135deg, #8B5CF6 0%, #6366F1 100%)',
              color: '#FFFFFF',
              fontSize: '0.85rem',
              fontWeight: 700,
              border: 'none',
              cursor: 'pointer',
              boxShadow: '0 4px 16px rgba(139, 92, 246, 0.35)',
              transition: 'all 0.2s ease',
              whiteSpace: 'nowrap',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-1px)';
              e.currentTarget.style.boxShadow = '0 6px 20px rgba(139, 92, 246, 0.5)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 4px 16px rgba(139, 92, 246, 0.35)';
            }}
          >
            <Calculator size={15} />
            <span>Estimate My Salary</span>
          </button>

          {/* Mobile Hamburger Toggle Button */}
          <button
            type="button"
            className="mobile-hamburger"
            onClick={() => setMobileMenuOpen((prev) => !prev)}
            style={{
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '8px',
              padding: '8px',
              color: '#CBD5E1',
              cursor: 'pointer',
              display: 'none', // Controlled by CSS media query
            }}
          >
            {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </header>

      {/* Mobile Drawer / Dropdown Menu */}
      {mobileMenuOpen && (
        <div
          style={{
            position: 'fixed',
            top: '70px',
            left: 0,
            right: 0,
            background: 'rgba(10, 11, 15, 0.98)',
            borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
            zIndex: 49,
            padding: '20px 24px 28px 24px',
            display: 'flex',
            flexDirection: 'column',
            gap: '12px',
            backdropFilter: 'blur(20px)',
          }}
        >
          {NAV_ITEMS.map((item) => {
            const IconComponent = item.icon;
            const isActive = activePage === item.id;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => handleNavClick(item.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '12px 16px',
                  borderRadius: '10px',
                  background: isActive ? 'rgba(139, 92, 246, 0.18)' : 'rgba(255, 255, 255, 0.03)',
                  border: isActive ? '1px solid #8B5CF6' : '1px solid rgba(255, 255, 255, 0.06)',
                  color: isActive ? '#FFFFFF' : '#CBD5E1',
                  fontSize: '0.95rem',
                  fontWeight: isActive ? 700 : 500,
                  cursor: 'pointer',
                  textAlign: 'left',
                }}
              >
                <IconComponent size={18} />
                <span>{item.label}</span>
              </button>
            );
          })}

          <div style={{ marginTop: '8px', paddingTop: '12px', borderTop: '1px solid rgba(255, 255, 255, 0.08)' }}>
            <button
              type="button"
              onClick={() => handleNavClick('calculator')}
              style={{
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                padding: '14px',
                borderRadius: '10px',
                background: 'linear-gradient(135deg, #8B5CF6 0%, #6366F1 100%)',
                color: '#FFFFFF',
                fontSize: '1rem',
                fontWeight: 700,
                border: 'none',
                cursor: 'pointer',
              }}
            >
              <Calculator size={18} />
              <span>Estimate My Salary</span>
            </button>
          </div>
        </div>
      )}
    </>
  );
};
