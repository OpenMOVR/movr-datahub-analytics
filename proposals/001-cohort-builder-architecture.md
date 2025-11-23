# Proposal 001: Cohort Builder Architecture

**Status:** 💡 Proposed
**Author:** Andre Daniel Paredes
**Date:** 2025-11-20
**Type:** Feature Proposal

---

## Executive Summary

This proposal outlines the architecture for a robust cohort building system that handles the complexity of combining baseline data (demographics, diagnosis) with longitudinal data (encounters) while supporting disease-specific and eCRF-specific rules.

---

## Background

### Current Implementation (Summary Command)

The `movr summary` command implements basic data wrangling patterns that we need to formalize and extend:

#### 1. **Field Name Resolution Pattern**
```python
# Pattern: Check actual field names first, then fallbacks
disease_col = None
for col in ["dstype", "DISEASE", "DIAGNOSIS"]:
    if col in df.columns:
        disease_col = col
        break
```

**Why this works:**
- Handles variations in field naming across data sources
- Prioritizes actual MOVR field names
- Falls back to generic/legacy names
- Documented in `config/field_mappings.yaml`

#### 2. **Duplicate Column Handling During Merge**
```python
# Problem: Both tables have dstype column
# Solution: Drop from encounter (keep demographics version)
if disease_col in encounter_df.columns:
    encounter_df = encounter_df.drop(columns=[disease_col])

merged = encounter_df.merge(
    demographics_df[["FACPATID", disease_col]],
    on="FACPATID",
    how="left"
)
```

**Why this is needed:**
- Baseline fields (demographics) are source of truth
- Encounter table may duplicate baseline fields for convenience
- Prevents `field_x` and `field_y` column renaming
- Explicit about which version to use

#### 3. **Registry Filtering with Field Variations**
```python
registry_col = None
for col in ["usndr", "REGISTRY", "DATA_SOURCE", "SOURCE"]:
    if col in df.columns:
        registry_col = col
        break

if registry_col == "usndr":
    # Binary flag: null/0 = DataHub, 1 = USNDR
    return df[(df[registry_col].isna()) | (df[registry_col] == 0)]
else:
    # String match
    return df[df[registry_col].str.upper().str.contains("MOVR|DATAHUB", na=False)]
```

**Pattern established:**
- Check for field existence first
- Handle different data types (binary flags vs strings)
- Graceful fallback if field doesn't exist

#### 4. **Temporal Aggregation (Implicit)**
Current implementation joins ALL encounters to demographics:
```python
# Gets all encounters for each participant
merged = encounter_df.merge(
    demographics_df[["FACPATID", disease_col]],
    on="FACPATID",
    how="left"
)
```

**Missing capability:** No way to specify:
- First encounter only
- Last encounter only
- Most recent value per specific field
- Encounter at specific time point

---

## Problem Statement

### Data Structure Characteristics

1. **Baseline Tables** (captured once):
   - `demographics_maindata` - participant baseline info
   - `diagnosis_maindata` - diagnosis, genetic info
   - Joined on: `FACPATID`
   - Cardinality: **One record per participant**

2. **Longitudinal Tables** (captured repeatedly):
   - `encounter_maindata` - clinical visits
   - `log_maindata` - ongoing treatment log
   - Joined on: `FACPATID` + temporal field (e.g., `encntdt`)
   - Cardinality: **Multiple records per participant**

3. **Repeat Group Tables** (nested within encounters):
   - `encounter_medication_rg` - medications per encounter
   - `encounter_hospitalization_rg` - hospitalizations per encounter
   - Joined on: `FACPATID` + `CASE_ID`
   - Cardinality: **Multiple records per encounter**

### Key Challenges

1. **Temporal Selection Problem:**
   - When joining demographics with encounters, which encounter(s) do we use?
   - First visit? Last visit? All visits?
   - Different fields may need different logic

2. **Field-Level Temporal Rules:**
   - `encntdt` (encounter date): Use from selected encounter
   - `height`: Use most recent non-null value
   - `wgt` (weight): Use value from selected encounter
   - `alsfrstl` (ALS score): Use most recent assessment

3. **Disease-Specific Rules:**
   - DMD: Steroid use requires looking at medication repeat groups
   - ALS: ALSFRS-R score changes require temporal comparison
   - SMA: SMN copy number is baseline (diagnosis) not longitudinal

4. **eCRF-Specific Rules:**
   - Pulmonary function tests: Use most recent within 12 months
   - Cardiac assessments: May be in multiple forms (ECG, Echo)
   - Surgeries: Need to know if *ever* occurred vs current status

5. **Configuration Complexity:**
   - 33+ tables total
   - 5+ diseases with different requirements
   - Multiple eCRFs per disease
   - Rules vary by analysis type

---

## Proposed Solution

### Architecture Overview

