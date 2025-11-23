# Data Wrangling Rule Proposal: DMD Glucocorticoid Exposure Flag

> NOTE: This proposal has been moved to the lightweight transforms folder:
> `proposals/transforms/2025-11-21-dmd-glucocorticoid-exposure-transform.md`
> Please review and use the transforms copy as the canonical location.

- **Author**: Andre Daniel Paredes
- **Date**: 2025-11-21
- **Category**: Normalization | Business Rule | Transform
- **Priority**: Medium
- **Status**: Proposed
- **Rule ID**: (proposed: DT-GC-001)

---

## Summary

Create a reliable, auditable DMD-specific transformation that consolidates multiple clinical inputs into a single `Glucocorticoid_exposure` field to indicate whether a patient is taking (or has recently taken) systemic glucocorticoids. This helps cohort selection and stratified analyses where treatment exposure must be consistently defined.

This rule is limited to Duchenne muscular dystrophy (DMD) cohorts because exposure implications and clinical practice vary by condition.

---

## Motivation

### Problem Statement
Exposure to systemic glucocorticoids is an important modifier for disease trajectories in DMD. Data sources capture this information in multiple places (medications list, free-text notes, structured med flags, visit-level boolean fields). Analysts currently implement ad-hoc logic that is inconsistent between studies.

### Impact
- Improves repeatability for cohort selection and treatment-effect analyses.
- Reduces silent differences that bias comparative studies.

---

## Rule Specification

### Scope

**Tables Affected**:
- medication_prescriptions (where available), encounter_maindata, medication flags

**Fields Ingested** (example):
- `med_name`, `med_class`, `med_dose`, `started_date`, `stopped_date`, `med_flag_gc` (any boolean)
- visit-level `glucocorticoid` or medication list text

**New Output Fields**:
- `Glucocorticoid_exposure` — Enum: `Yes`, `No`, `Unknown`, `Possible` (if conflicting evidence)
- `Gc_evidence` — compact audit summary (source(s) that led to decision)

**When to apply**: After medication parsing and standardization (normalize drug names/classes first).

### Input Requirements
- Medication parsing / standardization has run (e.g., med name canonicalization to recognized glucocorticoid classes like prednisone, deflazacort, methylprednisolone).

### Rule Logic (concise)

1. If canonical medication table contains a present/globally active glucocorticoid (name or ATC class) within a clinically relevant window => `Yes`.
2. If explicit `med_flag_gc == False` or absence of any med / med-class evidence and authorized negative flag => `No`.
3. If only ambiguous or free-text evidence (e.g., `possible`, `tapering`, or old stopped dates) => `Possible` and include `Gc_evidence` for manual review.
4. If no pertinent evidence / missing data => `Unknown`.

### Edge Cases
- Multiple conflicting entries: prefer explicit medication records with active dates; if conflict arises (e.g., record says stopped last visit and started again at earlier date), prefer most recent active status and record the conflict in `Gc_evidence`.
- Route/local steroid (topical inhaled) should be excluded unless explicitly systemic in coding.

### Strictness Modes
- Strict: raise error for missing medication canonicalization step or for ambiguous entries tagged `Possible`.
- Permissive: emit `Possible` or `Unknown` and add audit logs; pipeline continues.

---

## Implementation Notes

- Best implemented as a plugin that depends on the medication normalization component. Provide a mapping table for glucocorticoid synonyms and classes.
- Output includes both the canonical enum and a short `Gc_evidence` text column with the reason and source(s).

### Pseudocode
```python
def determine_gc_exposure(row):
    # Check canonical medication list / med class
    # Check med_flag_gc, med_name, started/stopped dates
    return exposure, evidence

df[['Glucocorticoid_exposure', 'Gc_evidence']] = df.apply(determine_gc_exposure, axis=1, result_type='expand')
```

---

## Tests and Validation
- Unit tests for known glucocorticoid names / synonyms, date window behavior, negative flags and conflicting evidence handling.
- Integration run with medication normalization component to verify expected counts vs. manual chart review on a small sample.

## Rollout & Tracking
- Proposed ID: DT-GC-001
- After acceptance: add mapping table for glucocorticoids to `config/field_mappings.yaml` or `plugins/` and add an example notebook demonstrating the rule.

---

## Notes
- Conservative approach recommended — favor auditability and `Possible`/`Unknown` over incorrect `Yes/No` assignments.
- This rule is intentionally DMD-scoped; consider future generalization once patterns are stable and validated.
