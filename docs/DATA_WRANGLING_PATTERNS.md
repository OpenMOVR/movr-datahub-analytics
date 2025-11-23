# Data Wrangling Patterns - Current Implementation

**Document Purpose:** Document the data wrangling patterns implemented in `movr summary` that serve as foundation for cohort building architecture.

**Last Updated:** 2025-11-20
**Author:** Andre Daniel Paredes

---

## Overview

The `movr summary` command implements several key data wrangling patterns that will be formalized and extended in the cohort builder architecture (see [Proposal 001](../proposals/001-cohort-builder-architecture.md)).

---

## Pattern 1: Field Name Resolution

### Problem
Field names vary across:
- Different data sources (MOVR DataHub vs USNDR)
- Legacy vs current naming conventions
- Different table versions

### Solution
Prioritized field name checking with fallback chain.

### Implementation

**Location:** `src/movr/cli/commands/summary.py` lines 83-90, 101-113, etc.

```python
# Check for disease column (actual field name first)
disease_col = None
for col in ["dstype", "DISEASE", "DIAGNOSIS", "PRIMARY_DIAGNOSIS"]:
    if col in df.columns:
        disease_col = col
        break

if disease_col is None:
    return {}  # Cannot proceed without disease field
```

### Configuration
**File:** `config/field_mappings.yaml`

```yaml
fields:
  disease:
    - dstype             # ACTUAL field name in MOVR data (disease type)
    - DISEASE            # Fallback/legacy
    - DIAGNOSIS          # Fallback
    - PRIMARY_DIAGNOSIS  # Fallback
    - DX                 # Fallback
```

### Why This Works
1. **Prioritizes actual field names:** Checks `dstype` (actual MOVR field) before generic names
2. **Graceful degradation:** Falls back to legacy names if needed
3. **Explicit documentation:** `field_mappings.yaml` documents the priority order
4. **Fail-fast:** Returns early if no matching field found

### When to Use
- Any operation that needs to reference a field that might vary in name
- Cross-registry analysis (MOVR DataHub vs USNDR)
- Handling legacy data exports

---

## Pattern 2: Duplicate Column Handling in Merges

### Problem
When merging baseline (demographics) with longitudinal (encounter) tables:
- Both tables may contain the same field (e.g., `dstype`, `dob`, `sex`)
- Pandas renames duplicates to `field_x` and `field_y`
- Unclear which version is authoritative
- Leads to KeyError when trying to use `disease_col` after merge

### Example Error
```python
# Before fix:
merged = encounter_df.merge(
    demographics_df[["FACPATID", "dstype"]],
    on="FACPATID",
    how="left"
)

# Result: columns are dstype_x and dstype_y
summary = merged.groupby(["dstype", "ENCOUNTER_YEAR"]).size()
# KeyError: 'dstype'
```

### Solution
Explicitly drop duplicate columns from the longitudinal table BEFORE merging.

### Implementation

**Location:** `src/movr/cli/commands/summary.py` lines 170-173

```python
# Drop disease column from encounter if it exists (we want demographics version)
if disease_col in encounter_df.columns:
    encounter_df = encounter_df.drop(columns=[disease_col])

merged = encounter_df.merge(
    demographics_df[["FACPATID", disease_col]],
    on="FACPATID",
    how="left"
)

# Now can use disease_col directly:
summary = merged.groupby([disease_col, "ENCOUNTER_YEAR"]).size()
```

### Why This Works
1. **Explicit precedence:** Baseline fields always win
2. **No column renaming:** Avoids `_x` and `_y` suffixes
3. **Clear intent:** Code explicitly states which version is kept
4. **Prevents errors:** No KeyError from using wrong column name

### Rule Established
**Baseline fields (demographics, diagnosis) are source of truth.**

Fields that should ALWAYS come from baseline:
- `FACPATID` (patient ID)
- `dstype` (disease)
- `dob` (date of birth)
- `sex` (biological sex)
- `enroldt` (enrollment date)
- `usndr` (registry flag)
- Genetic/diagnosis fields