```
config/
├── config.yaml                           # Core config (as is)
├── field_mappings.yaml                   # Field name resolution (as is)
├── wrangling_rules.yaml                  # Table-level rules (as is)
│
├── cohort_building/                      # NEW: Cohort building configs
│   ├── baseline_fields.yaml              # Which fields come from baseline tables
│   ├── temporal_resolution.yaml          # How to resolve temporal conflicts
│   ├── disease_rules/                    # Disease-specific cohort rules
│   │   ├── dmd.yaml
│   │   ├── als.yaml
│   │   ├── sma.yaml
│   │   ├── lgmd.yaml
│   │   └── ...
│   └── ecrf_rules/                       # eCRF-specific field rules
│       ├── pulmonary_function.yaml
│       ├── cardiac_assessment.yaml
│       ├── medications.yaml
│       └── ...
```

### 1. Baseline Fields Configuration

**File:** `config/cohort_building/baseline_fields.yaml`

```yaml
# Baseline Fields Configuration
# These fields should ALWAYS come from baseline tables (demographics, diagnosis)
# and NEVER be overridden by longitudinal data

baseline_sources:
  # Patient identity and demographics
  patient_identity:
    table: demographics_maindata
    fields:
      - FACPATID
      - guid1
      - dob
      - dob1
      - sex
      - gender
      - ethnic
      - ethnicity
    strategy: demographics_only  # Never merge from other sources

  # Disease and diagnosis
  disease_diagnosis:
    table: diagnosis_maindata
    fields:
      - dstype              # Disease type
      - lgidvar             # LGMD variant
      - lgidvar1            # LGMD variant details
      - lgidvar2
    strategy: diagnosis_only  # If field exists in multiple tables, use diagnosis version

  # Enrollment
  enrollment:
    table: demographics_maindata
    fields:
      - enroldt             # Enrollment date
      - usndr               # Registry flag
    strategy: demographics_only

  # Genetic information
  genetic:
    table: diagnosis_maindata
    fields:
      - dnaconf             # DNA confirmation (if exists)
      # Add other genetic fields
    strategy: diagnosis_only

merge_conflict_resolution:
  # When field exists in both baseline and longitudinal tables
  # Which version should win?
  default: baseline_wins

  exceptions:
    # Some baseline fields may be updated in encounters
    - field: dob
      strategy: baseline_wins
      reason: "Date of birth should never change"

    - field: sex
      strategy: baseline_wins
      reason: "Biological sex is baseline characteristic"
```

### 2. Derived Age Fields Configuration

**File:** `config/cohort_building/derived_age_fields.yaml`

#### Naming Convention for Processed Fields

**MOVR DataHub Field Naming Standards:**
- **IQVIA Product Fields:** `ALL_CAPS` (e.g., `FACPATID`, `CASE_ID`)
- **Original Data Fields:** `lowercase` (e.g., `dstype`, `enroldt`, `dob`)
- **MOVR Processed/Derived Fields:** `CamelCase` (e.g., `Age_At_Enrollment`, `Age_At_Diagnosis`)

This convention makes it immediately clear which fields are:
1. System/product fields (ALL_CAPS)
2. Captured clinical data (lowercase)
3. Calculated/derived by MOVR analytics (CamelCase)

#### Configuration

