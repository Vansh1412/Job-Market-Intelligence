/**
 * JobIntel Motion System Design Tokens
 * ====================================
 * Unified, calm, professional animation constants, easings, and reusable
 * Framer Motion variants for modern analytics product UX.
 * 
 * Core Philosophy:
 * - Premium, fast, calm, intuitive, professional.
 * - Max duration for page transitions <= 250ms (never blocks user interaction).
 * - Full compliance with WCAG 2.1 AA prefers-reduced-motion.
 */

import { useState, useEffect } from 'react';
import type { Variants, Transition } from 'framer-motion';

// ---------------------------------------------------------------------------
// 1. TIMING CONSTANTS (seconds)
// ---------------------------------------------------------------------------
export const DURATION = {
  fast: 0.15,      // 150ms: micro-interactions, tooltips, tags
  normal: 0.24,    // 240ms: page transitions, wizard steps, drawers
  slow: 0.45,      // 450ms: chart initial bar growth, hero reveals
  ambient: 16.0,   // 16s: continuous background drift
} as const;

// ---------------------------------------------------------------------------
// 2. EASING CURVES
// ---------------------------------------------------------------------------
export const EASING = {
  easeOut: [0.16, 1, 0.3, 1] as const,     // snappy entrance, smooth settling
  easeInOut: [0.4, 0, 0.2, 1] as const,   // balanced symmetrical transitions
  linear: [0, 0, 1, 1] as const,          // constant velocity for ambient drift
} as const;

export const transitionFast: Transition = {
  duration: DURATION.fast,
  ease: EASING.easeOut,
};

export const transitionNormal: Transition = {
  duration: DURATION.normal,
  ease: EASING.easeOut,
};

// ---------------------------------------------------------------------------
// 3. ACCESSIBILITY: REDUCED MOTION HOOK
// ---------------------------------------------------------------------------
export function usePrefersReducedMotion(): boolean {
  const [prefersReduced, setPrefersReduced] = useState<boolean>(() => {
    if (typeof window === 'undefined') return false;
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  });

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    const handleChange = (e: MediaQueryListEvent) => setPrefersReduced(e.matches);

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  return prefersReduced;
}

// ---------------------------------------------------------------------------
// 4. REUSABLE MOTION VARIANTS
// ---------------------------------------------------------------------------

/** Global Page Transition: calm opacity fade + subtle 6px upward settle */
export const pageTransitionVariants: Variants = {
  initial: {
    opacity: 0,
    y: 6,
  },
  animate: {
    opacity: 1,
    y: 0,
    transition: {
      duration: DURATION.normal,
      ease: EASING.easeOut,
    },
  },
  exit: {
    opacity: 0.96,
    transition: {
      duration: 0.14,
      ease: 'easeOut',
    },
  },
};

/** Staggered Card Container: parent container for KPI cards & lists */
export const containerStaggerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.06,
      delayChildren: 0.04,
    },
  },
};

/** Individual Card Entrance */
export const itemFadeUpVariants: Variants = {
  hidden: {
    opacity: 0,
    y: 8,
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.28,
      ease: EASING.easeOut,
    },
  },
};

/** Hero Entrance Sequence (Landing & Subpages) */
export const heroSequenceVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.08,
      delayChildren: 0.05,
    },
  },
  initial: { opacity: 0 },
  animate: {
    opacity: 1,
    transition: {
      staggerChildren: 0.08,
      delayChildren: 0.05,
    },
  },
};

export const heroItemVariants: Variants = {
  hidden: {
    opacity: 0,
    y: 10,
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.32,
      ease: EASING.easeOut,
    },
  },
  initial: {
    opacity: 0,
    y: 10,
  },
  animate: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.32,
      ease: EASING.easeOut,
    },
  },
};

/** Salary Calculator: Direction-Aware Wizard Slide */
export const wizardSlideVariants: Variants = {
  enter: (direction: number) => ({
    x: direction > 0 ? 18 : -18,
    opacity: 0,
  }),
  center: {
    x: 0,
    opacity: 1,
    transition: {
      duration: DURATION.normal,
      ease: EASING.easeOut,
    },
  },
  exit: (direction: number) => ({
    x: direction > 0 ? -18 : 18,
    opacity: 0,
    transition: {
      duration: 0.16,
      ease: 'easeIn',
    },
  }),
};

/** Salary Prediction Result Reveal */
export const resultRevealVariants: Variants = {
  hidden: {
    opacity: 0,
    scale: 0.985,
    y: 8,
  },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: {
      duration: 0.38,
      ease: EASING.easeOut,
    },
  },
};

/** Detail Panel / Drawer Crossfade */
export const detailCrossfadeVariants: Variants = {
  hidden: {
    opacity: 0,
    y: 4,
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: DURATION.fast,
      ease: 'easeOut',
    },
  },
};

/** Hover & Tap Micro-Interaction Props */
export const buttonInteractionProps = {
  whileHover: { y: -1.5, scale: 1.012, transition: { duration: 0.15, ease: EASING.easeOut } },
  whileTap: { scale: 0.985, transition: { duration: 0.1 } },
};

export const cardInteractionProps = {
  whileHover: { y: -2, transition: { duration: 0.2, ease: EASING.easeOut } },
};
