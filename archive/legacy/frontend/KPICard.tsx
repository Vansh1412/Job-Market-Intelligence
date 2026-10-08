import React from 'react';

interface KPICardProps {
  label: string;
  value: string | number;
  sub?: string;
  delta?: string;
  deltaPositive?: boolean;
  accentColor?: string;
  accent?: string;
  icon?: React.ReactNode;
}

export const KPICard: React.FC<KPICardProps> = ({
  label,
  value,
  sub,
  delta,
  deltaPositive = true,
  accentColor,
  accent,
  icon,
}) => {
  const displayAccent = accent || accentColor || '#8B5CF6';

  return (
    <div
      className="ji-card"
      style={{
        padding: '20px 22px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Top Accent Light Bar */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '2px',
          background: `linear-gradient(90deg, ${displayAccent} 0%, transparent 80%)`,
        }}
      />

      <div>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '8px',
          }}
        >
          <span
            style={{
              fontSize: '0.72rem',
              fontWeight: 700,
              color: '#94A3B8',
              letterSpacing: '0.08em',
              textTransform: 'uppercase',
            }}
          >
            {label}
          </span>
          {icon && <span style={{ color: displayAccent }}>{icon}</span>}
        </div>

        <div
          className="font-mono-numbers"
          style={{
            fontSize: '2.1rem',
            fontWeight: 800,
            color: '#FFFFFF',
            letterSpacing: '-0.03em',
            lineHeight: 1.1,
            marginBottom: '8px',
          }}
        >
          {typeof value === 'number' ? value.toLocaleString() : value}
        </div>
      </div>

      <div>
        {delta && (
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              fontSize: '0.74rem',
              fontWeight: 700,
              padding: '2px 8px',
              borderRadius: '6px',
              background: deltaPositive ? 'rgba(16, 185, 129, 0.14)' : 'rgba(239, 68, 68, 0.14)',
              color: deltaPositive ? '#34D399' : '#F87171',
              border: `1px solid ${deltaPositive ? 'rgba(16, 185, 129, 0.28)' : 'rgba(239, 68, 68, 0.28)'}`,
              marginBottom: sub ? '6px' : 0,
            }}
          >
            <span>{deltaPositive ? '↑' : '↓'}</span>
            <span>{delta}</span>
          </div>
        )}

        {sub && (
          <div
            style={{
              fontSize: '0.76rem',
              color: '#64748B',
              lineHeight: 1.4,
            }}
          >
            {sub}
          </div>
        )}
      </div>
    </div>
  );
};