```yaml
# Derived Age Fields Configuration
# Calculates age at key time points from date of birth and event dates

# Base fields required for age calculations
required_fields:
  date_of_birth: dob          # Primary DOB field
  date_of_birth_alt: dob1     # Alternative DOB field (use if dob is null)

# Naming convention for derived fields
naming_convention:
  pattern: "CamelCase"
  description: "First letter of each word capitalized, separated by underscore"
  examples:
    - Age_At_Enrollment
    - Age_At_Diagnosis
    - Age_At_Visit
    - Current_Age

# Age derivation rules
age_derivations:
  # Critical: Age at enrollment
  Age_At_Enrollment:
    description: "Age in years at study enrollment"
    formula: "years_between(enroldt, dob)"
    source_fields:
      date: enroldt          # Enrollment date
      reference: dob         # Date of birth
    validation:
      min: 0                 # Age cannot be negative
      max: 120               # Sanity check
      warn_if_null: true
    priority: critical
    use_cases:
      - "Eligibility criteria"
      - "Age stratification"
      - "Baseline demographics"

  # Critical: Age at diagnosis
  Age_At_Diagnosis:
    description: "Age in years at disease diagnosis (disease-specific)"
    formula: "years_between(diagnosis_date, dob)"
    source_fields:
      # Diagnosis date varies by disease - see disease_specific_diagnosis_dates
      date: null  # Determined by dstype
      reference: dob
    disease_specific: true
    validation:
      min: 0
      max: 120
      warn_if_null: true
    priority: critical
    use_cases:
      - "Natural history analysis"
      - "Disease progression modeling"

  # High priority: Age at encounter/visit
  Age_At_Visit:
    description: "Age in years at each clinical encounter"
    formula: "years_between(encntdt, dob)"
    source_fields:
      date: encntdt         # Encounter date
      reference: dob
    temporal: true          # Calculated per encounter
    validation:
      min: 0
      max: 120
    priority: high
    use_cases:
      - "Longitudinal analysis"
      - "Age-specific outcomes"

  # Medium priority: Current age
  Current_Age:
    description: "Current age in years (as of analysis date)"
    formula: "years_between(current_date, dob)"
    source_fields:
      date: current_date    # System date at time of analysis
      reference: dob
    validation:
      min: 0
      max: 120
    priority: medium
    use_cases:
      - "Current cohort demographics"
      - "Cross-sectional analysis"

  # Medium priority: Age at symptom onset
  Age_At_Symptom_Onset:
    description: "Age when symptoms first appeared"
    formula: "years_between(symptom_onset_date, dob)"
    source_fields:
      date: null  # Disease-specific - see below
      reference: dob
    disease_specific: true
    validation:
      min: 0
      warn_if_after_diagnosis: true
    priority: medium

# Disease-specific diagnosis and symptom date fields
disease_specific_diagnosis_dates:
  # DMD/BMD
  DMD:
    diagnosis_date_field: null      # Use diagnosis age field instead
    diagnosis_age_field: dmddgnag   # Age at DMD diagnosis (already in years)
    symptom_onset_age_field: dmdonsag  # Age at symptom onset (already in years)
    diagnosis_confirmation: dmddiag  # Yes/No field
    note: "DMD uses age fields directly, not dates"

  BMD:
    diagnosis_date_field: null
    diagnosis_age_field: bmddgnag   # Age at BMD diagnosis
    symptom_onset_age_field: null   # May use dmdonsag if same table
    diagnosis_confirmation: bmddiag
    note: "BMD uses age fields directly"

  # ALS
  ALS:
    diagnosis_date_field: null
    diagnosis_age_field: null       # Check if alsdiagag exists
    symptom_onset_age_field: null
    diagnosis_confirmation: alsdiag
    note: "Need to verify ALS-specific age/date fields"

  # SMA
  SMA:
    diagnosis_date_field: null
    diagnosis_age_field: null       # Check if smadiagag exists
    symptom_onset_age_field: null
    diagnosis_confirmation: smadiag
    note: "Need to verify SMA-specific age/date fields"

  # LGMD
  LGMD:
    diagnosis_date_field: null
    diagnosis_age_field: null       # Check if lgmddiagag exists
    symptom_onset_age_field: null
    diagnosis_confirmation: lgmddiag
    note: "Need to verify LGMD-specific age/date fields"

  # FSHD
  FSHD:
    diagnosis_date_field: null
    diagnosis_age_field: null
    symptom_onset_age_field: null
    diagnosis_confirmation: fshddiag
    note: "Need to verify FSHD-specific age/date fields"

  # Pompe
  Pompe:
    diagnosis_date_field: null
    diagnosis_age_field: null
    symptom_onset_age_field: null
    diagnosis_confirmation: pompediag
    note: "Need to verify Pompe-specific age/date fields"

# Additional date-to-age conversions
additional_age_conversions:
  # Ambulation loss
  Age_At_Ambulation_Loss:
    condition: "amblloss == 'Yes'"
    source_fields:
      date: amblsdt
      reference: dob
    validation:
      min: 0
      warn_if_before_symptom_onset: true

  # First steroid use
  Age_At_First_Steroid:
    source_fields:
      date: null  # Derived from medication repeat groups
      reference: dob
    requires_custom_logic: true
    note: "Must search medication_rg for first steroid occurrence"

  # Ventilation start
  Age_At_Ventilation:
    source_fields:
      date: fstnivdt      # First NIV date (if exists)
      reference: dob
    validation:
      min: 0

  # Tracheostomy
  Age_At_Tracheostomy:
    source_fields:
      date: trachdt
      reference: dob
    validation:
      min: 0

# Validation rules
validation_rules:
  # Rule 1: Age cannot be negative
  negative_age_check:
    description: "Age at any time point must be >= 0"
    severity: error
    action: flag_record
    message: "Negative age calculated: check {date_field} and dob fields"

  # Rule 2: Age at diagnosis should be before current age
  diagnosis_age_check:
    description: "Age at diagnosis should be <= current age"
    severity: warning
    action: flag_record
    message: "Age at diagnosis ({Age_At_Diagnosis}) > current age ({Current_Age})"

  # Rule 3: Age at symptom onset should be before diagnosis
  symptom_onset_check:
    description: "Symptom onset should precede diagnosis"
    severity: warning
    condition: "Age_At_Symptom_Onset > Age_At_Diagnosis"
    action: flag_record
    message: "Symptom onset after diagnosis (check dates)"

  # Rule 4: Enrollment age should be positive
  enrollment_age_check:
    description: "Age at enrollment must be > 0"
    severity: error
    condition: "Age_At_Enrollment < 0"
    action: exclude_record
    message: "Invalid enrollment age (check enroldt and dob)"

  # Rule 5: Age should not exceed biological limits
  max_age_check:
    description: "Age should not exceed 120 years"
    severity: warning
    condition: "any_age_field > 120"
    action: flag_record
    message: "Unrealistic age calculated: check date fields"

  # Rule 6: Missing DOB
  missing_dob_check:
    description: "DOB is required for age calculations"
    severity: error
    condition: "dob is null and dob1 is null"
    action: exclude_record
    message: "Cannot calculate age: DOB missing"

# Calculation implementation
calculation_logic:
  years_between:
    description: "Calculate years between two dates"
    implementation: |
      def years_between(date1, date2):
          """
          Calculate years between two dates.

          Args:
              date1: Later date (event date)
              date2: Earlier date (reference date, usually DOB)

          Returns:
              float: Years between dates (can be fractional)
          """
          if pd.isna(date1) or pd.isna(date2):
              return None

          # Convert to datetime
          dt1 = pd.to_datetime(date1)
          dt2 = pd.to_datetime(date2)

          # Calculate difference in days, convert to years
          days_diff = (dt1 - dt2).days
          years = days_diff / 365.25  # Account for leap years

          return round(years, 2)

  age_from_age_field:
    description: "Use existing age field if available"
    implementation: |
      def get_age_at_diagnosis(row):
          """
          Get age at diagnosis from age field or calculate from dates.

          For diseases like DMD, use dmddgnag (age at diagnosis field).
          Fall back to date calculation if needed.
          """
          disease = row['dstype']

          if disease == 'DMD':
              # Use age field directly
              return row.get('dmddgnag')
          elif disease == 'BMD':
              return row.get('bmddgnag')
          # ... other diseases

          # Fallback: calculate from dates if available
          # return years_between(diagnosis_date, dob)

# Integration with cohort building
cohort_integration:
  when_to_calculate:
    - stage: after_baseline_merge
      fields: [Age_At_Enrollment, Age_At_Diagnosis, Current_Age]

    - stage: after_temporal_resolution
      fields: [Age_At_Visit, Age_At_Symptom_Onset]

    - stage: after_derived_fields
      fields: [Age_At_Ambulation_Loss, Age_At_First_Steroid]

  include_in_output:
    default: true
    configurable: true
    option: include_age_fields

  quality_report:
    generate: true
    include:
      - count_negative_ages
      - count_missing_ages
      - distribution_by_age_group
      - validation_flags

# Example usage in cohort building
example_usage: |
  # In CohortBuilder:
  cohort = builder.create_cohort(
      disease="DMD",
      temporal_strategy="last_encounter",
      derive_age_fields=True,  # Enable age field derivation
      age_fields=[
          "Age_At_Enrollment",
          "Age_At_Diagnosis",
          "Age_At_Visit",
          "Current_Age"
      ]
  )

  # Result includes derived fields:
  # - Age_At_Enrollment (from enroldt)
  # - Age_At_Diagnosis (from dmddgnag for DMD)
  # - Age_At_Visit (from encntdt of selected encounter)
  # - Current_Age (from system date)
```

