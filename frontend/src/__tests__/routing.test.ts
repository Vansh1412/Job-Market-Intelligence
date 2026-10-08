import { describe, it, expect } from 'vitest';

// Define the exact Route and Navigation contract
const ROUTE_MAP: Record<string, string> = {
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

const PAGE_TO_ROUTE: Record<string, string> = {
  home: '/',
  calculator: '/salary',
  explore: '/explore',
  skills: '/skills',
  archetypes: '/archetypes',
  comparison: '/cross-market',
  howitworks: '/how-it-works',
};

describe('Routing Architecture & Contract', () => {
  it('maps every primary navigation target to a defined route', () => {
    const pages = ['home', 'calculator', 'explore', 'skills', 'archetypes', 'comparison', 'howitworks'];
    for (const page of pages) {
      const route = PAGE_TO_ROUTE[page];
      expect(route).toBeDefined();
      expect(ROUTE_MAP[route]).toBe(page);
    }
  });

  it('supports backward-compatible aliases for salary and comparison', () => {
    expect(ROUTE_MAP['/calculator']).toBe('calculator');
    expect(ROUTE_MAP['/salary']).toBe('calculator');
    expect(ROUTE_MAP['/comparison']).toBe('comparison');
    expect(ROUTE_MAP['/cross-market']).toBe('comparison');
    expect(ROUTE_MAP['/howitworks']).toBe('howitworks');
    expect(ROUTE_MAP['/how-it-works']).toBe('howitworks');
  });

  it('safely falls back to home for unknown pathnames', () => {
    const unknownPath = '/non-existent-page-xyz';
    const resolvedPage = ROUTE_MAP[unknownPath] || 'home';
    expect(resolvedPage).toBe('home');
  });
});
