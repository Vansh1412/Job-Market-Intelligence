import React from 'react';
import { ResearchQuestion } from '../types';

interface RQCardProps {
  rq: ResearchQuestion;
}

export const ResearchQuestionCard: React.FC<RQCardProps> = ({ rq }) => {
  return (
    <div
      className="ji-card"
      style={{
        padding: '22px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        position: 'relative',
        borderTop: `2px solid ${rq.color}`,
        height: '100%',
      }}
    >
      <div>
        {/* RQ Number & Status Pill */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '10px',
          }}
        >
          <span
            style={{
              fontSize: '0.74rem',
              fontWeight: 700,
              color: rq.color,
              letterSpacing: '0.06em',
              textTransform: 'uppercase',
            }}
          >
            {rq.number}
          </span>
          <span
            style={{
              fontSize: '0.67rem',
              fontWeight: 700,
              padding: '2px 8px',
              borderRadius: '12px',
              background: `${rq.color}18`,
              border: `1px solid ${rq.color}35`,
              color: rq.color,
              letterSpacing: '0.04em',
            }}
          >
            {rq.status}
          </span>
        </div>

        {/* Title */}
        <h3
          style={{
            fontSize: '1.25rem',
            fontWeight: 700,
            color: '#FFFFFF',
            letterSpacing: '-0.02em',
            marginBottom: '8px',
          }}
        >
          {rq.title}
        </h3>

        {/* Question Prompt */}
        <div
          style={{
            fontSize: '0.85rem',
            fontStyle: 'italic',
            color: '#94A3B8',
            marginBottom: '14px',
            lineHeight: 1.45,
          }}
        >
          "{rq.question}"
        </div>

        {/* Empirical Finding */}
        <p
          style={{
            fontSize: '0.86rem',
            color: '#CBD5E1',
            lineHeight: 1.6,
            marginBottom: '18px',
          }}
        >
          {rq.finding}
        </p>
      </div>

      {/* Metrics Chips */}
      {rq.metrics && rq.metrics.length > 0 && (
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '6px',
            paddingTop: '14px',
            borderTop: '1px solid rgba(255, 255, 255, 0.06)',
          }}
        >
          {rq.metrics.map((m, idx) => (
            <div
              key={idx}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                fontSize: '0.78rem',
              }}
            >
              <span style={{ color: '#64748B' }}>{m.label}</span>
              <span style={{ color: '#F8FAFC', fontWeight: 600, fontFamily: 'var(--font-mono)' }}>
                {m.value}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