#### Data Dictionary Integration

Age fields should also be added to the data dictionary for documentation:

**File:** `data/metadata/data_dictionary.parquet` (updated after derivation)

| Field Name | Description | Display Label | Field Type | Source | Formula |
|------------|-------------|---------------|------------|--------|---------|
| Age_At_Enrollment | Age in years at enrollment | Age at Enrollment | Numeric (Derived) | Calculated | `(enroldt - dob) / 365.25` |
| Age_At_Diagnosis | Age in years at diagnosis | Age at Diagnosis | Numeric (Derived) | Calculated | Disease-specific |
| Age_At_Visit | Age in years at encounter | Age at Visit | Numeric (Derived) | Calculated | `(encntdt - dob) / 365.25` |
| Current_Age | Current age in years | Current Age | Numeric (Derived) | Calculated | `(today - dob) / 365.25` |

### 3. Temporal Resolution Configuration

**File:** `config/cohort_building/temporal_resolution.yaml`

```yaml
# Temporal Resolution Rules
# Defines how to handle temporal data when building cohorts

temporal_strategies:
  # Strategy 1: First encounter
  first_encounter:
    description: "Use data from participant's first encounter"
    implementation:
      - group_by: FACPATID
      - sort_by: encntdt
      - select: first
    use_cases:
      - "Baseline clinical characteristics"
      - "Initial presentation analysis"

  # Strategy 2: Last encounter
  last_encounter:
    description: "Use data from participant's most recent encounter"
    implementation:
      - group_by: FACPATID
      - sort_by: encntdt
      - select: last
    use_cases:
      - "Current status"
      - "Most recent assessment"

  # Strategy 3: All encounters
  all_encounters:
    description: "Include all encounters (longitudinal analysis)"
    implementation:
      - group_by: null
      - filter: null
      - select: all
    use_cases:
      - "Trajectory analysis"
      - "Repeated measures"
      - "Time-to-event analysis"

  # Strategy 4: Most recent non-null
  most_recent_non_null:
    description: "Use most recent non-null value for each field"
    implementation:
      - group_by: FACPATID
      - for_each_field:
          - sort_by: encntdt
          - filter: notna
          - select: last
    use_cases:
      - "Height (doesn't change much)"
      - "Genetic test results"
      - "Cumulative max scores"

  # Strategy 5: Specific time point
  specific_timepoint:
    description: "Use encounter closest to specific date"
    implementation:
      - group_by: FACPATID
      - filter: abs(encntdt - target_date) < window
      - sort_by: abs(encntdt - target_date)
      - select: first
    parameters:
      - target_date: date
      - window: timedelta (default: 90 days)
    use_cases:
      - "Study baseline (within 90 days of enrollment)"
      - "Annual follow-up analysis"

  # Strategy 6: Field-specific last value
  field_specific_last:
    description: "Per-field temporal resolution"
    implementation:
      - for_each_field:
          - apply custom strategy
    configuration:
      # Example: Different strategies per field
      height:
        strategy: most_recent_non_null
        reason: "Height stabilizes in adulthood"

      wgt:
        strategy: last_encounter
        reason: "Weight can fluctuate"

      alsfrstl:
        strategy: last_encounter
        reason: "ALS score reflects current status"

      fvc:
        strategy: within_timeframe
        timeframe: 12 months
        reason: "PFTs should be recent"

# Default strategy per analysis type
default_strategies:
  baseline_analysis:
    strategy: first_encounter
    description: "For baseline characteristics studies"

  current_status:
    strategy: last_encounter
    description: "For current status reports"

  longitudinal:
    strategy: all_encounters
    description: "For trajectory analysis"

# Merge strategies when combining tables
merge_strategies:
  demographics_encounter:
    baseline_table: demographics_maindata
    longitudinal_table: encounter_maindata

    # Default: Use last encounter
    default_strategy: last_encounter

    # But some fields have special rules
    field_overrides:
      # Baseline fields always from demographics
      dob:
        source: demographics
        strategy: baseline_only

      sex:
        source: demographics
        strategy: baseline_only

      dstype:
        source: demographics
        strategy: baseline_only

      # Clinical fields from encounter
      height:
        source: encounter
        strategy: most_recent_non_null

      wgt:
        source: encounter
        strategy: last_encounter

      bmi:
        source: encounter
        strategy: calculated  # Calculate from height/weight
        formula: "wgt / (height/100)**2"

  diagnosis_encounter:
    baseline_table: diagnosis_maindata
    longitudinal_table: encounter_maindata

    default_strategy: diagnosis_wins_on_conflict

    field_overrides:
      # Genetic data always from diagnosis
      lgidvar:
        source: diagnosis
        strategy: baseline_only
```

