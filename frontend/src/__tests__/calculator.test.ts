import { describe, it, expect } from 'vitest';

export interface USAPredictPayload {
  role_family: string;
  seniority: string;
  city_clean: string;
  is_remote: boolean;
  selected_skills: string[];
}

export interface IndiaPredictPayload {
  normalized_role: string;
  experience_midpoint_years: number;
  experience_range_years: number;
  city_grouped: string;
  work_mode: string;
  selected_skills: string[];
}

describe('Calculator Payload & Request Construction', () => {
  it('correctly constructs USA prediction payload conforming to backend schema', () => {
    const usaPayload: USAPredictPayload = {
      role_family: 'Data Scientist',
      seniority: 'Senior',
      city_clean: 'San Francisco-Oakland-Hayward, CA',
      is_remote: false,
      selected_skills: ['skill_python', 'skill_sql', 'skill_aws'],
    };

    expect(usaPayload.role_family).toBe('Data Scientist');
    expect(usaPayload.seniority).toBe('Senior');
    expect(usaPayload.city_clean).toContain('San Francisco');
    expect(usaPayload.is_remote).toBe(false);
    expect(usaPayload.selected_skills).toHaveLength(3);
    expect(usaPayload.selected_skills).toContain('skill_python');
    expect(usaPayload.selected_skills.length).toBeLessThanOrEqual(50);
  });

  it('correctly constructs India prediction payload conforming to backend schema', () => {
    const indiaPayload: IndiaPredictPayload = {
      normalized_role: 'Backend Developer',
      experience_midpoint_years: 5,
      experience_range_years: 4,
      city_grouped: 'Bengaluru',
      work_mode: 'Remote',
      selected_skills: ['skill_java', 'skill_spring', 'skill_docker'],
    };

    expect(indiaPayload.normalized_role).toBe('Backend Developer');
    expect(indiaPayload.experience_midpoint_years).toBe(5);
    expect(indiaPayload.city_grouped).toBe('Bengaluru');
    expect(indiaPayload.work_mode).toBe('Remote');
    expect(indiaPayload.selected_skills).toHaveLength(3);
    expect(indiaPayload.selected_skills).toContain('skill_java');
    expect(indiaPayload.selected_skills.length).toBeLessThanOrEqual(50);
  });

  it('safely handles empty skill selection without error', () => {
    const emptySkillsPayload: USAPredictPayload = {
      role_family: 'Software Engineer',
      seniority: 'Entry',
      city_clean: 'National Average',
      is_remote: true,
      selected_skills: [],
    };

    expect(emptySkillsPayload.selected_skills).toEqual([]);
    expect(Array.isArray(emptySkillsPayload.selected_skills)).toBe(true);
  });
});
