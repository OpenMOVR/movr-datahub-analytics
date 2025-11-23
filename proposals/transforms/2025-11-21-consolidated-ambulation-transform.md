# Transform Proposal: Consolidated Ambulation Status

- **Author**: Andre Daniel Paredes
- **Date**: 2025-11-21
- **Category**: Transform | Normalization
- **Priority**: High
- **Status**: Proposed

---

## Summary

Small transform that produces a canonical `Consolidated_ambulation` field and an optional boolean `Ambulatory_status` by consolidating multiple source fields (e.g., `ambulatn`, `curramb`, `amblost`/`amblloss`, `whlchr`). This is intended to be lightweight, auditable, and non-destructive — a one-field answer to a frequent analysis question.

---

## Why this is a Transform

This is a field-level, derived transformation (not an architectural change). It reduces repeated ad-hoc logic in analysis code by providing a single canonical value for ambulatory status that downstream analyses can rely on.

---

## Minimal Implementation TODOs (for PR / Implementation)

- [ ] Add plugin function `consolidate_ambulation(df)` in `plugins/` that returns `Consolidated_ambulation` and `Ambulatory_status`.
- [ ] Add a short mapping table (if needed) for canonical `curramb` labels in `config/` or add mapping inline in plugin.
- [ ] Unit tests covering DMD and ALS logic branches, edge cases, and mapping to boolean status.
- [ ] Integration example / small notebook demonstrating before/after counts for a canonical cohort query.
- [ ] Audit column: include a small `Consolidation_issue` or `Consolidation_evidence` text field for conflicts.