### 3. Disease-Specific Rules

**File:** `config/cohort_building/disease_rules/dmd.yaml`

```yaml
# Disease-Specific Cohort Building Rules: Duchenne Muscular Dystrophy (DMD)

disease: DMD
description: "Cohort building rules specific to Duchenne Muscular Dystrophy"

# Required baseline fields
required_baseline:
  - FACPATID
  - dstype: DMD
  - sex: Male  # DMD primarily affects males
  - dob

# Recommended baseline fields
recommended_baseline:
  - enroldt
  - genetic confirmation fields (if available)

# Temporal resolution for common DMD analyses
temporal_strategies:
  # Steroid use analysis
  steroid_use:
    description: "Determine steroid exposure"
    source_tables:
      - encounter_maindata
      - encounter_medication_rg
      - log_medication_rg

    strategy: custom
    logic:
      # Check if patient is "currently on steroids" (as of last encounter)
      current_use:
        table: encounter_maindata
        temporal_strategy: last_encounter
        fields:
          - glcouse          # Currently on glucocorticoid
          - glcregm          # Glucocorticoid regimen
          - glcdose          # Dose
          - glcdosemg        # Dose in mg

      # Check medication repeat groups for steroid history
      ever_used:
        tables:
          - encounter_medication_rg
          - log_medication_rg
        strategy: any_occurrence
        medication_names:
          - prednisone
          - deflazacort
          - prednisolone
        case_insensitive: true

      # Derive combined variable
      derived_fields:
        - name: steroid_current
          source: encounter_maindata.glcouse
          strategy: last_encounter

        - name: steroid_ever
          source: medication_rg
          strategy: any_match
          condition: "medication_name in steroid_list"

        - name: steroid_start_date
          source: medication_rg
          strategy: first_occurrence
          sort_by: start_date

        - name: steroid_duration_days
          calculation: "last_encounter_date - steroid_start_date"
          unit: days

  # Ambulation loss
  ambulation_status:
    description: "Determine ambulatory status"
    source_tables:
      - encounter_maindata

    fields:
      - amblloss         # Ambulatory function lost
      - amblsdt          # Date lost ambulation

    strategy: field_specific_last
    logic:
      # If ever lost ambulation, use that record
      - check: amblloss == "Yes"
        then: use_first_yes_occurrence
        keep_fields: [amblsdt]

      # Otherwise, use last encounter
      - else: use_last_encounter

  # Cardiac function
  cardiac_assessment:
    description: "Most recent cardiac evaluation"
    source_tables:
      - encounter_maindata

    temporal_strategy: most_recent_non_null
    max_age: 12 months

    fields:
      - ecgbtwvt          # ECG between visits
      - ecgdt             # ECG date
      - ecgrslt           # ECG result
      - echobtwvt         # Echo between visits
      - echodt            # Echo date
      - lftvent           # Left ventricular function
      - efnorpt           # EF normal percent

  # Pulmonary function
  pulmonary_function:
    description: "Most recent PFT results"
    source_tables:
      - encounter_maindata

    temporal_strategy: most_recent_non_null
    max_age: 12 months

    fields:
      - pftest            # PFT performed
      - pfttstdt          # PFT date
      - fvcpctpd          # FVC % predicted
      - fvcrslt           # FVC result
      - fev1rslt          # FEV1 result

# Common DMD cohort definitions
cohort_templates:
  ambulatory:
    description: "Ambulatory DMD participants"
    filters:
      - dstype: DMD
      - amblloss: [null, "No"]  # Never lost or hasn't lost

    temporal_strategy: last_encounter

    required_fields:
      - FACPATID
      - dstype
      - sex
      - age
      - amblloss

  steroid_treated:
    description: "DMD participants ever on steroids"
    filters:
      - dstype: DMD
      - steroid_ever: true

    temporal_strategy: all_encounters

    derived_fields:
      - steroid_ever
      - steroid_current
      - steroid_duration_days

  pediatric_ambulatory:
    description: "Pediatric ambulatory DMD"
    filters:
      - dstype: DMD
      - age: [4, 18]
      - amblloss: [null, "No"]
      - sex: Male

    temporal_strategy: last_encounter

# Field importance ranking for DMD
field_priority:
  critical:
    - FACPATID
    - dstype
    - dob
    - sex

  high_importance:
    - enroldt
    - amblloss
    - amblsdt
    - glcouse
    - steroid fields

  medium_importance:
    - cardiac fields
    - pulmonary fields
    - height
    - wgt

  low_importance:
    - contact information
    - administrative fields
```

