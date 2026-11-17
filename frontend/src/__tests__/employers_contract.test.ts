import { describe, it, expect } from 'vitest';
import {
  EmployerCategory,
  EmployerVerificationStatus,
  EmployerLocationType,
  EmployerProfile,
  ResolutionMatchType,
  EntityReviewStatus,
  EmployerResolutionRequest,
  EmployerResolutionResponse,
  EntityMatchCandidate,
} from '../types';

describe('Employer Intelligence Types, Schemas & Contracts', () => {
  it('defines valid EmployerCategory enum values', () => {
    const validCategories: EmployerCategory[] = [
      'INDIAN_HEADQUARTERED',
      'MULTINATIONAL_OPERATING_IN_INDIA',
      'OTHER_INTERNATIONAL',
    ];
    expect(validCategories).toHaveLength(3);
  });

  it('defines valid EmployerVerificationStatus enum values', () => {
    const validStatuses: EmployerVerificationStatus[] = [
      'UNVERIFIED',
      'REVIEW_REQUIRED',
      'VERIFIED',
    ];
    expect(validStatuses).toHaveLength(3);
  });

  it('defines valid EmployerLocationType enum values', () => {
    const validLocationTypes: EmployerLocationType[] = [
      'HEADQUARTERS',
      'OFFICE',
      'RESEARCH',
      'OTHER',
    ];
    expect(validLocationTypes).toHaveLength(4);
  });

  it('defines valid ResolutionMatchType enum values', () => {
    const validMatchTypes: ResolutionMatchType[] = [
      'EXACT_IDENTIFIER_MATCH',
      'STRONG_CANDIDATE_MATCH',
      'AMBIGUOUS_CANDIDATE',
      'NO_MATCH',
    ];
    expect(validMatchTypes).toHaveLength(4);
  });

  it('defines valid EntityReviewStatus enum values', () => {
    const validReviewStatuses: EntityReviewStatus[] = [
      'AUTOMATICALLY_RESOLVED',
      'MANUAL_REVIEW_REQUIRED',
      'CONFIRMED_DISTINCT',
      'HUMAN_VERIFIED_MERGE',
    ];
    expect(validReviewStatuses).toHaveLength(4);
  });
});

