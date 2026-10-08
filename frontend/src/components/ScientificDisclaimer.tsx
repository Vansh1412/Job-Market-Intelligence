import React from 'react';
import { ShieldAlert } from 'lucide-react';

interface ScientificDisclaimerProps {
  customText?: string;
}

export const ScientificDisclaimer: React.FC<ScientificDisclaimerProps> = ({ customText }) => {
  const defaultText =
    'All reported salary figures and model predictions reflect observational labor market associations within the audited tech job corpus. Skill presence indicates market valuation correlation and does not imply causal wage enhancement.';

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'flex-start',
        gap: '12px',
        padding: '14px 18px',
        borderRadius: '10px',
        background: 'rgba(139, 92, 246, 0.05)',
        border: '1px solid rgba(139, 92, 246, 0.2)',
        marginTop: '28px',
        marginBottom: '16px',
      }}
    >
      <ShieldAlert size={18} style={{ color: '#A78BFA', marginTop: '2px', flexShrink: 0 }} />
      <div style={{ fontSize: '0.82rem', color: '#CBD5E1', lineHeight: 1.55 }}>
        <strong style={{ color: '#E2E8F0', fontWeight: 600 }}>Methodological Notice: </strong>
        {customText || defaultText}
      </div>
    </div>
  );
};