### 4. eCRF-Specific Rules

**File:** `config/cohort_building/ecrf_rules/pulmonary_function.yaml`

```yaml
# eCRF-Specific Rules: Pulmonary Function Tests

ecrf_name: pulmonary_function
description: "Rules for handling pulmonary function test data across tables"

# Where this data lives
data_sources:
  primary:
    table: encounter_maindata
    fields:
      - pftest            # Was PFT performed?
      - pfttstdt          # PFT test date
      - pftfvc            # FVC measurement
      - fvcrslt           # FVC result
      - fvcpctpd          # FVC % predicted
      - pftfev1           # FEV1 measurement
      - fev1rslt          # FEV1 result
      - supfvc            # Supine FVC
      - supfpd            # Supine FVC % predicted
      - pftmep            # MEP
      - meprslt           # MEP result
      - pftmip            # MIP
      - miprslt           # MIP result

  # May also exist in disease-specific supplements
  secondary:
    table: encounter_maindata
    condition: "disease in ['ALS', 'SMA']"
    additional_fields:
      - pftsnip           # SNIP test
      - sniprslt          # SNIP result

# Temporal resolution strategy
temporal_strategy: most_recent_valid
validation:
  # PFT must be recent
  max_age: 12 months

  # Must have test date
  required_fields:
    - pfttstdt

  # At least one measurement
  require_any_of:
    - fvcrslt
    - fev1rslt
    - supfvc

# How to combine with other tables
merge_rules:
  with_demographics:
    join_on: FACPATID
    strategy: most_recent_non_null

    # Calculate age at PFT
    derived_fields:
      - name: age_at_pft
        formula: "pfttstdt - dob"
        unit: years

  with_encounters:
    join_on: [FACPATID, CASE_ID]
    strategy: encounter_specific

    # Keep PFT from that specific encounter
    note: "PFT is tied to specific encounter"

# Quality flags
quality_checks:
  # Flag if PFT is too old
  - name: pft_outdated
    condition: "(current_date - pfttstdt) > 365 days"
    severity: warning

  # Flag if missing key measurements
  - name: incomplete_pft
    condition: "fvcrslt.isna() and fev1rslt.isna()"
    severity: error

  # Flag unlikely values
  - name: unlikely_fvc
    condition: "fvcpctpd < 10 or fvcpctpd > 200"
    severity: warning

# Disease-specific interpretation
disease_specific:
  DMD:
    primary_measure: fvcpctpd
    clinical_threshold: 50
    interpretation: "FVC <50% indicates significant respiratory compromise"

  ALS:
    primary_measure: fvcpctpd
    secondary_measure: supfpd
    clinical_threshold: 50
    interpretation: "FVC <50% or supine FVC <50% indicates respiratory failure risk"

  SMA:
    primary_measure: fvcpctpd
    clinical_threshold: 40
    interpretation: "FVC <40% indicates need for respiratory support"
```

