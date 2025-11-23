# Proposal 001 - Quick Reference

**See full proposal:** [001-cohort-builder-architecture.md](001-cohort-builder-architecture.md)
**See implementation patterns:** [../docs/DATA_WRANGLING_PATTERNS.md](../docs/DATA_WRANGLING_PATTERNS.md)

---

## What We Learned from Summary Command

### 6 Key Patterns Implemented

1. **Field Name Resolution**
   - Check actual field names first: `dstype`, `enroldt`, `encntdt`
   - Fall back to legacy: `DISEASE`, `ENROLLMENT_DATE`, etc.
   - Documented in: `config/field_mappings.yaml`

2. **Duplicate Column Handling**
   - When merging baseline + longitudinal: Drop duplicates from longitudinal FIRST
   - Rule: Baseline always wins (demographics/diagnosis are source of truth)
   - Fields: `dstype`, `dob`, `sex`, `enroldt`, `usndr`

3. **Registry Filtering**
   - Handle field name variations: `usndr`, `REGISTRY`, `DATA_SOURCE`
   - Handle data type variations: Binary (0/1) vs String ("MOVR")
   - Semantic awareness: `usndr=1` means USNDR, not DataHub

4. **Temporal Aggregation (Current)**
   - Summary uses ALL encounters (needed for counts)
   - Missing: First/last encounter, field-specific strategies

5. **Date Parsing**
   - Suppress warnings with `warnings.catch_warnings()`
   - Still handle errors with `errors="coerce"`

6. **Groupby Patterns**
   - Count unique: `groupby().nunique()`
   - Count occurrences: `groupby().size()`
   - Average: `groupby().mean()`
   - Pivot for display

---

## What We Need for Cohort Building

### The Problem

**Baseline Tables** (one record per participant):
- `demographics_maindata`
- `diagnosis_maindata`

**Longitudinal Tables** (multiple records per participant):
- `encounter_maindata`
- `log_maindata`

**Repeat Groups** (nested within encounters):
- `encounter_medication_rg`
- `encounter_hospitalization_rg`

### The Questions

1. **Which encounter?**
   - First visit?
   - Last visit?
   - All visits?

2. **Per-field temporal logic?**
   - `height`: Use most recent non-null
   - `wgt`: Use from selected encounter
   - `alsfrstl`: Use most recent assessment
   - `fvc`: Use within last 12 months

3. **Disease-specific rules?**
   - DMD: Steroid use (check medication repeat groups)
   - ALS: ALSFRS-R progression (temporal comparison)
   - SMA: SMN copy number (baseline only)

4. **eCRF-specific rules?**
   - Pulmonary function: Most recent within 12 months
   - Cardiac: May be in ECG or Echo
   - Surgery history: Ever occurred vs current status

---

## The Solution: Configuration-Driven Architecture

### New Config Structure
```
config/cohort_building/
├── baseline_fields.yaml          # Which fields from baseline
├── derived_age_fields.yaml       # NEW: Age calculations & naming
├── temporal_resolution.yaml      # How to handle time
├── disease_rules/
│   ├── dmd.yaml                 # DMD-specific rules
│   ├── als.yaml
│   └── sma.yaml
└── ecrf_rules/
    ├── pulmonary_function.yaml  # PFT handling
    ├── cardiac_assessment.yaml
    └── medications.yaml
```

### IMPORTANT: Naming Convention for Derived Fields

**MOVR Field Naming Standards:**
- **IQVIA Product:** `ALL_CAPS` (e.g., `FACPATID`, `CASE_ID`)
- **Original Data:** `lowercase` (e.g., `dstype`, `enroldt`, `dob`)
- **MOVR Processed:** `CamelCase` (e.g., `Age_At_Enrollment`, `Age_At_Diagnosis`)

This makes it immediately clear:
1. System/product fields (ALL_CAPS)
2. Captured clinical data (lowercase)
3. Calculated/derived (CamelCase)

### Temporal Strategies

**Built-in strategies:**
1. `first_encounter` - Participant's first visit
2. `last_encounter` - Most recent visit
3. `all_encounters` - Keep all (longitudinal)
4. `most_recent_non_null` - Per-field, use latest non-null
5. `specific_timepoint` - Within N days of target date
6. `field_specific_last` - Different strategy per field

**Example: Field-Specific**
```yaml
fields:
  height:
    strategy: most_recent_non_null
    reason: "Height stabilizes in adulthood"

  wgt:
    strategy: last_encounter
    reason: "Weight fluctuates, use current"

  fvc:
    strategy: within_timeframe
    timeframe: 12 months
    reason: "PFTs should be recent"
```

### Disease-Specific Example (DMD)

**Steroid Use:**
```yaml
steroid_use:
  current_use:
    table: encounter_maindata
    strategy: last_encounter
    fields: [glcouse, glcregm, glcdose]

  ever_used:
    tables: [encounter_medication_rg, log_medication_rg]
    strategy: any_occurrence
    medication_names: [prednisone, deflazacort]

  derived_fields:
    - steroid_current: from encounter
    - steroid_ever: from medications
    - steroid_start_date: first occurrence
    - steroid_duration: calculated
```

**Ambulation Loss:**
```yaml
ambulation_status:
  fields: [amblloss, amblsdt]
  strategy: field_specific_last

  logic:
    - if amblloss == "Yes": use first "Yes" occurrence
    - else: use last encounter
```

### Cohort Builder API

```python
from movr.cohorts import CohortBuilder

builder = CohortBuilder()

# Simple cohort (last encounter)
cohort = builder.create_cohort(
    base_table="demographics",
    temporal_strategy="last_encounter",
    disease="DMD"
)

# Complex cohort (disease-specific rules)
cohort = builder.create_cohort_from_template(
    disease="DMD",
    template="ambulatory"  # Uses DMD ambulatory rules
)

# Custom cohort
cohort = builder.create_cohort(
    temporal_strategy="field_specific_last",
    disease="DMD",
    filters={"age": [4, 18], "amblloss": "No"},
    include_fields=["FACPATID", "dstype", "age", "steroid_current"]
)
```

---

## Implementation Phases

**Phase 1:** Foundation (2 weeks)
- Config structure
- Basic temporal strategies

**Phase 2:** Disease Rules (2 weeks)
- DMD, ALS, SMA rules
- Test with real data

**Phase 3:** eCRF Rules (2 weeks)
- Pulmonary, cardiac, medications
- Cross-table joins

**Phase 4:** Advanced (2 weeks)
- Field-specific resolution
- Derived fields
- Quality checks

---

## Open Questions

1. **Performance:** How to optimize for 10K+ participants?
2. **Versioning:** How to ensure reproducibility?
3. **Validation:** How to validate rules are correct?
4. **UI/UX:** CLI interface? Future web UI?

---

## Success Criteria

✅ Can build baseline cohorts
✅ Can join baseline + most recent encounter
✅ Can apply disease-specific rules
✅ Can handle field-level temporal resolution
✅ Can calculate derived fields
✅ Configuration is maintainable
✅ Performance <5 seconds for 10K participants
✅ Results are reproducible

---

## Next Actions

1. **Review** this proposal
2. **Prioritize** diseases (DMD first?)
3. **Begin** Phase 1 implementation
4. **Schedule** design review meeting

---

**Questions? Comments?**

Open an issue or discussion in the repository.

---

**Related Documents:**
- [Full Proposal](001-cohort-builder-architecture.md)
- [Current Patterns](../docs/DATA_WRANGLING_PATTERNS.md)
- [Field Mappings](../config/field_mappings.yaml)
- [Summary Command](../src/movr/cli/commands/summary.py)
