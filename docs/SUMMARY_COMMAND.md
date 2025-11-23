# Summary Command Architecture

**Quick access to key registry statistics**

The `movr summary` command provides instant access to commonly-needed summary statistics without writing code.

---

## Usage

```bash
# Show all metrics for MOVR DataHub (default)
movr summary

# Show specific metric
movr summary --metric enrollment
movr summary --metric recruitment
movr summary --metric encounters
movr summary --metric rates

# Show for different registry
movr summary --registry usndr
movr summary --registry all

# Combine options
movr summary --registry datahub --metric enrollment
```

---

## Available Options

### Registry Selection

| Flag | Description |
|------|-------------|
| `--registry datahub` | MOVR DataHub only (default) |
| `--registry usndr` | USNDR only |
| `--registry all` | All registries combined |

### Metric Selection

| Flag | Metrics Shown |
|------|---------------|
| `--metric enrollment` | Participants enrolled by disease |
| `--metric recruitment` | Annual recruitment by disease |
| `--metric encounters` | Total encounters, by year, by disease/year |
| `--metric rates` | Avg encounters per participant by disease (overall and per year) |
| `--metric all` | All metrics (default) |

---

## Output Sections

### 1. Enrollment by Disease

Shows total unique participants enrolled by disease.

**Example Output:**
```
Enrollment by Disease
┌─────────────┬──────────────┐
│ Disease     │ Participants │
├─────────────┼──────────────┤
│ DMD         │        1,234 │
│ SMA         │          567 │
│ LGMD        │          890 │
│             │              │
│ TOTAL       │        2,691 │
└─────────────┴──────────────┘
```

### 2. Annual Recruitment by Disease

Shows new participant enrollments per year by disease.

**Example Output:**
```
Annual Recruitment by Disease
┌─────────────┬──────┬──────┬──────┐
│ Disease     │ 2022 │ 2023 │ 2024 │
├─────────────┼──────┼──────┼──────┤
│ DMD         │  400 │  450 │  384 │
│ SMA         │  180 │  200 │  187 │
│ LGMD        │  290 │  320 │  280 │
└─────────────┴──────┴──────┴──────┘
```

### 3. Encounter Summary

Shows total encounters overall and by year, then by disease and year.

**Example Output:**
```
Encounter Summary
Total Encounters: 15,432

Encounters by Year:
┌──────┬────────────┐
│ Year │ Encounters │
├──────┼────────────┤
│ 2022 │      4,500 │
│ 2023 │      5,200 │
│ 2024 │      5,732 │
└──────┴────────────┘

Encounters by Disease and Year:
┌─────────────┬──────┬──────┬──────┐
│ Disease     │ 2022 │ 2023 │ 2024 │
├─────────────┼──────┼──────┼──────┤
│ DMD         │ 2,000│ 2,300│ 2,500│
│ SMA         │ 1,200│ 1,400│ 1,532│
│ LGMD        │ 1,300│ 1,500│ 1,700│
└─────────────┴──────┴──────┴──────┘
```

### 4. Average Encounters per Participant

Shows average number of encounters per participant by disease, both overall and per year.

**Example Output:**
```
Average Encounters per Participant by Disease
┌─────────────┬──────────────────────────────┐
│ Disease     │ Avg Encounters/Participant   │
├─────────────┼──────────────────────────────┤
│ DMD         │                         4.52 │
│ SMA         │                         3.81 │
│ LGMD        │                         4.12 │
└─────────────┴──────────────────────────────┘

Average Encounters per Participant by Disease and Year:
┌─────────────┬──────┬──────┬──────┐
│ Disease     │ 2022 │ 2023 │ 2024 │
├─────────────┼──────┼──────┼──────┤
│ DMD         │ 1.45 │ 1.52 │ 1.55 │
│ SMA         │ 1.20 │ 1.28 │ 1.33 │
│ LGMD        │ 1.35 │ 1.40 │ 1.37 │
└─────────────┴──────┴──────┴──────┘
```