### 5. Cohort Builder API

**File:** `src/movr/cohorts/builder.py`

```python
from typing import Optional, List, Dict, Union
from pathlib import Path
import pandas as pd
import yaml

class CohortBuilder:
    """
    Build cohorts using configurable temporal and disease-specific rules.
    """

    def __init__(self, config_dir: Path = Path("config/cohort_building")):
        """Initialize with cohort building configuration."""
        self.config_dir = config_dir
        self.baseline_config = self._load_config("baseline_fields.yaml")
        self.temporal_config = self._load_config("temporal_resolution.yaml")
        self.disease_rules = {}
        self.ecrf_rules = {}

    def load_disease_rules(self, disease: str):
        """Load disease-specific rules."""
        path = self.config_dir / "disease_rules" / f"{disease.lower()}.yaml"
        self.disease_rules[disease] = self._load_config(path)

    def create_cohort(
        self,
        base_table: str = "demographics",
        temporal_strategy: str = "last_encounter",
        disease: Optional[str] = None,
        filters: Optional[Dict] = None,
        include_fields: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Create a cohort DataFrame.

        Args:
            base_table: Baseline table to start from
            temporal_strategy: How to handle temporal data
            disease: Apply disease-specific rules
            filters: Additional filters
            include_fields: Specific fields to include

        Returns:
            Cohort DataFrame with resolved temporal conflicts
        """
        # 1. Load baseline data
        baseline_df = self._load_baseline(base_table)

        # 2. Apply disease-specific baseline requirements
        if disease:
            self.load_disease_rules(disease)
            baseline_df = self._apply_disease_baseline_rules(baseline_df, disease)

        # 3. Join with longitudinal data (if needed)
        if temporal_strategy != "baseline_only":
            cohort_df = self._join_longitudinal(
                baseline_df,
                strategy=temporal_strategy,
                disease=disease
            )
        else:
            cohort_df = baseline_df

        # 4. Apply filters
        if filters:
            cohort_df = self._apply_filters(cohort_df, filters)

        # 5. Select fields
        if include_fields:
            cohort_df = self._select_fields(cohort_df, include_fields)

        # 6. Calculate derived fields (if disease-specific)
        if disease:
            cohort_df = self._calculate_derived_fields(cohort_df, disease)

        return cohort_df

    def _join_longitudinal(
        self,
        baseline_df: pd.DataFrame,
        strategy: str,
        disease: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Join baseline with longitudinal data using specified strategy.

        Implements:
        - first_encounter
        - last_encounter
        - all_encounters
        - most_recent_non_null
        - field_specific_last
        """
        # Load encounter data
        encounter_df = self._load_encounter_data()

        # Handle duplicate columns (keep baseline version)
        baseline_fields = self._get_baseline_field_list()
        duplicate_cols = [col for col in encounter_df.columns
                         if col in baseline_df.columns and col != "FACPATID"]

        if duplicate_cols:
            encounter_df = encounter_df.drop(columns=duplicate_cols)

        # Apply temporal strategy
        if strategy == "first_encounter":
            encounter_df = self._select_first_encounter(encounter_df)
        elif strategy == "last_encounter":
            encounter_df = self._select_last_encounter(encounter_df)
        elif strategy == "most_recent_non_null":
            encounter_df = self._select_most_recent_non_null(encounter_df)
        elif strategy == "field_specific_last":
            encounter_df = self._apply_field_specific_strategies(encounter_df, disease)
        # elif strategy == "all_encounters": keep all

        # Merge
        merged_df = baseline_df.merge(encounter_df, on="FACPATID", how="left")

        return merged_df

    def _select_last_encounter(self, df: pd.DataFrame) -> pd.DataFrame:
        """Select most recent encounter per participant."""
        # Sort by encounter date
        df = df.sort_values("encntdt", ascending=False)

        # Keep first (most recent) per participant
        return df.groupby("FACPATID").first().reset_index()

    def _select_first_encounter(self, df: pd.DataFrame) -> pd.DataFrame:
        """Select earliest encounter per participant."""
        df = df.sort_values("encntdt", ascending=True)
        return df.groupby("FACPATID").first().reset_index()

    def _select_most_recent_non_null(self, df: pd.DataFrame) -> pd.DataFrame:
        """For each field, use most recent non-null value."""
        # Group by participant
        result_df = pd.DataFrame()

        for facpatid, group in df.groupby("FACPATID"):
            # Sort by date
            group = group.sort_values("encntdt", ascending=False)

            # For each column, take first non-null
            row = {}
            row["FACPATID"] = facpatid

            for col in group.columns:
                if col == "FACPATID":
                    continue

                # Get first non-null value
                non_null_values = group[col].dropna()
                if len(non_null_values) > 0:
                    row[col] = non_null_values.iloc[0]
                else:
                    row[col] = None

            result_df = pd.concat([result_df, pd.DataFrame([row])], ignore_index=True)

        return result_df
```

