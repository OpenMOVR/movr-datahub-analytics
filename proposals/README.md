# Proposals Directory

This directory contains **RFCs (Requests for Comments)** for significant features, changes, and data wrangling rules.

---

## Directory Structure

```
proposals/
├── README.md                           # This file
├── templates/                          # Proposal templates
│   ├── feature-proposal-template.md    # For new features
│   └── rule-proposal-template.md       # For wrangling rules
├── rules/                              # Data wrangling rule proposals
│   └── YYYY-MM-DD-rule-name.md
├── transforms/                         # Small, testable field-level transformations
│   └── YYYY-MM-DD-transform-name.md
├── accepted/                           # Accepted proposals
│   └── YYYY-MM-DD-feature-name.md
├── rejected/                           # Rejected proposals (with reasoning)
│   └── YYYY-MM-DD-feature-name.md
├── deferred/                           # Deferred for future consideration
│   └── YYYY-MM-DD-feature-name.md
└── YYYY-MM-DD-feature-name.md          # Active proposals (root level)
```

---

## Proposal Process

### 1. Check Existing Proposals

Before creating a new proposal:
- Search this directory for similar ideas

- See also: `proposals/BRANCHING_STRATEGY.md` for recommended branch names, PR types and examples (useful for transform-style RFCs and prototypes)
- Check [FEATURES.md](../FEATURES.md) for planned features
- Review [DATA_WRANGLING_TRACKER.md](../DATA_WRANGLING_TRACKER.md) for existing rules

### 2. Choose Template

- **Feature Proposal**: Use `templates/feature-proposal-template.md`
- **Data Wrangling Rule**: Use `templates/rule-proposal-template.md`
- **Transform Proposal**: Use `templates/rule-proposal-template.md` (keeps proposals light — see "Transforms" SOP below)

### 3. Create Proposal

Copy the appropriate template and name your file:

**Feature proposals:**
```
proposals/YYYY-MM-DD-descriptive-feature-name.md
```

**Rule proposals:**
```
proposals/rules/YYYY-MM-DD-descriptive-rule-name.md
```

### 4. Submit Pull Request

1. Create a branch: `git checkout -b rfc/your-proposal-name`
2. Add your proposal file
3. Commit: `git commit -m "RFC: Your Proposal Title"`
4. Push and create PR with label `rfc` or `rule-proposal`

### 5. Discussion & Revision

- Community and team provide feedback on the PR
- Author addresses comments and revises proposal
- Discussion continues until consensus

### 6. Decision

Proposals are:
- **Accepted**: Moved to `accepted/`, added to FEATURES.md or DATA_WRANGLING_TRACKER.md
- **Rejected**: Moved to `rejected/` with documented reasoning
- **Deferred**: Moved to `deferred/` for future reconsideration

### 7. Implementation

Once accepted:
- Implementation PR references the proposal
- Feature/rule is built, tested, documented
- Status updated in tracking documents

---

## Proposal Guidelines

### What Requires a Proposal?

**Yes, create a proposal for:**
- New major features or modules
- API changes or additions
- New data wrangling rule categories
 - New transform / derived field that combines or consolidates multiple source fields into one canonical value (e.g., a single ambulation status column derived from multiple columns). These should be proposed as lightweight rule proposals under `proposals/rules/` or `proposals/transforms/` for clarity.
- Architectural changes
- Breaking changes
- New data sources or integrations

**No, just create an issue for:**
- Bug fixes
- Documentation improvements
- Minor optimizations
- Small enhancements to existing features

### Good Proposals Include

1. **Clear Problem Statement**: What problem are you solving?
2. **Detailed Design**: How will it work technically?
3. **Examples**: Show how users will use it
4. **Alternatives**: What other approaches were considered?
5. **Impact Analysis**: Backwards compatibility, performance, testing

---

## Transforms SOP (short & pragmatic)

Transforms are frequent and small: a single canonical field derived from multiple inputs to answer a repeatable analytic question. Keep them short and conservative.

Key points:
- Keep the spec focused: inputs, precedence/logic, outputs, and minimal audit fields.
- Default to non-destructive behavior: produce a canonical field plus an audit/issue column rather than overwriting original values.
- Provide unit tests and one integration example; avoid heavy documentation — aim for clarity and reproducibility.
- Location: prefer `proposals/rules/` or `proposals/transforms/` with filenames `YYYY-MM-DD-descriptive-transform.md`.
- Use `rule-proposal-template.md` as a baseline and keep the proposal lean.

---

---

## Active Proposals

| Proposal | Author | Date | Status | Links |
|----------|--------|------|--------|-------|
| [001: Cohort Builder Architecture](001-cohort-builder-architecture.md) | Andre Daniel Paredes | 2025-11-20 | 💡 Proposed | [Quick Ref](001-QUICK-REFERENCE.md) · [Patterns](../docs/DATA_WRANGLING_PATTERNS.md) |

---

## Recently Accepted

| Proposal | Accepted Date | Implemented |
|----------|---------------|-------------|
| (None yet) | | |

---

## Recently Rejected

| Proposal | Rejected Date | Reason |
|----------|---------------|--------|
| (None yet) | | |

---

## Questions?

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed contribution guidelines.

Open a GitHub Discussion if you have questions about the proposal process.

---

**Last Updated**: 2025-11-21
**Created By**: Andre Daniel Paredes
**Maintained By**: Andre Daniel Paredes
