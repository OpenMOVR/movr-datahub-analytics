# Data Wrangling Rules

**Comprehensive Data Processing Rules for MOVR DataHub Analytics**

**Last Updated:** 2025-11-20
**Author:** Andre Daniel Paredes

---

## Overview

This document specifies the data wrangling rules applied to MOVR registry data. These rules ensure data quality, consistency, and reproducibility across all analyses.

For implementation status, see [DATA_WRANGLING_TRACKER.md](DATA_WRANGLING_TRACKER.md).
For implemented patterns, see [docs/DATA_WRANGLING_PATTERNS.md](docs/DATA_WRANGLING_PATTERNS.md).

---

## Rule Categories

1. [Field Name Resolution](#1-field-name-resolution)
2. [Duplicate Handling](#2-duplicate-handling)
3. [Data Type Standardization](#3-data-type-standardization)
4. [Missing Value Handling](#4-missing-value-handling)
5. [Date Processing](#5-date-processing)
6. [Registry Filtering](#6-registry-filtering)
7. [Referential Integrity](#7-referential-integrity)
8. [Value Normalization](#8-value-normalization)

---

## 1. Field Name Resolution

### Problem
Field names vary across data sources and versions:
- MOVR DataHub uses lowercase field names (e.g., `dstype`, `enroldt`)
- Legacy exports may use different conventions (e.g., `DISEASE`, `ENROLLMENT_DATE`)

### Rules

#### R-101: Prioritized Field Name Lookup
**Always check actual field names before fallbacks.**

```python
# Check for disease column (actual field name first)
disease_col = None
for col in ["dstype", "DISEASE", "DIAGNOSIS", "PRIMARY_DIAGNOSIS"]:
    if col in df.columns:
        disease_col = col
        break
```

#### R-102: Field Mapping Configuration
**Document field mappings in `config/field_mappings.yaml`.**

```yaml
fields:
  disease:
    - dstype             # ACTUAL field name (priority 1)
    - DISEASE            # Fallback/legacy
    - DIAGNOSIS          # Fallback
    - PRIMARY_DIAGNOSIS  # Fallback
```

#### R-103: Fail-Fast on Missing Critical Fields
**Return early or raise error if required field not found.**

```python
if disease_col is None:
    return {}  # Or raise ValueError("Disease field not found")
```

### References
- Configuration: `config/field_mappings.yaml`
- Implementation: `src/movr/cli/commands/summary.py:83-90`
- Pattern: [docs/DATA_WRANGLING_PATTERNS.md](docs/DATA_WRANGLING_PATTERNS.md#pattern-1-field-name-resolution)

---

## 2. Duplicate Handling

### Problem
When merging baseline and longitudinal tables:
- Both may contain the same field (e.g., `dstype`, `dob`, `sex`)
- Pandas renames duplicates to `field_x` and `field_y`
- Unclear which version is authoritative

### Rules

#### R-201: Baseline Fields Take Precedence
**Demographic/diagnosis fields from baseline tables are source of truth.**

Fields that ALWAYS come from baseline:
- `FACPATID` (patient ID)
- `dstype` (disease type)
- `dob` (date of birth)
- `sex` (biological sex)
- `enroldt` (enrollment date)
- `usndr` (registry flag)
- Genetic/diagnosis fields

#### R-202: Drop Duplicate Columns Before Merge
**Remove duplicate columns from longitudinal table before joining.**

```python
# Drop disease column from encounter if it exists
if disease_col in encounter_df.columns:
    encounter_df = encounter_df.drop(columns=[disease_col])

merged = encounter_df.merge(
    demographics_df[["FACPATID", disease_col]],
    on="FACPATID",
    how="left"
)
```

#### R-203: Explicit Column Selection in Merges
**Always specify which columns to include from each table.**

```python
# Good: Explicit column selection
merged = encounter_df.merge(
    demographics_df[["FACPATID", "dstype", "dob"]],
    on="FACPATID"
)

# Bad: Implicit merge with duplicate columns
merged = encounter_df.merge(demographics_df, on="FACPATID")
```

### References
- Implementation: `src/movr/cli/commands/summary.py:170-173`
- Pattern: [docs/DATA_WRANGLING_PATTERNS.md](docs/DATA_WRANGLING_PATTERNS.md#pattern-2-duplicate-column-handling-in-merges)

---

## 3. Data Type Standardization

### Rules

#### R-301: Patient IDs as Strings
**Always store patient IDs as strings, not integers.**

```python
df["FACPATID"] = df["FACPATID"].astype(str)
```

Reason: IDs may have leading zeros or non-numeric characters.

#### R-302: Preserve Original Types from Parquet
**Trust Parquet column types over Excel type inference.**

#### R-303: Numeric Fields
**Convert numeric fields explicitly when needed.**

```python
df["age"] = pd.to_numeric(df["age"], errors="coerce")
```

---

## 4. Missing Value Handling

### Rules

#### R-401: Standardize NA Representations
**Convert various NA representations to pandas NA.**

Values treated as NA:
- Empty string (`""`)
- Whitespace-only string (`"   "`)
- `"NA"`, `"N/A"`, `"n/a"`
- `"NULL"`, `"null"`
- `"None"`, `"none"`
- `-999`, `-9999` (coded missing)

#### R-402: Preserve NA in Categorical Fields
**Do not fill NA in categorical fields without explicit reason.**

```python
# Good: Keep NA values
df["amblloss"].isna()

# Bad: Replace NA without reason
df["amblloss"].fillna("Unknown")
```

#### R-403: Document NA Handling Decisions
**When filling NA, document the rationale in code comments.**

---

## 5. Date Processing

### Rules

#### R-501: Suppress Date Parsing Warnings
**Use context manager to suppress pandas warnings.**

```python
import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore", UserWarning)
    df["ENROLLMENT_DATE"] = pd.to_datetime(df[date_col], errors="coerce")
```

#### R-502: Handle Invalid Dates with Coercion
**Convert invalid dates to NaT, not errors.**

```python
df["date"] = pd.to_datetime(df["date"], errors="coerce")
```

#### R-503: Extract Year/Month Components
**Create separate columns for year/month when needed for aggregation.**

```python
df["ENROLLMENT_YEAR"] = df["ENROLLMENT_DATE"].dt.year
df["ENROLLMENT_MONTH"] = df["ENROLLMENT_DATE"].dt.month
```

#### R-504: Date Validation
**Validate dates are within reasonable ranges.**

```python
# Flag future dates
df["date_invalid"] = df["ENROLLMENT_DATE"] > pd.Timestamp.now()

# Flag unreasonable past dates
df["date_invalid"] |= df["ENROLLMENT_DATE"] < pd.Timestamp("1900-01-01")
```

### References
- Implementation: `src/movr/cli/commands/summary.py:119-124`
- Pattern: [docs/DATA_WRANGLING_PATTERNS.md](docs/DATA_WRANGLING_PATTERNS.md#pattern-5-date-parsing-with-warning-suppression)

---

## 6. Registry Filtering

### Problem
Registry field varies in:
- Field name: `usndr`, `REGISTRY`, `DATA_SOURCE`
- Data type: Binary (0/1) vs string ("MOVR", "USNDR")
- Semantics: `usndr=1` means USNDR, not DataHub

### Rules

#### R-601: Registry Field Name Resolution
**Check multiple field names for registry indicator.**

```python
registry_col = None
for col in ["usndr", "REGISTRY", "DATA_SOURCE", "SOURCE"]:
    if col in df.columns:
        registry_col = col
        break
```

#### R-602: Type-Aware Registry Filtering
**Handle both binary and string registry indicators.**

```python
if registry_col == "usndr":
    # Binary flag: empty/null/0 = DataHub, 1/non-empty = USNDR
    datahub = df[(df[registry_col].isna()) |
                 (df[registry_col] == 0) |
                 (df[registry_col] == "")]
else:
    # String field: search for registry name
    datahub = df[df[registry_col].str.upper().str.contains("MOVR|DATAHUB")]
```

#### R-603: Graceful Fallback for Missing Registry
**Return unfiltered data if no registry field exists.**

```python
if registry_col is None:
    return df  # No filtering possible
```

### References
- Implementation: `src/movr/cli/commands/summary.py:54-78`
- Pattern: [docs/DATA_WRANGLING_PATTERNS.md](docs/DATA_WRANGLING_PATTERNS.md#pattern-3-registry-filtering-with-type-handling)

---

## 7. Referential Integrity

### Rules

#### R-701: Validate Foreign Keys
**Ensure FACPATID exists in demographics before joining.**

```python
# Check for orphan records
orphans = encounter_df[~encounter_df["FACPATID"].isin(demographics_df["FACPATID"])]
if len(orphans) > 0:
    logger.warning(f"Found {len(orphans)} orphan encounter records")
```

#### R-702: Cascade Filters to Related Tables
**When filtering base cohort, apply same filter to related tables.**

#### R-703: Document Relationship Assumptions
**Comment on expected cardinality (1:1, 1:N, M:N).**

---

## 8. Value Normalization

### Rules

#### R-801: Text Case Normalization
**Standardize text case for categorical comparisons.**

```python
df["disease"] = df["disease"].str.upper().str.strip()
```

#### R-802: Whitespace Trimming
**Remove leading/trailing whitespace from string fields.**

```python
df["field"] = df["field"].str.strip()
```

#### R-803: Value Range Validation
**Flag values outside expected ranges.**

```python
# Age validation
df["age_invalid"] = (df["age"] < 0) | (df["age"] > 120)
```

---

## Strictness Modes

The framework supports three strictness modes:

### Strict Mode
- Raises errors on rule violations
- Use for production pipelines
- Ensures data quality

### Permissive Mode (Default)
- Logs warnings but continues processing
- Use for exploratory analysis
- Flags issues without stopping

### Interactive Mode
- Prompts user for decisions
- Use for manual data review
- Allows case-by-case handling

```yaml
# config/config.yaml
options:
  strictness: permissive  # strict | permissive | interactive
```

---

## Age Calculation Rules

### R-901: Age Derivation from DOB
**Calculate age at any time point from DOB.**

```python
def years_between(date1, date2):
    """Calculate years between two dates."""
    if pd.isna(date1) or pd.isna(date2):
        return None
    dt1 = pd.to_datetime(date1)
    dt2 = pd.to_datetime(date2)
    years = (dt1 - dt2).days / 365.25
    return round(years, 2)
```

### R-902: Critical Age Fields
- `Age_At_Enrollment` = years_between(enroldt, dob)
- `Age_At_Diagnosis` = disease-specific (e.g., `dmddgnag` for DMD)
- `Age_At_Visit` = years_between(encntdt, dob)

### R-903: Age Validation
- Age < 0: Error (flag record)
- Age > 120: Warning (review record)
- Age at enrollment < 0: Exclude record

### References
- Proposal: [Proposal 001: Derived Age Fields](proposals/001-cohort-builder-architecture.md)
- Quick Reference: [proposals/001-QUICK-REFERENCE.md](proposals/001-QUICK-REFERENCE.md)

---

## Naming Conventions

### Field Naming Standards

| Type | Convention | Examples |
|------|------------|----------|
| IQVIA Product Fields | ALL_CAPS | `FACPATID`, `CASE_ID` |
| Original Clinical Data | lowercase | `dstype`, `enroldt`, `dob` |
| MOVR Processed/Derived | CamelCase | `Age_At_Enrollment`, `Age_At_Diagnosis` |

---

## Rule Implementation Tracking

| Rule ID | Status | Implemented In |
|---------|--------|----------------|
| R-101 | ✅ Implemented | summary.py:83-90 |
| R-102 | ✅ Implemented | field_mappings.yaml |
| R-103 | ✅ Implemented | summary.py:91-92 |
| R-201 | ✅ Implemented | summary.py (rule documented) |
| R-202 | ✅ Implemented | summary.py:170-173 |
| R-501 | ✅ Implemented | summary.py:119-124 |
| R-502 | ✅ Implemented | summary.py:123 |
| R-601 | ✅ Implemented | summary.py:56-61 |
| R-602 | ✅ Implemented | summary.py:66-78 |
| R-901 | 💡 Proposed | Proposal 001 |
| R-902 | 💡 Proposed | Proposal 001 |
| R-903 | 💡 Proposed | Proposal 001 |

---

## Related Documentation

- [DATA_WRANGLING_TRACKER.md](DATA_WRANGLING_TRACKER.md) - Implementation status tracker
- [docs/DATA_WRANGLING_PATTERNS.md](docs/DATA_WRANGLING_PATTERNS.md) - Implemented patterns
- [config/field_mappings.yaml](config/field_mappings.yaml) - Field name mappings
- [proposals/001-cohort-builder-architecture.md](proposals/001-cohort-builder-architecture.md) - Cohort builder proposal
- [CONTRIBUTING.md](CONTRIBUTING.md) - How to propose new rules

---

**Last Updated:** 2025-11-20