---

## Implementation Plan

### Phase 1: Foundation (Weeks 1-2)
1. Create config directory structure
2. Implement `baseline_fields.yaml` configuration
3. Implement `temporal_resolution.yaml` configuration
4. Update `CohortBuilder` class with basic temporal strategies

### Phase 2: Disease-Specific Rules (Weeks 3-4)
1. Implement DMD rules (`dmd.yaml`)
2. Implement ALS rules (`als.yaml`)
3. Implement SMA rules (`sma.yaml`)
4. Test with real data

### Phase 3: eCRF Rules (Weeks 5-6)
1. Implement pulmonary function rules
2. Implement cardiac assessment rules
3. Implement medication rules
4. Test cross-table joins

### Phase 4: Advanced Features (Weeks 7-8)
1. Field-specific temporal resolution
2. Derived field calculations
3. Quality checks and validation
4. Documentation and examples

---

## Testing Strategy

### Unit Tests
```python
def test_baseline_field_resolution():
    """Test that baseline fields always come from baseline tables."""
    cohort = builder.create_cohort(
        temporal_strategy="last_encounter",
        disease="DMD"
    )

    # dstype should come from demographics, not encounter
    assert cohort["dstype"].source == "demographics"

def test_last_encounter_strategy():
    """Test last encounter temporal strategy."""
    cohort = builder.create_cohort(
        temporal_strategy="last_encounter"
    )

    # Should have one row per participant
    assert cohort["FACPATID"].nunique() == len(cohort)

def test_disease_specific_derived_fields():
    """Test DMD steroid exposure calculation."""
    cohort = builder.create_cohort(
        disease="DMD",
        temporal_strategy="all_encounters"
    )

    # Should have derived steroid fields
    assert "steroid_ever" in cohort.columns
    assert "steroid_current" in cohort.columns
```

### Integration Tests
```python
def test_dmd_ambulatory_cohort():
    """Test building DMD ambulatory cohort."""
    cohort = builder.create_cohort_from_template(
        disease="DMD",
        template="ambulatory"
    )

    # All should be DMD
    assert (cohort["dstype"] == "DMD").all()

    # None should have lost ambulation
    assert (cohort["amblloss"].isna() | (cohort["amblloss"] == "No")).all()
```

---

## Open Questions

1. **Performance:**
   - How to optimize for large datasets (10K+ participants, 100K+ encounters)?
   - Should we cache intermediate results?
   - Lazy evaluation vs eager?

2. **Versioning:**
   - How to version cohort definitions?
   - How to ensure reproducibility across rule changes?

3. **Validation:**
   - How to validate that rules are being applied correctly?
   - Automated rule conflict detection?

4. **UI/UX:**
   - CLI interface for cohort building?
   - Interactive cohort builder (future web UI)?

---

## Related Work

- **Current Implementation:** `src/movr/cli/commands/summary.py`
- **Field Mappings:** `config/field_mappings.yaml`
- **Wrangling Rules:** `config/wrangling_rules.yaml`
- **Existing Cohorts:** `src/movr/cohorts/manager.py`

---

## Success Criteria

1. ✅ Can build baseline cohorts (demographics only)
2. ✅ Can join baseline + most recent encounter
3. ✅ Can apply disease-specific rules (DMD, ALS, SMA)
4. ✅ Can handle field-level temporal resolution
5. ✅ Can calculate derived fields (steroid exposure, ambulation status)
6. ✅ Configuration is readable and maintainable
7. ✅ Performance is acceptable (<5 seconds for 10K participants)
8. ✅ Results are reproducible and auditable

---

## References

- Existing patterns in `summary.py` lines 53-272
- Field mappings: `config/field_mappings.yaml`
- MOVR data dictionary
- Clinical domain knowledge (steroid use, ambulation, PFTs)

---

**Next Steps:**
1. Review and approve this proposal
2. Prioritize disease rules (DMD first?)
3. Begin Phase 1 implementation
4. Schedule design review for temporal resolution logic
