import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { api } from '../services/api';
import { EmployerResolutionRequest } from '../types';

describe('Employer Intelligence API Route Prefix & Error Contracts', () => {
  const originalFetch = globalThis.fetch;
  let fetchSpy: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    fetchSpy = vi.fn();
    globalThis.fetch = fetchSpy as unknown as typeof fetch;
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
    vi.restoreAllMocks();
  });

  describe('A. Employer List Endpoint (/api/v1/employers)', () => {
    it('invokes /api/v1/employers with correct prefix and no duplicate /api/api', async () => {
      fetchSpy.mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      } as Response);

      await api.getEmployers();

      expect(fetchSpy).toHaveBeenCalledTimes(1);
      const requestedUrl = fetchSpy.mock.calls[0][0] as string;
      expect(requestedUrl).toMatch(/\/api\/v1\/employers$/);
      expect(requestedUrl).not.toMatch(/\/api\/api\//);
      expect(requestedUrl).not.toMatch(/(?<!\/api)\/v1\/employers$/);
    });

    it('preserves limit and offset pagination parameters on /api/v1/employers', async () => {
      fetchSpy.mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      } as Response);

      await api.getEmployers({ limit: 10, offset: 20 });

      expect(fetchSpy).toHaveBeenCalledTimes(1);
      const requestedUrl = fetchSpy.mock.calls[0][0] as string;
      expect(requestedUrl).toContain('/api/v1/employers?limit=10&offset=20');
      expect(requestedUrl).not.toContain('/api/api');
      expect(requestedUrl).not.toMatch(/(?<!\/api)\/v1\/employers\?/);
    });
  });

  describe('B. Employer Resolution Endpoint (/api/v1/employers/resolve)', () => {
    it('invokes /api/v1/employers/resolve with POST method, intact body, and no duplicate prefix', async () => {
      const mockResponse = {
        query_name: 'Acme Test Corp',
        query_market_id: 'USA',
        resolution_match_type: 'NO_MATCH',
        resolved_company_id: null,
        review_status: 'CONFIRMED_DISTINCT',
        candidates: [],
        governance_caveat: 'Strict resolution policy',
      };

      fetchSpy.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const payload: EmployerResolutionRequest = {
        candidate_name: 'Acme Test Corp',
        market_id: 'USA',
        statutory_authority: 'US_SEC',
        statutory_identifier: '0001018724',
      };

      const result = await api.resolveEmployer(payload);

      expect(fetchSpy).toHaveBeenCalledTimes(1);
      const [requestedUrl, options] = fetchSpy.mock.calls[0] as [string, RequestInit];
      expect(requestedUrl).toMatch(/\/api\/v1\/employers\/resolve$/);
      expect(requestedUrl).not.toMatch(/\/api\/api\//);
      expect(requestedUrl).not.toMatch(/(?<!\/api)\/v1\/employers\/resolve$/);
      expect(options?.method).toBe('POST');
      expect(options?.headers).toEqual({ 'Content-Type': 'application/json' });
      expect(JSON.parse(options?.body as string)).toEqual(payload);
      expect(result).toEqual(mockResponse);
    });
  });

  describe('C. Employer Detail Endpoint (/api/v1/employers/{company_id})', () => {
    it('invokes /api/v1/employers/{company_id} with URL-encoded identifier', async () => {
      const mockProfile = {
        company_id: 'cmp_test/123@#',
        company_name: 'Test Corp',
        headquarters_country: 'US',
        company_category: 'OTHER_INTERNATIONAL',
        operating_markets: ['US'],
        source_references: [],
        verification_status: 'UNVERIFIED',
        locations: [],
      };

      fetchSpy.mockResolvedValueOnce({
        ok: true,
        json: async () => mockProfile,
      } as Response);

      await api.getEmployerDetail('cmp_test/123@#');

      expect(fetchSpy).toHaveBeenCalledTimes(1);
      const requestedUrl = fetchSpy.mock.calls[0][0] as string;
      expect(requestedUrl).toContain('/api/v1/employers/cmp_test%2F123%40%23');
      expect(requestedUrl).not.toContain('/api/api');
      expect(requestedUrl).not.toMatch(/(?<!\/api)\/v1\/employers\//);
    });
  });

  describe('D. Error Behavior & Distinction', () => {
    it('distinguishes HTTP 404 from empty registry by throwing an error instead of returning []', async () => {
      fetchSpy.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        text: async () => '{"detail": "Employer not found"}',
      } as Response);

      await expect(api.getEmployers()).rejects.toThrow(/API error \(404\)/);
    });

    it('handles HTTP 422 validation errors by propagating the rejection', async () => {
      fetchSpy.mockResolvedValueOnce({
        ok: false,
        status: 422,
        statusText: 'Unprocessable Entity',
        text: async () => '{"detail": "candidate_name required"}',
      } as Response);

      await expect(api.resolveEmployer({ candidate_name: '' })).rejects.toThrow(/API error \(422\)/);
    });

    it('does not silently convert network failures into empty results', async () => {
      fetchSpy.mockRejectedValueOnce(new TypeError('Failed to fetch'));

      await expect(api.getEmployers()).rejects.toThrow('Failed to fetch');
    });

    it('preserves null resolved_company_id as a valid unmerged entity state', async () => {
      fetchSpy.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          query_name: 'Distinct Co',
          resolution_match_type: 'NO_MATCH',
          resolved_company_id: null,
          review_status: 'CONFIRMED_DISTINCT',
          candidates: [],
          governance_caveat: 'Strict resolution policy',
        }),
      } as Response);

      const res = await api.resolveEmployer({ candidate_name: 'Distinct Co' });
      expect(res.resolved_company_id).toBeNull();
      expect(res.review_status).toBe('CONFIRMED_DISTINCT');
    });

    it('preserves manual review required distinction from automatic resolution', async () => {
      fetchSpy.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          query_name: 'Ambiguous Co',
          resolution_match_type: 'AMBIGUOUS_CANDIDATE',
          resolved_company_id: null,
          review_status: 'MANUAL_REVIEW_REQUIRED',
          candidates: [
            {
              target_company_id: 'cand_1',
              target_company_name: 'Ambiguous Co Inc',
              target_market_id: 'USA',
              match_type: 'AMBIGUOUS_CANDIDATE',
              similarity_score: 0.88,
              shared_brand_detected: true,
              is_subsidiary_relationship: false,
              evidence_summary: 'Duplicate collision',
              review_status: 'MANUAL_REVIEW_REQUIRED',
              requires_human_approval: true,
            },
          ],
          governance_caveat: 'Strict resolution policy',
        }),
      } as Response);

      const res = await api.resolveEmployer({ candidate_name: 'Ambiguous Co' });
      expect(res.review_status).toBe('MANUAL_REVIEW_REQUIRED');
      expect(res.resolved_company_id).toBeNull();
      expect(res.candidates[0].requires_human_approval).toBe(true);
    });
  });
});