---

## Architecture

### Design Decisions

1. **CLI-based**: Quick terminal access without opening Python/Jupyter
2. **Static metrics**: Common statistics that are frequently needed
3. **Registry filtering**: Support for multi-registry environments
4. **Flexible output**: Choose all metrics or specific ones

### Data Requirements

**Required tables:**
- `demographics_maindata`: For participant enrollment and disease info
- `encounter_maindata`: For encounter counts and dates

**Optional columns:**
- `REGISTRY`: For multi-registry filtering (defaults to all data if missing)
- `ENROLLMENT_DATE`: For recruitment analysis (tries alternatives)
- `ENCOUNTER_DATE`: For temporal analysis (tries alternatives)

### Alternative Column Names

The command automatically tries alternative column names:

| Standard | Alternatives |
|----------|-------------|
| `ENROLLMENT_DATE` | `ENROLL_DATE`, `CONSENT_DATE`, `FIRST_VISIT_DATE` |
| `ENCOUNTER_DATE` | `VISIT_DATE`, `CASE_DATE`, `DATE` |

---

## Implementation Details

### Class: `SummaryReporter`

**Location**: `src/movr/cli/commands/summary.py`

**Key Methods:**
- `load_data()`: Load demographics and encounter tables
- `filter_by_registry()`: Apply registry filter
- `get_enrollment_by_disease()`: Count unique participants per disease
- `get_annual_recruitment()`: Count new enrollments per year per disease
- `get_encounter_summary()`: Count total encounters overall and by year
- `get_encounters_by_disease_year()`: Count encounters by disease and year
- `get_avg_encounters_per_participant_disease()`: Calculate average encounters per participant by disease
- `get_avg_encounters_per_participant_disease_year()`: Calculate average by disease and year

### Error Handling

- Gracefully handles missing columns (tries alternatives)
- Shows warning if data not available
- Suggests running `movr convert` if tables missing

---

## Common Use Cases

### 1. Quick Overview Before Meeting

```bash
movr summary
```

Get all key metrics in one shot for presentations or discussions.

### 2. Check Specific Metric

```bash
movr summary --metric enrollment
```

Quick check of current enrollment numbers by disease.

### 3. Annual Report Data

```bash
movr summary --metric recruitment
```

Get yearly recruitment trends for annual reports.

### 4. Monitor Data Collection

```bash
movr summary --metric encounters
```

Check encounter collection patterns and completeness.

### 5. Multi-Registry Comparison

```bash
movr summary --registry datahub > datahub_summary.txt
movr summary --registry usndr > usndr_summary.txt
```

Generate separate summaries for comparison.

---

## Future Enhancements

Potential additions (not yet implemented):

- **Export formats**: `--output json`, `--output csv`, `--output excel`
- **Date ranges**: `--start-date`, `--end-date`
- **Site-level stats**: Breakdown by site/center
- **Longitudinal metrics**: Follow-up time, retention rates
- **Comparison mode**: Compare two time periods
- **Visualization**: `--plot` flag to generate charts

---

## Related Commands

- `movr validate`: Data quality checks
- `movr status`: Configuration and file status
- `movr convert`: Excel to Parquet conversion

---

## Examples

### Example 1: Daily Check

```bash
# Quick morning check
movr summary --metric enrollment

# Output shows current enrollment counts
```

### Example 2: Monthly Report

```bash
# Generate full summary for monthly report
movr summary > monthly_summary_2024_11.txt

# Email or share the text file
```

### Example 3: Targeted Analysis

```bash
# Just check encounter patterns
movr summary --metric encounters

# Just check recruitment trends
movr summary --metric recruitment
```

---

**Last Updated**: 2025-11-20
**Created By**: Andre Daniel Paredes
**Maintained By**: Andre Daniel Paredes
