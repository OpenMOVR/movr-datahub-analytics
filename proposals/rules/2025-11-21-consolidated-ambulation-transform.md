# Data Wrangling Rule Proposal: Consolidated Ambulation Status

> NOTE: This proposal has been moved to the lightweight transforms folder:
> `proposals/transforms/2025-11-21-consolidated-ambulation-transform.md`
> Please review and use the transforms copy as the canonical location.

- **Author**: Andre Daniel Paredes
- **Date**: 2025-11-21
- **Category**: Normalization | Business Rule | Transform
- **Priority**: High
- **Status**: Proposed
- **Rule ID**: (proposed: DT-AMB-001)

---

## Summary

Create a small, testable transformation that produces one canonical field representing patient ambulation status for conditions where multiple source fields are used (e.g., DMD and ALS). This reduces duplicate logic across analyses and makes downstream interpretations consistent and auditable.

This rule also proposes a light-weight sub-rule to normalize age units commonly used in ambulation logic (convert months to years where appropriate) to avoid inconsistent age thresholds in rules.

---

## Motivation

### Problem Statement
Clinical datasets include multiple, overlapping fields that imply ambulation status (examples: `ambulatn`, `curramb`, `amblost`/`amblloss`, `whlchr`, etc.). Analytical queries repeatedly re-implement multi-field logic which is error-prone and inconsistent across analyses.

### Impact
- Affects exploratory and outcome analyses that filter by ambulatory status (cohort selection, survival, longitudinal models).
- Conflicting or missing values lead to inaccurate cohort counts and analysis bias.

---

## Rule Specification

### Scope

**Tables Affected**:
- `encounter_maindata` (or equivalent encounter-level table where these fields exist)

**Fields Affected** (example names; match local schema):
- `ambulatn` (ambulation at enrollment)
- `curramb` (current ambulation description)
- `amblost` / `amblloss` (lost ambulation flag)
- `whlchr` (wheelchair usage)
- `Age_at_encounter_months` or `Age_at_encounter` (age in months)

**New Output Fields**:
- `Consolidated_ambulation` (text / categorical canonical label)
- `Ambulatory_status` (Yes / No / Unknown) — optional, derived for quick boolean filtering

**When to apply**: As part of wrangling/normalization stage for encounter-level data, after core parsing/normalization of the raw fields.

### Input Requirements
- Required: at least one of `curramb`, `ambulatn`, `amblost`/`amblloss`, or `whlchr` present.
- Age must be present when any age-bound decisions are required. If age is stored in months, conversion sub-rule should run first.

### Rule Logic (concise)

1. If age < 36 months (3 years) => `Consolidated_ambulation = 'N/A - patient is under age 3 at time of encounter'`
2. When `amblost` is present and True => flag as `Not ambulatory` unless conflicting current ambulation (mark as `INCONSISTENT INFORMATION` and flag for review).
3. If `amblost` is missing: apply lookup and precedence:
   - Wheelchair permanent => Not ambulatory (unless `curramb` explicitly says otherwise => inconsistency)
   - `curramb` available => use `curramb` (but map to standardized labels: `Not ambulatory`, `Ambulatory without difficulty`, `Ambulatory with difficulty`, `Unknown`)
   - If only `ambulatn` (enrollment) exists and `curramb` missing: if `ambulatn == 'Yes'` and `Total_encounters == 1`, return `'Ambulatory with enrollment'` else map by `whlchr` when present.
4. Set `Ambulatory_status` to `No` if `Consolidated_ambulation` contains `'Not ambulatory'`; `Yes` if it contains `'Ambulatory'`; `Unknown` if `Unknown`.

### Edge Cases
- Conflicting values across fields => set `Consolidated_ambulation` to `INCONSISTENT INFORMATION: <brief reason>` and add audit flag for manual review.
- Missing age or invalid age units => run age-normalization sub-rule or flag for review.

### Strictness Modes
- Strict: raise validation if required fields are missing or conflicts cannot be resolved.
- Permissive (recommended default): produce canonical value, add audit log entries and a `Consolidation_issue` column for downstream review.

---

## Implementation Approach

1. Implement as a small plugin rule in `plugins/` (Python function) compatible with YAML-driven wrangling pipeline.
2. Provide unit tests and small example datasets demonstrating DMD and ALS behavior.
3. Export both `Consolidated_ambulation` and `Ambulatory_status` to the target table.

### Pseudocode Snippet
```python
def consolidate_ambulation(row):
    # apply precedence described above and return canonical label
    return canonical_label

# Pipeline usage example
df['Consolidated_ambulation'] = df.apply(consolidate_ambulation, axis=1)
df['Ambulatory_status'] = df['Consolidated_ambulation'].map(map_to_boolean)
```

---

## Tests and Validation
- Unit tests for all branches: DMD (using `amblost` + wheelchair + curramb + enroll-only), ALS (curramb + amblloss), missing/unknown behaviour.
- Integration test on sample hub dataset ensuring stable counts for a canonical cohort query.

## Rollout & Tracking
- Proposed ID: DT-AMB-001
- After acceptance: add to `DATA_WRANGLING_TRACKER.md` and include an example notebook demonstrating the plugin.

---

## Notes
- Keep the rule compact and conservative — prefer audit flags over destructive corrections.
- This rule seeds a small canonical field that should be favored by analysis code and docs going forward.