### When to Use
- Joining demographics + encounter
- Joining demographics + log
- Joining diagnosis + encounter
- Any baseline + longitudinal merge

---

## Pattern 3: Registry Filtering with Type Handling

### Problem
Registry field varies in:
- Field name: `usndr`, `REGISTRY`, `DATA_SOURCE`, `SOURCE`
- Data type: Binary flag (0/1) vs string ("MOVR", "USNDR")
- Semantics: `usndr=1` means USNDR, but `REGISTRY="MOVR"` means DataHub

### Solution
Check field existence first, then handle data type appropriately.

### Implementation

**Location:** `src/movr/cli/commands/summary.py` lines 53-77

```python
def filter_by_registry(self, df: pd.DataFrame) -> pd.DataFrame:
    """Filter data by registry if registry column exists."""
    # Check for actual field name first, then fallbacks
    registry_col = None
    for col in ["usndr", "REGISTRY", "DATA_SOURCE", "SOURCE"]:
        if col in df.columns:
            registry_col = col
            break

    if registry_col is None:
        return df  # No filtering possible

    if self.registry == "datahub":
        # For usndr field: assume empty/null/0 = DataHub, 1/Yes = USNDR
        if registry_col == "usndr":
            return df[(df[registry_col].isna()) |
                     (df[registry_col] == 0) |
                     (df[registry_col] == "")]
        else:
            # String field: search for MOVR or DataHub
            return df[df[registry_col].astype(str).str.upper()
                       .str.contains("MOVR|DATAHUB", na=False)]

    elif self.registry == "usndr":
        if registry_col == "usndr":
            # Binary flag: 1 or non-empty means USNDR
            return df[(df[registry_col].notna()) &
                     (df[registry_col] != 0) &
                     (df[registry_col] != "")]
        else:
            # String field: search for USNDR
            return df[df[registry_col].astype(str).str.upper()
                       .str.contains("USNDR", na=False)]
    else:  # all
        return df
```

### Why This Works
1. **Field name agnostic:** Works with any registry field name
2. **Type agnostic:** Handles both binary and string types
3. **Semantic aware:** Understands that `usndr=1` means USNDR, not DataHub
4. **Graceful fallback:** Returns unfiltered data if no registry field

### When to Use
- Any analysis that needs to separate registries
- Cross-registry comparison
- Registry-specific reports

---

## Pattern 4: Temporal Aggregation (Implicit)

### Problem
Encounter data has multiple records per participant. Which record(s) should be used?

### Current Implementation
**All encounters** are joined to demographics:

**Location:** `src/movr/cli/commands/summary.py` lines 154-194

```python
def get_encounters_by_disease_year(self) -> pd.DataFrame:
    """Get encounter counts by disease and year."""
    # Merge demographics (for disease) with encounters
    demographics_df = self.filter_by_registry(self.demographics)
    encounter_df = self.filter_by_registry(self.encounter)

    # ... field name resolution ...

    # Drop disease column from encounter if it exists
    if disease_col in encounter_df.columns:
        encounter_df = encounter_df.drop(columns=[disease_col])

    # Join ALL encounters to demographics
    merged = encounter_df.merge(
        demographics_df[["FACPATID", disease_col]],
        on="FACPATID",
        how="left"
    )

    # Result: Multiple rows per participant (one per encounter)
    # Count encounters by disease and year
    summary = merged.groupby([disease_col, "ENCOUNTER_YEAR"]).size()
```

### What's Missing
No way to specify:
- ❌ First encounter only
- ❌ Last encounter only
- ❌ Most recent value per specific field
- ❌ Encounter at specific time point

### This is Intentional
Summary statistics NEED all encounters:
- Total encounter counts
- Encounters per year
- Average encounters per participant

### For Cohort Building
We'll need additional strategies (see Proposal 001):
- `first_encounter`: Baseline clinical characteristics
- `last_encounter`: Current status
- `most_recent_non_null`: Per-field resolution (height, genetic results)
- `specific_timepoint`: Study baseline (within 90 days of enrollment)
- `field_specific_last`: Different strategy per field

---

## Pattern 5: Date Parsing with Warning Suppression