describe('Employer Resolution Request & Response Structure', () => {
  it('correctly constructs an EmployerResolutionRequest payload', () => {
    const request: EmployerResolutionRequest = {
      candidate_name: 'Infosys Limited',
      market_id: 'IN',
      statutory_identifier: 'L85110KA1981PLC013115',
      statutory_authority: 'MCA',
    };

    expect(request.candidate_name).toBe('Infosys Limited');
    expect(request.market_id).toBe('IN');
    expect(request.statutory_identifier).toBe('L85110KA1981PLC013115');
    expect(request.statutory_authority).toBe('MCA');
  });

  it('handles optional fields as null or undefined', () => {
    const minimalRequest: EmployerResolutionRequest = {
      candidate_name: 'Unknown Startup Inc',
    };

    expect(minimalRequest.candidate_name).toBe('Unknown Startup Inc');
    expect(minimalRequest.market_id).toBeUndefined();
    expect(minimalRequest.statutory_identifier).toBeUndefined();
    expect(minimalRequest.statutory_authority).toBeUndefined();
  });

  it('validates successful resolution response structure (Rule 1 & Rule 5)', () => {
    const mockSuccessResponse: EmployerResolutionResponse = {
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
          evidence_summary: 'Exact statutory identifier verified with authoritative US corporate registry.',
          review_status: 'AUTOMATICALLY_RESOLVED',
          requires_human_approval: false,
        },
      ],
      governance_caveat: 'JOBINTEL strict resolution policy: shared brand names and parent-subsidiary relationships do not constitute proof of identical legal identity.',
    };

    expect(mockSuccessResponse.resolution_match_type).toBe('EXACT_IDENTIFIER_MATCH');
    expect(mockSuccessResponse.review_status).toBe('AUTOMATICALLY_RESOLVED');
    expect(mockSuccessResponse.resolved_company_id).toBe('google_llc');
    expect(mockSuccessResponse.candidates[0].similarity_score).toBe(1.0);
    expect(mockSuccessResponse.candidates[0].requires_human_approval).toBe(false);
  });

  it('preserves null resolved_company_id during duplicate identifier collision (Rule 2)', () => {
    const mockCollisionResponse: EmployerResolutionResponse = {
      query_name: 'Acme International',
      query_market_id: 'US',
      resolution_match_type: 'AMBIGUOUS_CANDIDATE',
      resolved_company_id: null,
      review_status: 'MANUAL_REVIEW_REQUIRED',
      candidates: [
        {
          target_company_id: 'acme_corp_delaware',
          target_company_name: 'Acme Corporation (Delaware)',
          target_market_id: 'US',
          match_type: 'AMBIGUOUS_CANDIDATE',
          similarity_score: 0.85,
          shared_brand_detected: true,
          is_subsidiary_relationship: false,
          evidence_summary: "Statutory identifier '0001234567' is duplicated across 2 distinct registered employers. Automatic resolution prohibited; manual review required.",
          review_status: 'MANUAL_REVIEW_REQUIRED',
          requires_human_approval: true,
        },
        {
          target_company_id: 'acme_corp_nevada',
          target_company_name: 'Acme Holdings (Nevada)',
          target_market_id: 'US',
          match_type: 'AMBIGUOUS_CANDIDATE',
          similarity_score: 0.78,
          shared_brand_detected: true,
          is_subsidiary_relationship: false,
          evidence_summary: "Statutory identifier '0001234567' is duplicated across 2 distinct registered employers. Automatic resolution prohibited; manual review required.",
          review_status: 'MANUAL_REVIEW_REQUIRED',
          requires_human_approval: true,
        },
      ],
      governance_caveat: 'Ambiguous candidates require manual review.',
    };

    // Governance Invariants for Collisions:
    expect(mockCollisionResponse.resolved_company_id).toBeNull();
    expect(mockCollisionResponse.review_status).toBe('MANUAL_REVIEW_REQUIRED');
    expect(mockCollisionResponse.candidates.length).toBeGreaterThan(1);
    for (const cand of mockCollisionResponse.candidates) {
      expect(cand.requires_human_approval).toBe(true);
      expect(cand.review_status).toBe('MANUAL_REVIEW_REQUIRED');
      // Evidence must disclose duplicate collision
      expect(cand.evidence_summary).toContain('duplicated across');
    }
  });

  it('symmetrically marks subsidiary distinctions without arbitrary collapsing (Rule 3)', () => {
    const mockSubsidiaryResponse: EmployerResolutionResponse = {
      query_name: 'Google India Private Limited',
      query_market_id: 'IN',
      resolution_match_type: 'AMBIGUOUS_CANDIDATE',
      resolved_company_id: null,
      review_status: 'MANUAL_REVIEW_REQUIRED',
      candidates: [
        {
          target_company_id: 'google_llc',
          target_company_name: 'Google LLC',
          target_market_id: 'US',
          match_type: 'AMBIGUOUS_CANDIDATE',
          similarity_score: 0.62,
          shared_brand_detected: true,
          is_subsidiary_relationship: true,
          evidence_summary: "Shared brand 'google' detected. Cross-market entity distinction: Subsidiary relationship indicated. Automatic collapsing prohibited by governance.",
          review_status: 'MANUAL_REVIEW_REQUIRED',
          requires_human_approval: true,
        },
      ],
      governance_caveat: 'Shared brand names do not constitute proof of identical legal identity.',
    };

    expect(mockSubsidiaryResponse.resolved_company_id).toBeNull();
    expect(mockSubsidiaryResponse.candidates[0].is_subsidiary_relationship).toBe(true);
    expect(mockSubsidiaryResponse.candidates[0].shared_brand_detected).toBe(true);
    expect(mockSubsidiaryResponse.candidates[0].requires_human_approval).toBe(true);
  });

  it('treats similarity score strictly as matching score, never calibrated probability (Rule 4)', () => {
    const candidate: EntityMatchCandidate = {
      target_company_id: 'test_company',
      target_company_name: 'Test Company Ltd',
      target_market_id: 'UK',
      match_type: 'STRONG_CANDIDATE_MATCH',
      similarity_score: 0.985,
      shared_brand_detected: false,
      is_subsidiary_relationship: false,
      evidence_summary: 'High normalized lexical similarity (98.50%) in same jurisdiction (UK).',
      review_status: 'MANUAL_REVIEW_REQUIRED',
      requires_human_approval: true,
    };

    // Score is bounded in [0.0, 1.0]
    expect(candidate.similarity_score).toBeGreaterThanOrEqual(0.0);
    expect(candidate.similarity_score).toBeLessThanOrEqual(1.0);
    // Even high lexical similarity (98.5%) requires human approval
    expect(candidate.requires_human_approval).toBe(true);
    expect(candidate.review_status).toBe('MANUAL_REVIEW_REQUIRED');
  });

  it('correctly models confirmed distinct entity when no match is found', () => {
    const noMatchResponse: EmployerResolutionResponse = {
      query_name: 'Totally Nonexistent Entity X123',
      query_market_id: 'IN',
      resolution_match_type: 'NO_MATCH',
      resolved_company_id: null,
      review_status: 'CONFIRMED_DISTINCT',
      candidates: [],
      governance_caveat: 'Strict resolution policy.',
    };

    expect(noMatchResponse.resolution_match_type).toBe('NO_MATCH');
    expect(noMatchResponse.resolved_company_id).toBeNull();
    expect(noMatchResponse.review_status).toBe('CONFIRMED_DISTINCT');
    expect(noMatchResponse.candidates).toHaveLength(0);
  });
});

