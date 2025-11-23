# Proposal & RFC Branching Strategy (recommended)

This short guide explains the suggested branching and PR workflow for proposal / transform work in this repository. It's intentionally lightweight so proposal authors can get feedback quickly and implement prototypes when appropriate.

---

## Goals

- Make proposal branches discoverable and consistent
- Separate RFC-only branches (discussion) from prototype implementation branches
- Provide clear examples for transform-style proposals (derived fields) so contributors know how to proceed

---

## Branch Naming Conventions

Use predictable prefixes so branches are easy to find and review.

- RFC / discussion branches:
  - `rfc/<short-descriptive-name>`
  - e.g. `rfc/transforms/consolidated-ambulation` or `rfc/transforms/ambulation-and-gc`

- Implementation / prototype branches:
  - `feat/<short-descriptive-name>` or `impl/<short-descriptive-name>`
  - e.g. `feat/transforms/consolidated-ambulation-plugin`

- Hotfix / small follow-ups:
  - `fix/<short-desc>`

Notes:
- Keep branch names short, lower-case, and use hyphens. Include the scope (`transforms`, `rules`, `cli`, etc.) to make code ownership obvious.

---

## PR Types and When to Use Them

Choose one of the following PR strategies depending on how much work you want to propose:

1) RFC / Proposal-only PR (recommended for early feedback)
   - Branch: `rfc/<name>`
   - Contents: proposal files (in `proposals/transforms/` or `proposals/rules/`), short TODOs
   - Goal: capture problem, proposed solution, tests/implementation checklist
   - Benefit: fast to review, encourages early feedback

2) RFC + Prototype PR (recommended when you want to demonstrate run-ready behaviour)
   - Branch: `rfc/<name>-with-prototype` or `feat/<name>-prototype`
   - Contents: proposal files + small plugin skeleton / unit tests / example notebook
   - Goal: reduce ambiguity and unblocks reviewers by providing runnable artifacts

3) Implementation-only PR (for maintainers or follow-ups after RFC)
   - Branch: `feat/<name>`
   - Contents: full implementation, tests, docs, integration examples

---

## Minimal PR Checklist (good for transforms)

- [ ] Does the PR include a short description and link to any RFC file?
- [ ] Are the inputs, outputs, and non-destructive behavior described?
- [ ] Are unit tests included for key branches (edge cases and typical branches)?
- [ ] Is there an audit/evidence column or descriptive logging for ambiguous cases?
- [ ] If a prototype is included: is there a small example notebook demonstrating before/after?

---

## Example branches for our current transforms (suggested)

1) Consolidated Ambulation (RFC-only):
   - Branch: `rfc/transforms/consolidated-ambulation`
   - Files in PR: `proposals/transforms/2025-11-21-consolidated-ambulation-transform.md`
   - Description: lightweight RFC that defines `Consolidated_ambulation` and `Ambulatory_status` with TODOs for plugin and tests.

2) DMD Glucocorticoid Exposure (RFC-only):
   - Branch: `rfc/transforms/dmd-glucocorticoid-exposure`
   - Files in PR: `proposals/transforms/2025-11-21-dmd-glucocorticoid-exposure-transform.md`
   - Description: DMD-scoped transform RFC that defines `Glucocorticoid_exposure` and `Gc_evidence` with mapping and test TODOs.

If you want to include prototypes in the same branches, append `-with-prototype` and include a small plugin and tests.

---

## Example local commands

Create RFC branch + push
```bash
git checkout -b rfc/transforms/consolidated-ambulation
git add proposals/transforms/2025-11-21-consolidated-ambulation-transform.md
git commit -m "RFC: Consolidated ambulation transform"
git push -u origin HEAD
```

Create RFC + prototype branch
```bash
git checkout -b rfc/transforms/consolidated-ambulation-with-prototype
# add plugin file, tests, and small example notebook
git add plugins/ tests/ notebooks/examples
git commit -m "RFC + prototype: Consolidated ambulation transform"
git push -u origin HEAD
```

---

If you want, I can also add a GitHub PR template or a short CONTRIBUTING snippet to help reviewers identify the PR type at a glance.