### Problem
Pandas shows UserWarning when parsing dates without explicit format:
```
UserWarning: Could not infer format, so each element will be parsed
individually, falling back to `dateutil`.
```

### Solution
Suppress warning while still handling errors gracefully.

### Implementation

**Location:** `src/movr/cli/commands/summary.py` lines 119-124, 147-150, etc.

```python
import warnings

# Before parsing dates:
df = df.copy()
# Suppress UserWarning about date format inference
with warnings.catch_warnings():
    warnings.simplefilter("ignore", UserWarning)
    df["ENROLLMENT_DATE"] = pd.to_datetime(df[date_col], errors="coerce")
df["ENROLLMENT_YEAR"] = df["ENROLLMENT_DATE"].dt.year
```

### Why This Works
1. **Suppresses noise:** Users don't see warning spam
2. **Still handles errors:** `errors="coerce"` converts invalid dates to NaT
3. **Context-specific:** Only suppresses during date parsing
4. **Safe:** Warning is informational, not critical

### When to Use
- Parsing dates from Excel with mixed formats
- Known date format variations that pandas handles correctly
- Production code where warnings add noise

---

## Pattern 6: Groupby Aggregation Patterns

### Count Unique Participants
```python
disease_counts = df.groupby("dstype")["FACPATID"].nunique().to_dict()
# Result: {"DMD": 727, "SMA": 545, ...}
```

### Count Occurrences
```python
encounters_by_year = merged.groupby([disease_col, "ENCOUNTER_YEAR"]).size()
# Result: MultiIndex with counts
```

### Average per Group
```python
avg_encounters = encounters_per_patient.groupby("Disease")["Encounters"].mean()
# Result: {"DMD": 3.2, "SMA": 2.8, ...}
```

### Pivot for Display
```python
pivot = recruitment.pivot(
    index="Disease",
    columns="Year",
    values="Participants"
).fillna(0).astype(int)
# Result: Wide format table for Rich display
```

---

## Summary of Patterns Implemented

| Pattern | Purpose | Location | Status |
|---------|---------|----------|--------|
| Field Name Resolution | Handle naming variations | Lines 83-90, 101-113, 133-140, etc. | ✅ Implemented |
| Duplicate Column Handling | Avoid merge conflicts | Lines 170-173, 217-218, 253-254 | ✅ Implemented |
| Registry Filtering | Type-aware filtering | Lines 53-77 | ✅ Implemented |
| All Encounters Join | Implicit temporal strategy | Lines 175-179 | ✅ Implemented |
| Date Parsing | Suppress warnings | Lines 119-124, 147-150, etc. | ✅ Implemented |
| Groupby Aggregations | Statistical summaries | Multiple locations | ✅ Implemented |

---

## Next Steps

See [Proposal 001: Cohort Builder Architecture](../proposals/001-cohort-builder-architecture.md) for:

1. **Formalization of these patterns** into reusable components
2. **Additional temporal strategies** (first encounter, last encounter, field-specific)
3. **Disease-specific rules** (DMD, ALS, SMA)
4. **eCRF-specific rules** (pulmonary function, cardiac assessment)
5. **Configuration-driven architecture** for maintainability at scale

---

## Code References

**Main Implementation:** `src/movr/cli/commands/summary.py`

**Key Methods:**
- `filter_by_registry()` - Lines 53-77
- `get_enrollment_by_disease()` - Lines 79-95
- `get_annual_recruitment()` - Lines 97-126
- `get_encounter_summary()` - Lines 128-152
- `get_encounters_by_disease_year()` - Lines 154-194
- `get_avg_encounters_per_participant_disease()` - Lines 196-233
- `get_avg_encounters_per_participant_disease_year()` - Lines 235-272

**Configuration:**
- `config/field_mappings.yaml` - Field name mappings

**Related:**
- [Proposal 001](../proposals/001-cohort-builder-architecture.md)
- [FEATURES.md](../FEATURES.md) - Feature tracking
- [DATA_WRANGLING_RULES.md](../DATA_WRANGLING_RULES.md) - General wrangling rules
