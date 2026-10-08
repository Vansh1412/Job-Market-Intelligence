import React, { useState, useEffect } from 'react';
import { MarketProvider } from './context/MarketContext';
import { AtmosphericBackground } from './components/AtmosphericBackground';
import { AppHeader, NavigationPage } from './components/AppHeader';
import { AnimatePresence, motion } from 'framer-motion';
import { pageTransitionVariants } from './utils/motionTokens';

import { HomePage } from './pages/HomePage';
import { PredictorPage } from './pages/PredictorPage';
import { ExploreMarketPage } from './pages/ExploreMarketPage';
import { SkillsPage } from './pages/SkillsPage';
import { ArchetypesPage } from './pages/ArchetypesPage';
import { CrossMarketPage } from './pages/CrossMarketPage';
import { MethodologyPage } from './pages/MethodologyPage';

const ROUTE_MAP: Record<string, NavigationPage> = {
  '/': 'home',
  '/salary': 'calculator',
  '/calculator': 'calculator',
  '/explore': 'explore',
  '/skills': 'skills',
  '/archetypes': 'archetypes',
  '/cross-market': 'comparison',
  '/comparison': 'comparison',
  '/how-it-works': 'howitworks',
  '/howitworks': 'howitworks',
};

const PAGE_TO_ROUTE: Record<NavigationPage, string> = {
  home: '/',
  calculator: '/salary',
  explore: '/explore',
  skills: '/skills',
  archetypes: '/archetypes',
  comparison: '/cross-market',
  howitworks: '/how-it-works',
};

function getPageFromLocation(): NavigationPage {
  const hash = window.location.hash.replace(/^#\/?/, '/');
  if (hash && hash !== '/' && ROUTE_MAP[hash]) {
    return ROUTE_MAP[hash];
  }
  const path = window.location.pathname.replace(/\/$/, '') || '/';
  if (ROUTE_MAP[path]) {
    return ROUTE_MAP[path];
  }
  return 'home';
}

export const AppContent: React.FC = () => {
  const [activePage, setActivePage] = useState<NavigationPage>(() => getPageFromLocation());

  useEffect(() => {
    const handleLocationChange = () => {
      const page = getPageFromLocation();
      setActivePage(page);
    };

    window.addEventListener('popstate', handleLocationChange);
    window.addEventListener('hashchange', handleLocationChange);

    // Initial URL sync
    const initialPage = getPageFromLocation();
    const targetPath = PAGE_TO_ROUTE[initialPage] || '/';
    if (window.location.pathname !== targetPath) {
      window.history.replaceState({ page: initialPage }, '', targetPath);
    }

    return () => {
      window.removeEventListener('popstate', handleLocationChange);
      window.removeEventListener('hashchange', handleLocationChange);
    };
  }, []);

  const navigateTo = (page: NavigationPage) => {
    setActivePage(page);
    const targetPath = PAGE_TO_ROUTE[page] || '/';
    window.history.pushState({ page }, '', targetPath);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const renderActivePage = () => {
    switch (activePage) {
      case 'home':
        return <HomePage onNavigate={(p) => navigateTo(p as NavigationPage)} />;
      case 'calculator':
        return <PredictorPage onNavigate={(p) => navigateTo(p as NavigationPage)} />;
      case 'explore':
        return <ExploreMarketPage onNavigate={(p) => navigateTo(p as NavigationPage)} />;
      case 'skills':
        return <SkillsPage onNavigate={(p) => navigateTo(p as NavigationPage)} />;
      case 'archetypes':
        return <ArchetypesPage onNavigate={(p) => navigateTo(p as NavigationPage)} />;
      case 'comparison':
        return <CrossMarketPage />;
      case 'howitworks':
        return <MethodologyPage />;
      default:
        return <HomePage onNavigate={(p) => navigateTo(p as NavigationPage)} />;
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', position: 'relative' }}>
      {/* Living Multi-Color Atmospheric Background */}
      <AtmosphericBackground />

      {/* Global Application Header with 7 Primary Nav Links & Estimate My Salary CTA */}
      <AppHeader
        activePage={activePage}
        onSelectPage={(page) => navigateTo(page)}
      />

      {/* Main Product Container */}
      <main
        style={{
          flex: 1,
          padding: '36px 24px 60px 24px',
          maxWidth: '1240px',
          margin: '0 auto',
          width: '100%',
          position: 'relative',
          zIndex: 10,
        }}
      >
        <AnimatePresence mode="wait">
          <motion.div
            key={activePage}
            variants={pageTransitionVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            style={{ width: '100%' }}
          >
            {renderActivePage()}
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <MarketProvider>
      <AppContent />
    </MarketProvider>
  );
};

export default App;
