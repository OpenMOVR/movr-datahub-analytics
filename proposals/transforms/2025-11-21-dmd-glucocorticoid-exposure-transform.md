# Transform Proposal: DMD Glucocorticoid Exposure Flag

- **Author**: Andre Daniel Paredes
- **Date**: 2025-11-21
- **Category**: Transform | Normalization
- **Priority**: Medium
- **Status**: Proposed

---

## Summary

Small, conservative transform that produces a `Glucocorticoid_exposure` enum and a short `Gc_evidence` text column for DMD cohorts. This transform standardizes medication-derived exposure information to a small set of canonical values useful for cohort selection and stratified analyses.

---

## Why this is a Transform

It consolidates multiple medication/flag fields into a single canonical field for a common analytic question (systemic glucocorticoid exposure). The scope is intentionally DMD-specific to avoid over-generalizing when evidence requirements differ across diseases.

---

## Minimal Implementation TODOs (for PR / Implementation)

- [ ] Add plugin `determine_gc_exposure(df)` in `plugins/` that consumes normalized medication listings and outputs `Glucocorticoid_exposure` and `Gc_evidence`.
- [ ] Add a small canonical mapping for glucocorticoid medications and classes to `config/field_mappings.yaml` (prednisone, deflazacort, methylprednisolone, etc.).
- [ ] Unit tests for Yes/No/Possible/Unknown cases, date-window behavior, and exclusion of topical/inhaled routes.
- [ ] Integration example showing counts and a short manual review sample to validate gold-standard behavior.
