import React from 'react';
import { ArrowRight } from 'lucide-react';
import { DataFlowItem } from '../types';

interface DataFlowVisualProps {
  items: DataFlowItem[];
}

export const DataFlowVisual: React.FC<DataFlowVisualProps> = ({ items }) => {
  return (
    <div
      className="ji-card-static"
      style={{
        padding: '24px 28px',
        marginBottom: '28px',
        background: 'rgba(16, 17, 22, 0.65)',
      }}
    >
      <div style={{ marginBottom: '16px' }}>
        <div
          style={{
            fontSize: '0.72rem',
            fontWeight: 700,
            color: '#8B5CF6',
            letterSpacing: '0.08em',
            textTransform: 'uppercase',
            marginBottom: '4px',
          }}
        >
          Research Data Flow & Population Selection
        </div>
        <div style={{ fontSize: '1rem', fontWeight: 700, color: '#FFFFFF' }}>
          Corpus Progression & Sample Attrition Funnel
        </div>
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: `repeat(${items.length}, 1fr)`,
          gap: '12px',
          alignItems: 'stretch',
        }}
      >
        {items.map((item, idx) => (
          <div
            key={item.stage}
            style={{
              display: 'flex',
              alignItems: 'center',
              position: 'relative',
            }}
          >
            <div
              style={{
                flex: 1,
                background: 'rgba(21, 23, 31, 0.7)',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                borderRadius: '10px',
                padding: '16px 14px',
                borderTop: `2px solid ${item.color}`,
                transition: 'transform 0.2s ease',
              }}
            >
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: '6px',
                }}
              >
                <span
                  style={{
                    fontSize: '0.68rem',
                    fontWeight: 700,
                    color: item.color,
                    letterSpacing: '0.04em',
                    textTransform: 'uppercase',
                  }}
                >
                  Step {idx + 1}
                </span>
                <span
                  style={{
                    fontSize: '0.68rem',
                    color: '#94A3B8',
                    fontFamily: 'var(--font-mono)',
                  }}
                >
                  {item.pct}
                </span>
              </div>

              <div
                className="font-mono-numbers"
                style={{
                  fontSize: '1.5rem',
                  fontWeight: 800,
                  color: '#FFFFFF',
                  letterSpacing: '-0.02em',
                  lineHeight: 1.1,
                  marginBottom: '4px',
                }}
              >
                {typeof item.count === 'number' ? item.count.toLocaleString() : item.count}
              </div>

              <div
                style={{
                  fontSize: '0.82rem',
                  fontWeight: 600,
                  color: '#CBD5E1',
                  marginBottom: '6px',
                }}
              >
                {item.stage}
              </div>

              <div
                style={{
                  fontSize: '0.72rem',
                  color: '#64748B',
                  lineHeight: 1.35,
                }}
              >
                {item.desc}
              </div>
            </div>

            {idx < items.length - 1 && (
              <div
                style={{
                  position: 'absolute',
                  right: '-10px',
                  zIndex: 2,
                  width: '20px',
                  height: '20px',
                  borderRadius: '50%',
                  background: '#15171F',
                  border: '1px solid rgba(255, 255, 255, 0.12)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#94A3B8',
                }}
              >
                <ArrowRight size={10} />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
