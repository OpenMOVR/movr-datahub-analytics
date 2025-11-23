# Data Wrangling Rules Tracker

**Status tracking for all data cleaning, transformation, and validation rules**

> This document tracks the implementation status of data wrangling rules. For detailed rule specifications, see [DATA_WRANGLING_RULES.md](DATA_WRANGLING_RULES.md).

---

## Status Definitions

| Status | Description |
|--------|-------------|
| ✅ **Implemented** | Rule is coded and tested in the system |
| 🚧 **In Progress** | Currently being implemented |
| 📋 **Proposed** | Documented proposal, awaiting approval/implementation |
| 💭 **Speculative** | Idea or possibility, not yet formally proposed |
| ⚠️ **Needed** | Identified need, requires design/specification |
| 🔴 **Blocked** | Cannot proceed due to dependency or issue |

---

## Rule Categories

1. [Record Uniqueness & Deduplication](#1-record-uniqueness--deduplication)
2. [Data Type Standardization](#2-data-type-standardization)
3. [Missing Value Handling](#3-missing-value-handling)
4. [Date & Temporal Logic](#4-date--temporal-logic)
5. [Referential Integrity](#5-referential-integrity)
6. [Value Normalization](#6-value-normalization)
7. [Domain-Specific Business Rules](#7-domain-specific-business-rules)
8. [Advanced Analytics Preparation](#8-advanced-analytics-preparation)

---

## 1. Record Uniqueness & Deduplication

| Rule ID | Rule Name | Status | Priority | Notes |
|---------|-----------|--------|----------|-------|
| RU-001 | Demographics table uniqueness (FACPATID) | ✅ Implemented | High | Core rule documented |
| RU-002 | Encounter deduplication (FACPATID + CASE_ID + FORM_NAME) | ✅ Implemented | High | Post-2019 data only |
| RU-003 | Diagnosis table uniqueness (FACPATID + DX_DATE + DX_CODE) | ✅ Implemented | High | Documented |
| RU-004 | Log table uniqueness (FACPATID + LOG_DATE + EVENT_TYPE) | ✅ Implemented | Medium | Documented |
| RU-005 | Encounter pre-2019 deduplication strategy | 💭 Speculative | Medium | Missing FORM_NAME in old data |
| RU-006 | Cross-file duplicate detection | 📋 Proposed | Low | Detect same patient across multiple Excel files |

---

## 2. Data Type Standardization

| Rule ID | Rule Name | Status | Priority | Notes |
|---------|-----------|--------|----------|-------|
| DT-001 | FACPATID as string (preserve leading zeros) | ✅ Implemented | High | Documented |
| DT-002 | CASE_ID as string | ✅ Implemented | High | Documented |
| DT-003 | Date parsing (multiple formats) | ✅ Implemented | High | Supports %Y-%m-%d, %m/%d/%Y, %d/%m/%Y |
| DT-004 | Numeric field validation | ✅ Implemented | Medium | Age, BMI, lab values |
| DT-005 | Boolean field standardization | 📋 Proposed | Low | Yes/No/True/False → boolean |
| DT-006 | Categorical field validation | 📋 Proposed | Medium | Validate against data dictionary |
| DT-007 | Phone number standardization | 💭 Speculative | Low | If PHI included |
| DT-008 | ZIP code format validation | 💭 Speculative | Low | If geographic analysis needed |

---

## 3. Missing Value Handling

| Rule ID | Rule Name | Status | Priority | Notes |
|---------|-----------|--------|----------|-------|
| MV-001 | NA value standardization | ✅ Implemented | High | "", "NA", "N/A", "NULL", "Unknown" → NaN |
| MV-002 | Required field validation (Demographics) | ✅ Implemented | High | FACPATID, BIRTH_DATE, SEX |
| MV-003 | Required field validation (Encounter) | ✅ Implemented | High | FACPATID, CASE_ID, ENCOUNTER_DATE |
| MV-004 | Optional field flagging | 📋 Proposed | Low | Flag records with high missing data |
| MV-005 | Imputation rules for continuous variables | 💭 Speculative | Low | Mean/median imputation strategies |
| MV-006 | Missing data pattern analysis | 📋 Proposed | Medium | Identify systematic missingness |

---

## 4. Date & Temporal Logic

| Rule ID | Rule Name | Status | Priority | Notes |
|---------|-----------|--------|----------|-------|
| DT-001 | Future date validation | ✅ Implemented | High | Dates should not be in the future |
| DT-002 | Age calculation from BIRTH_DATE | ✅ Implemented | High | As of encounter or current date |
| DT-003 | Date ordering validation | ✅ Implemented | Medium | Birth < Encounter < Death |
| DT-004 | Age range validation | ✅ Implemented | Medium | 0-120 years |
| DT-005 | Encounter date sequence validation | 📋 Proposed | Medium | Ensure chronological order per patient |
| DT-006 | Date of death consistency | 📋 Proposed | High | No encounters after death date |
| DT-007 | Age at diagnosis calculation | 💭 Speculative | Low | For specific analyses |
| DT-008 | Treatment duration calculation | 💭 Speculative | Low | Start date - end date |
| DT-009 | Follow-up time calculation | 📋 Proposed | Medium | First encounter to last encounter |
| DT-010 | Time since diagnosis | 💭 Speculative | Low | For longitudinal analyses |

---

## 5. Referential Integrity

| Rule ID | Rule Name | Status | Priority | Notes |
|---------|-----------|--------|----------|-------|
| RI-001 | FACPATID exists in Demographics | ✅ Implemented | High | All encounter/diagnosis FACPATIDs must exist |
| RI-002 | Orphaned record detection | ✅ Implemented | High | Flag records without parent |
| RI-003 | CASE_ID uniqueness within patient | 📋 Proposed | Medium | Validate CASE_ID per FACPATID |
| RI-004 | Diagnosis code validation | 💭 Speculative | Low | Check against ICD-10 codes |
| RI-005 | Medication code validation | 💭 Speculative | Low | Check against formulary |
| RI-006 | Provider ID validation | 💭 Speculative | Low | If provider data available |

---

## 6. Value Normalization

| Rule ID | Rule Name | Status | Priority | Notes |
|---------|-----------|--------|----------|-------|
| VN-001 | Text field trimming | ✅ Implemented | High | Remove leading/trailing whitespace |
| VN-002 | Uppercase disease codes | ✅ Implemented | Medium | DMD, SMA, LGMD standardization |
| VN-003 | Sex/gender standardization | ✅ Implemented | High | M/F/Male/Female → M/F |
| VN-004 | Range validation (Age, BMI, etc.) | ✅ Implemented | Medium | Documented ranges |
| VN-005 | Drug name standardization | 📋 Proposed | High | Map common names to generic |
| VN-006 | Diagnosis description normalization | 💭 Speculative | Low | Standardize free-text diagnoses |
| VN-007 | Unit conversion and standardization | 📋 Proposed | Medium | Convert all measurements to standard units |
| VN-008 | Race/ethnicity standardization | ⚠️ Needed | Medium | Follow NIH guidelines |
| VN-009 | State/country code standardization | 💭 Speculative | Low | Two-letter codes |

---

## 7. Domain-Specific Business Rules

| Rule ID | Rule Name | Status | Priority | Notes |
|---------|-----------|--------|----------|-------|
| BR-001 | Enrollment validation (3 required forms) | ✅ Implemented | High | Demographics, Encounter, Diagnosis |
| BR-002 | DMD diagnosis age range validation | 📋 Proposed | Medium | Typically diagnosed <5 years |
| BR-003 | SMA subtype consistency | 📋 Proposed | Medium | Validate subtype matches age/severity |
| BR-004 | Steroid therapy tracking | 💭 Speculative | Low | Identify prednisone/deflazacort usage |
| BR-005 | Ventilation status validation | 💭 Speculative | Low | Check for conflicting ventilation data |
| BR-006 | Ambulatory status consistency | 📋 Proposed | Medium | Validate timeline of ambulatory loss |
| BR-007 | Treatment eligibility rules | 💭 Speculative | Low | Gene therapy eligibility criteria |
| BR-008 | Disease progression milestones | 💭 Speculative | Low | Track loss of ambulation, etc. |

---

## 8. Advanced Analytics Preparation

| Rule ID | Rule Name | Status | Priority | Notes |
|---------|-----------|--------|----------|-------|
| AA-001 | Feature engineering framework | 📋 Proposed | Low | Create derived variables |
| AA-002 | Time-to-event data structuring | 💭 Speculative | Low | For survival analysis |
| AA-003 | Longitudinal data reshaping | 📋 Proposed | Medium | Wide to long format conversion |
| AA-004 | Cohort stratification variables | 💭 Speculative | Low | Age groups, disease severity |
| AA-005 | Missing data imputation strategies | 💭 Speculative | Low | Multiple imputation methods |
| AA-006 | Outlier detection and handling | 📋 Proposed | Medium | Statistical methods for outliers |
| AA-007 | Data aggregation rules | 💭 Speculative | Low | Patient-level summaries |
| AA-008 | Normalization for ML models | 💭 Speculative | Low | Scaling, encoding strategies |

---

## Priority Levels

- **High**: Core functionality, data integrity critical
- **Medium**: Important for analysis quality, not blocking
- **Low**: Nice-to-have, optimization, edge cases

---

## Recently Updated Rules

| Date | Rule ID | Change | Updated By |
|------|---------|--------|------------|
| 2025-11-20 | RU-002 | Added post-2019 FORM_NAME requirement | Andre Daniel Paredes |
| 2025-11-20 | DT-003 | Clarified date format support | Andre Daniel Paredes |
| 2025-11-20 | BR-001 | Documented enrollment validation | Andre Daniel Paredes |

---

## Rules Needing Design

The following rules are marked as **Needed** and require design/specification:

1. **VN-008**: Race/ethnicity standardization - Needs alignment with NIH guidelines
2. Add more as identified...

---

## Blocked Rules

The following rules are **Blocked** and cannot proceed:

| Rule ID | Rule Name | Blocker | Resolution |
|---------|-----------|---------|------------|
| (None currently blocked) | | | |

---

## How to Use This Tracker

1. **Finding Rules**: Use the category sections or search by Rule ID
2. **Proposing New Rules**: Create a proposal (see [CONTRIBUTING.md](CONTRIBUTING.md)) and add as "Proposed"
3. **Updating Status**: When implementing, change status and add notes
4. **Raising Issues**: Link GitHub issues to specific Rule IDs

---

## Related Documentation

- [DATA_WRANGLING_RULES.md](DATA_WRANGLING_RULES.md) - Full rule specifications
- [FEATURES.md](FEATURES.md) - Feature implementation tracker
- [CONTRIBUTING.md](CONTRIBUTING.md) - How to propose new rules
- [proposals/](proposals/) - Detailed rule proposals (RFC-style)

---

**Last Updated**: 2025-11-20
**Created By**: Andre Daniel Paredes
**Maintained By**: Andre Daniel Paredes
