import React from 'react';
import { motion } from 'framer-motion';
import { heroItemVariants, heroSequenceVariants } from '../utils/motionTokens';

interface PageHeroProps {
  badgeText?: string;
  badge?: string;
  badgeColor?: string;
  accentColor?: string;
  title: string;
  subtitle: string;
  actions?: React.ReactNode;
}

export const PageHero: React.FC<PageHeroProps> = ({
  badgeText,
  badge,
  badgeColor,
  accentColor,
  title,
  subtitle,
  actions,
}) => {
  const displayBadge = badge || badgeText || 'RESEARCH VERIFIED · FROZEN SSOT';
  const displayColor = accentColor || badgeColor || '#8B5CF6';

  return (
    <motion.div
      variants={heroSequenceVariants}
      initial="initial"
      animate="animate"
      style={{
        marginBottom: '28px',
        paddingBottom: '22px',
        borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
        position: 'relative',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          gap: '20px',
        }}
      >
        <div>
          {displayBadge && (
            <motion.div
              variants={heroItemVariants}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                padding: '3px 10px',
                borderRadius: '20px',
                background: `${displayColor}18`,
                border: `1px solid ${displayColor}40`,
                color: displayColor,
                fontSize: '0.72rem',
                fontWeight: 700,
                letterSpacing: '0.06em',
                textTransform: 'uppercase',
                marginBottom: '12px',
              }}
            >
              <span
                style={{
                  width: '5px',
                  height: '5px',
                  borderRadius: '50%',
                  background: displayColor,
                }}
              />
              {displayBadge}
            </motion.div>
          )}

          <motion.h1
            variants={heroItemVariants}
            style={{
              fontSize: '2.4rem',
              fontWeight: 800,
              letterSpacing: '-0.03em',
              color: '#FFFFFF',
              lineHeight: 1.15,
              marginBottom: '10px',
            }}
          >
            {title}
          </motion.h1>

          <motion.p
            variants={heroItemVariants}
            style={{
              fontSize: '1rem',
              color: '#94A3B8',
              lineHeight: 1.6,
              maxWidth: '860px',
            }}
          >
            {subtitle}
          </motion.p>
        </div>

        {actions && (
          <motion.div variants={heroItemVariants}>
            {actions}
          </motion.div>
        )}
      </div>
    </motion.div>
  );
};
