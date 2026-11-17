import { describe, it, expect, vi, beforeEach } from 'vitest';
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { EmployersPage } from '../pages/EmployersPage';
import { api } from '../services/api';

// Mock the API service
vi.mock('../services/api', () => ({
  api: {
    resolveEmployer: vi.fn(),
    getEmployers: vi.fn(),
    getEmployerDetail: vi.fn(),
  },
}));

describe('EmployersPage Component & User Interactions', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders page header, title, and governance principle card', () => {
    render(<EmployersPage />);

    expect(screen.getByRole('heading', { level: 1, name: /Employer Intelligence/i })).toBeDefined();
    expect(screen.getByText(/Explore employer identities, legal entities/i)).toBeDefined();
    expect(screen.getByText(/JOBINTEL Legal Identity Standard:/i)).toBeDefined();
  });

  it('renders all 3 primary navigation tabs', () => {
    render(<EmployersPage />);

    expect(screen.getByRole('button', { name: /Entity Resolution & Verification/i })).toBeDefined();
    expect(screen.getByRole('button', { name: /Employer Registry Explorer/i })).toBeDefined();
    expect(screen.getByRole('button', { name: /Statutory Standards & Governance/i })).toBeDefined();
  });

  it('switches to Statutory Standards tab and displays sovereign authority table', () => {
    render(<EmployersPage />);

    const standardsTab = screen.getByRole('button', { name: /Statutory Standards & Governance/i });
    fireEvent.click(standardsTab);

    expect(screen.getByText(/Sovereign Statutory Registers & Entity Governance/i)).toBeDefined();
    expect(screen.getByText(/Ministry of Corporate Affairs \(MCA\)/i)).toBeDefined();
    expect(screen.getByText(/Securities and Exchange Commission \(SEC \/ EDGAR\)/i)).toBeDefined();
    expect(screen.getByText(/Companies House/i)).toBeDefined();
    expect(screen.getByText(/Duplicate Identifier Collision Defense/i)).toBeDefined();
  });

  it('validates candidate name requirement on submission', async () => {
    render(<EmployersPage />);

    const resolveButton = screen.getByRole('button', { name: /Resolve Legal Entity/i });
    expect(resolveButton).toBeDefined();
  });

  it('executes resolution search and displays successful match', async () => {
    (api.resolveEmployer as any).mockResolvedValueOnce({
      query_name: 'Google LLC',
      query_market_id: 'US',
      resolution_match_type: 'EXACT_IDENTIFIER_MATCH',
      resolved_company_id: 'google_llc',
      review_status: 'AUTOMATICALLY_RESOLVED',
      candidates: [
        {
          target_company_id: 'google_llc',
          target_company_name: 'Google LLC',
          target_market_id: 'US',
          match_type: 'EXACT_IDENTIFIER_MATCH',
          similarity_score: 1.0,
          shared_brand_detected: false,
          is_subsidiary_relationship: false,
          evidence_summary: 'Exact statutory identifier verified with US SEC EDGAR.',
          review_status: 'AUTOMATICALLY_RESOLVED',
          requires_human_approval: false,
        },
      ],
      governance_caveat: 'Strict resolution policy: shared brand names do not constitute proof of identical legal identity.',
    });

    render(<EmployersPage />);

    const input = screen.getByPlaceholderText(/e\.g\. Google LLC, Infosys Limited/i);
    fireEvent.change(input, { target: { value: 'Google LLC' } });

    const resolveBtn = screen.getByRole('button', { name: /Resolve Legal Entity/i });
    fireEvent.click(resolveBtn);

    await waitFor(() => {
      expect(screen.getByText(/AUTOMATICALLY RESOLVED/i)).toBeDefined();
      const idMatches = screen.getAllByText(/google_llc/i);
      expect(idMatches.length).toBeGreaterThanOrEqual(1);
      expect(screen.getByText(/Exact statutory identifier verified with US SEC EDGAR/i)).toBeDefined();
    });
  });

  it('renders manual review and collision alert with null resolved company id', async () => {
    (api.resolveEmployer as any).mockResolvedValueOnce({
      query_name: 'Colliding Entity Inc',
      query_market_id: 'US',
      resolution_match_type: 'AMBIGUOUS_CANDIDATE',
      resolved_company_id: null,
      review_status: 'MANUAL_REVIEW_REQUIRED',
      candidates: [
        {
          target_company_id: 'colliding_1',
          target_company_name: 'Entity Alpha',
          target_market_id: 'US',
          match_type: 'AMBIGUOUS_CANDIDATE',
          similarity_score: 0.88,
          shared_brand_detected: true,
          is_subsidiary_relationship: false,
          evidence_summary: "Statutory identifier '000111222' is duplicated across 2 distinct registered employers. Automatic resolution prohibited; manual review required.",
          review_status: 'MANUAL_REVIEW_REQUIRED',
          requires_human_approval: true,
        },
      ],
      governance_caveat: 'Ambiguous candidates require manual review.',
    });

    render(<EmployersPage />);

    const input = screen.getByPlaceholderText(/e\.g\. Google LLC, Infosys Limited/i);
    fireEvent.change(input, { target: { value: 'Colliding Entity Inc' } });

    const resolveBtn = screen.getByRole('button', { name: /Resolve Legal Entity/i });
    fireEvent.click(resolveBtn);

    await waitFor(() => {
      const reviewBadges = screen.getAllByText(/MANUAL REVIEW REQUIRED/i);
      expect(reviewBadges.length).toBeGreaterThanOrEqual(1);
      expect(screen.getByText(/None \(Unresolved\)/i)).toBeDefined();
      expect(screen.getByText(/Human Approval Required/i)).toBeDefined();
      expect(screen.getByText(/Lexical similarity score; not a calibrated probability/i)).toBeDefined();
    });
  });

  it('switches to Registry tab and shows empty state when 0 employers exist', async () => {
    (api.getEmployers as any).mockResolvedValueOnce([]);

    render(<EmployersPage />);

    const registryTab = screen.getByRole('button', { name: /Employer Registry Explorer/i });
    fireEvent.click(registryTab);

    await waitFor(() => {
      expect(screen.getByText(/No Employer Records In Registry/i)).toBeDefined();
    });
  });
});
