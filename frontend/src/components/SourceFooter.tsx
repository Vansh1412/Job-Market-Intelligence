import React from 'react';

interface SourceFooterProps {
  sourceFile?: string;
  phaseTag?: string;
  date?: string;
}

export const SourceFooter: React.FC<SourceFooterProps> = ({
  sourceFile = 'reports/phase6_repository_audit.md',
  phaseTag = 'Phase 6 Integration',
  date = 'October 2026',
}) => {
  return (
    <footer
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '14px 4px',
        borderTop: '1px solid rgba(255, 255, 255, 0.06)',
        fontSize: '0.74rem',
        color: '#64748B',
        marginTop: '12px',
      }}
    >
      <div>
        Source: <code style={{ color: '#94A3B8', fontFamily: 'var(--font-mono)' }}>{sourceFile}</code> ({phaseTag})
      </div>
      <div>
        Frozen Results Registry · INT234 Predictive Analytics · {date}
      </div>
    </footer>
  );
};
