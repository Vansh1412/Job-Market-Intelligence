# Sprint 2 Employer Intelligence Design

**Status:** Feasibility and architecture only. No company, office, hiring, posting, salary, or headcount records were added or acquired.

## Existing foundation

Sprint 1 has typed `EmployerProfile`, `EmployerLocation`, source-reference and verification contracts in `src/backend/schemas/employer.py`, an empty registry in `src/backend/employers/registry.py`, and read-only list/detail routes. The registry is empty by design. This is sufficient for a foundation; it is not an employer intelligence dataset.

## Source feasibility

| Candidate source | Potential evidence | What it does not prove | Status / proposed use |
|---|---|---|---|
| Companies House Public Data API | UK registered company identity, status, SIC, registered office, public filing metadata | Active hiring, operating office, actual staff/headcount, current salaries or role openings | `REVIEW_REQUIRED`; optional entity disambiguation after terms, API credential, privacy and field-level review. No API access in planning. |
| Official employer website/careers page | Employer-published identity, stated office or live role at retrieval time | Other operating locations, role filled, complete vacancies, current status after retrieval | `REVIEW_REQUIRED` individually; manual verification or automation only if terms/access permit. |
| Licensed/official job advert aggregation | Could support a posting snapshot with source-provided dimensions | Hires, net job creation, total market vacancies | `REVIEW_REQUIRED` for exact dataset/terms. ONS/Textkernel aggregate demand is not company-level posting evidence. |
| Public reports/company disclosures | Evidence for stated facts at a date | Complete/realtime location, hiring or employee counts | `REVIEW_REQUIRED` per document and fact; preserve publication date and citation. |

Companies House says its API exposes public company data and requires an API key for public requests; developer guidance sets a 600 requests per five-minute limit and warns to protect keys. Companies House data-product guidance states public-register reuse is the reuser’s responsibility under applicable law. Company register data can include personal information, so avoid directors/PSC details and do not expose personal data. [API getting started](https://developer.company-information.service.gov.uk/get-started) · [Authentication](https://developer.company-information.service.gov.uk/authentication) · [Developer guidelines](https://developer.company-information.service.gov.uk/developer-guidelines) · [Data products and reuse](https://www.gov.uk/guidance/companies-house-data-products) · [Personal information guidance](https://www.gov.uk/guidance/your-personal-information-on-the-companies-house-register)

## Proposed future entities

Retain Sprint 1 employer and location model; extend only when backed by source evidence. Future entities may include:

- `Employer`: stable internal ID, Companies House number when verified, legal/trading names with source and observed dates, company status, source IDs.
- `EmployerLocation`: location type, country/region, exact evidence, observed/verified dates; registered office is a distinct location type from operating office.
- `JobPosting`: source posting ID/URL, employer link confidence, title/source text reference, location, observed first/last dates, status and retrieval provenance.
- `JobPostingSkill`, `JobPostingQualification`, `JobPostingExperience`: source statement plus extraction method/confidence; distinguish source-explicit from inferred.
- `JobPostingSalary`: preserve posted lower/upper amounts, currency, period, salary definition, pay frequency and source wording. No invented values or auto-conversions.
- `EmployerSource` and `HiringSnapshot`: source/collection method, timestamp, coverage, status and counts. Snapshot counts represent collected public ads, not hires.

## Verified identification rules

1. Match company legal name/number only with direct Companies House or official employer evidence; retain the exact source reference and observed date.
2. Treat brand/trading name to legal entity mapping as ambiguous until supported by an official page or filing.
3. Do not infer headquarters from registered office, or operating presence from a registry address.
4. A registered company does not imply that it is hiring. A posting does not imply a filled role.
5. For “multinational operating in market X,” require source evidence of an operating location in X; HQ country and operating markets are separate facts.
6. For live postings, preserve retrieval time and source status; respect robots, terms, rate limits, authentication, copyright and data-protection rules. No bypassing.
7. Store the minimum necessary fields; exclude director/PSC personal records and private contact data from career intelligence.

## Sprint 2 recommendation

Keep employer registry empty throughout Sprint 2 implementation unless a specific employer source and intended field use are approved and verified. Implement no scraping and no placeholder company records. Prioritize a UK aggregate salary/occupation vertical slice. Companies House could later serve identity resolution, subject to a separate precise terms/privacy decision; it is not a hiring source.
