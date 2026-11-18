# SPRINT 3B.3.3.4.6 — SEED INTEGRITY & CHECKSUM REPORT
**Sprint:** 3B.3.3.4.6  
**Document:** `05_seed_integrity_and_checksum_report.md`  
**Date:** 2026-11-18  
**Author:** Data Architect & Cryptographic Integrity Auditor  
**Status:** COMPLETE & VERIFIED  

---

## 1. Authoritative Seed Artifacts & Elimination of Split-Brain State

Sprint 3B.3.3.4.5 identified that two seed paths were previously floating in documentation and code:
1. `src/backend/data_catalog/staging_employers.json`
2. `data/processed/staging_employers.json`

In Sprint 3B.3.3.4.6, `data/processed/staging_employers.json` was permanently eliminated. A single authoritative location within the backend application package was standardized:
- **Seed Catalog:** [src/backend/data_catalog/staging_employers.json](file:///e:/Job%20Market/src/backend/data_catalog/staging_employers.json)
- **Companion Manifest:** [src/backend/data_catalog/staging_employers.manifest.json](file:///e:/Job%20Market/src/backend/data_catalog/staging_employers.manifest.json)

---

## 2. Deterministic Serialization & Line-Ending Normalization

To prevent hash divergence between Windows developer workstations (CRLF `\r\n`) and Linux cloud containers (LF `\n`), the serialization pipeline enforces explicit UNIX line endings:
```python
def serialize_profiles(profiles: List[EmployerProfile]) -> bytes:
    """Deterministically serialize employer profiles to UTF-8 bytes with UNIX LF."""
    raw_dicts = [p.model_dump() for p in profiles]
    json_text = json.dumps(raw_dicts, indent=2, sort_keys=True, ensure_ascii=False)
    # Guarantee standard UNIX LF line endings across all platforms
    normalized_text = json_text.replace("\r\n", "\n") + "\n"
    return normalized_text.encode("utf-8")
```

### Atomic File Write Semantics
Writes are performed atomically via a temporary file:
```python
tmp_path = p.with_suffix(p.suffix + ".tmp")
tmp_path.write_bytes(content_bytes)
os.replace(tmp_path, p)
```
This guarantees that file readers never observe partial or corrupt writes.

---

## 3. Cryptographic Companion Manifest

The generated companion manifest records the exact SHA-256 digest and file attributes:
```json
{
  "algorithm": "sha256",
  "candidate_ids": [
    "comp_au_atlassian",
    "comp_us_microsoft",
    "comp_uk_arm",
    "comp_sg_dbs",
    "comp_in_infosys"
  ],
  "env": "staging",
  "file_name": "staging_employers.json",
  "file_size_bytes": 5166,
  "generated_at": "2026-11-18T14:48:02.404847+00:00",
  "record_count": 5,
  "schema_version": "1.0",
  "sha256": "d0ead7dd297d6eeb5cfc7e35b1249e0813c52d02c4c7b48d04c5aac21c81d62d"
}
```

---

## 4. Verification Checksum Matrix

| Artifact Path | Size (Bytes) | Record Count | SHA-256 Digest | Status |
| :--- | :--- | :--- | :--- | :--- |
| `src/backend/data_catalog/staging_employers.json` | 5,166 | 5 | `d0ead7dd297d6eeb5cfc7e35b1249e0813c52d02c4c7b48d04c5aac21c81d62d` | **CERTIFIED** |
| `src/backend/data_catalog/staging_employers.manifest.json` | 425 | N/A | `c062c3f87b8d4f40f0f3531b40283a31c51206f6918d363f03bda98c69288c80` | **MATCHED** |