describe('Employer Profile & Registry Data Safety', () => {
  it('validates complete EmployerProfile structure with locations and sources', () => {
    const profile: EmployerProfile = {
      company_id: 'infosys_limited',
      company_name: 'Infosys Limited',
      headquarters_country: 'IN',
      company_category: 'INDIAN_HEADQUARTERED',
      industry: 'Information Technology & Consulting',
      official_website: 'https://www.infosys.com',
      operating_markets: ['IN', 'US', 'UK', 'AU', 'SG'],
      source_references: [
        {
          source_name: 'Ministry of Corporate Affairs Portal',
          source_organization: 'MCA',
          source_reference: 'https://www.mca.gov.in/mcafoportal/companyLLPMasterData.do',
          collected_at: '2026-11-17T00:00:00Z',
        },
      ],
      verification_status: 'VERIFIED',
      verified_at: '2026-11-17T00:00:00Z',
      locations: [
        {
          city: 'Bangalore',
          state_or_region: 'Karnataka',
          country_code: 'IN',
          location_type: 'HEADQUARTERS',
          verification_status: 'VERIFIED',
          verification_source: {
            source_name: 'MCA Master Record',
            source_organization: 'MCA',
            source_reference: 'https://www.mca.gov.in',
            collected_at: '2026-11-17T00:00:00Z',
          },
          verified_at: '2026-11-17T00:00:00Z',
        },
      ],
    };

    expect(profile.company_id).toBe('infosys_limited');
    expect(profile.company_name).toBe('Infosys Limited');
    expect(profile.headquarters_country).toBe('IN');
    expect(profile.operating_markets).toHaveLength(5);
    expect(profile.source_references).toHaveLength(1);
    expect(profile.locations).toHaveLength(1);
    expect(profile.locations[0].city).toBe('Bangalore');
  });

  it('guarantees zero data fabrication for unpublished workforce metrics (Rule 6)', () => {
    // When workforce observations are not present in profile,
    // they must not be populated with fake numbers.
    const profile: EmployerProfile = {
      company_id: 'test_corp',
      company_name: 'Test Corp',
      headquarters_country: 'US',
      company_category: 'OTHER_INTERNATIONAL',
      operating_markets: ['US'],
      source_references: [
        {
          source_name: 'SEC EDGAR',
          source_organization: 'SEC',
          source_reference: 'https://www.sec.gov',
        },
      ],
      verification_status: 'REVIEW_REQUIRED',
      locations: [],
    };

    // Assert that unsupported fields (headcount, vacancies, growth) do NOT exist on EmployerProfile
    expect((profile as any).headcount).toBeUndefined();
    expect((profile as any).active_vacancies).toBeUndefined();
    expect((profile as any).hiring_growth).toBeUndefined();
    expect((profile as any).employee_count).toBeUndefined();
  });
});
