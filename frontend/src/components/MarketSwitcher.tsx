import React from 'react';
import { useMarket } from '../context/MarketContext';

export const MarketSwitcher: React.FC<{ compact?: boolean }> = ({ compact = false }) => {
  const { market, setMarket } = useMarket();

  return (
    <div
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        background: 'rgba(15, 23, 42, 0.75)',
        border: '1px solid rgba(255, 255, 255, 0.12)',
        borderRadius: '12px',
        padding: '3px',
        backdropFilter: 'blur(12px)',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.25)',
      }}
    >
      {/* USA Button */}
      <button
        type="button"
        onClick={() => setMarket('USA')}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: compact ? '5px 12px' : '6px 16px',
          borderRadius: '9px',
          border: market === 'USA' ? '1px solid rgba(59, 130, 246, 0.5)' : '1px solid transparent',
          background:
            market === 'USA'
              ? 'linear-gradient(135deg, rgba(37, 99, 235, 0.28) 0%, rgba(59, 130, 246, 0.18) 100%)'
              : 'transparent',
          color: market === 'USA' ? '#FFFFFF' : '#94A3B8',
          fontWeight: market === 'USA' ? 700 : 500,
          fontSize: compact ? '0.78rem' : '0.84rem',
          cursor: 'pointer',
          transition: 'all 0.2s ease',
          boxShadow: market === 'USA' ? '0 0 15px rgba(59, 130, 246, 0.3)' : 'none',
        }}
      >
        <span style={{ fontSize: '1.05rem', lineHeight: 1 }}>🇺🇸</span>
        <span style={{ letterSpacing: '0.02em' }}>USA</span>
        {!compact && (
          <span
            className="market-currency-badge"
            style={{
              fontSize: '0.7rem',
              color: market === 'USA' ? '#93C5FD' : '#64748B',
              fontWeight: 600,
              background: 'rgba(255, 255, 255, 0.06)',
              padding: '1px 6px',
              borderRadius: '6px',
            }}
          >
            $ USD
          </span>
        )}
      </button>

      {/* India Button */}
      <button
        type="button"
        onClick={() => setMarket('India')}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: compact ? '5px 12px' : '6px 16px',
          borderRadius: '9px',
          border: market === 'India' ? '1px solid rgba(249, 115, 22, 0.5)' : '1px solid transparent',
          background:
            market === 'India'
              ? 'linear-gradient(135deg, rgba(234, 88, 12, 0.28) 0%, rgba(249, 115, 22, 0.18) 100%)'
              : 'transparent',
          color: market === 'India' ? '#FFFFFF' : '#94A3B8',
          fontWeight: market === 'India' ? 700 : 500,
          fontSize: compact ? '0.78rem' : '0.84rem',
          cursor: 'pointer',
          transition: 'all 0.2s ease',
          boxShadow: market === 'India' ? '0 0 15px rgba(249, 115, 22, 0.3)' : 'none',
        }}
      >
        <span style={{ fontSize: '1.05rem', lineHeight: 1 }}>🇮🇳</span>
        <span style={{ letterSpacing: '0.02em' }}>India</span>
        {!compact && (
          <span
            className="market-currency-badge"
            style={{
              fontSize: '0.7rem',
              color: market === 'India' ? '#FDBA74' : '#64748B',
              fontWeight: 600,
              background: 'rgba(255, 255, 255, 0.06)',
              padding: '1px 6px',
              borderRadius: '6px',
            }}
          >
            ₹ LPA
          </span>
        )}
      </button>
    </div>
  );
};
