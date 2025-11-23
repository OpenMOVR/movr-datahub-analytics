# Architecture Plan

**MOVR DataHub Analytics - System Architecture**

**Last Updated:** 2025-11-20
**Author:** Andre Daniel Paredes

---

## Overview

MOVR DataHub Analytics is a Python-based clinical data analytics framework designed for neuromuscular disease registry data. This document describes the system architecture, design decisions, and technical implementation details.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           CLI Interface                              │
│                    (movr setup | convert | summary)                 │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Configuration Layer                           │
│              (config.yaml | field_mappings.yaml | *.yaml)           │
└─────────────────────────────────────────────────────────────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Layer    │    │ Wrangling Layer │    │ Analytics Layer │
│   (load_data)   │    │ (WranglingRules)│    │ (CohortManager) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
          │                        │                        │
          ▼                        ▼                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Storage Layer                                 │
│              (Parquet files | Audit logs | Metadata)                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. CLI Interface (`src/movr/cli/`)

**Purpose:** User-facing command-line interface for all operations.

**Commands:**
- `movr setup` - Interactive configuration wizard
- `movr convert` - Excel to Parquet conversion
- `movr validate` - Data quality validation
- `movr summary` - Summary statistics
- `movr dictionary` - Data dictionary exploration
- `movr status` - System health check

**Design Principles:**
- Rich terminal output for readability
- Graceful error handling with helpful messages
- Progress indicators for long operations

### 2. Configuration Layer (`config/`)

**Purpose:** Centralized, YAML-based configuration for all settings.

**Key Files:**
- `config.yaml` - Main configuration (data sources, paths, options)
- `field_mappings.yaml` - Field name resolution (actual → fallback names)
- `wrangling_rules.yaml` - Data transformation rules

**Design Principles:**
- Configuration over code
- Sensible defaults with override capability
- Environment-aware (dev, prod, test)

### 3. Data Layer (`src/movr/data/`)

**Purpose:** Data loading, format conversion, and persistence.

**Key Capabilities:**
- Excel → Parquet conversion with audit logging
- Multi-sheet workbook handling
- Repeat group detection and flattening
- Metadata extraction and storage

**Design Principles:**
- Source files are read-only
- Parquet for efficient storage and querying
- Full audit trail for reproducibility

### 4. Wrangling Layer (`src/movr/wrangling/`)

**Purpose:** Data cleaning, transformation, and standardization.

**Key Patterns:**
- Field name resolution (see `docs/DATA_WRANGLING_PATTERNS.md`)
- Duplicate column handling in merges
- Registry filtering with type handling
- Date parsing with error handling

**Design Principles:**
- Rule-based transformations
- Plugin architecture for custom logic
- Configurable strictness levels

### 5. Cohort Layer (`src/movr/cohorts/`)

**Purpose:** Participant filtering and cohort management.

**Key Capabilities:**
- Base cohort creation (all enrolled participants)
- Filter-based cohort derivation
- Cohort persistence and reuse

**Planned Enhancements (Proposal 001):**
- Temporal resolution strategies
- Disease-specific rules
- eCRF-specific rules
- Derived field calculations

### 6. Analytics Layer (`src/movr/analytics/`)

**Purpose:** Statistical analysis and reporting.

**Key Capabilities:**
- Descriptive statistics
- Summary tables with pivot support
- Export to Excel/CSV

---

## Data Flow

### Excel → Analysis Pipeline

```
1. Excel Files (source-movr-data/)
   │
   ├── movr convert
   │   ├── Read Excel sheets
   │   ├── Detect repeat groups
   │   ├── Convert to Parquet
   │   └── Write audit log
   │
   ▼
2. Parquet Files (data/parquet/)
   │
   ├── movr validate
   │   ├── Apply validation rules
   │   ├── Check referential integrity
   │   └── Generate quality report
   │
   ▼
3. Validated Data
   │
   ├── load_data()
   │   ├── Load Parquet files
   │   ├── Apply field mappings
   │   └── Return DataFrame dict
   │
   ▼
4. Analysis
   │
   ├── CohortManager
   │   ├── Create base cohort
   │   ├── Apply filters
   │   └── Return cohort DataFrame
   │
   ├── DescriptiveAnalyzer
   │   ├── Calculate statistics
   │   ├── Generate tables
   │   └── Export results
   │
   ▼
5. Output (output/)
```

---

## Design Decisions

### 1. Why Parquet Over Excel?

| Aspect | Excel | Parquet |
|--------|-------|---------|
| Read Speed | Slow (seconds) | Fast (milliseconds) |
| File Size | Large | Compressed (5-10x smaller) |
| Column Types | Guessed | Preserved |
| Partial Reads | No | Yes (column pruning) |
| Concurrent Access | Limited | Supported |

### 2. Why YAML Configuration?

- **Human-readable:** Non-programmers can modify
- **Version-controlled:** Changes tracked in git
- **Validated:** Schema validation for correctness
- **Hierarchical:** Supports complex nested structures

### 3. Why Plugin Architecture?

- **Extensibility:** Custom transformations without core changes
- **Isolation:** Plugins can be tested independently
- **Flexibility:** Site-specific rules stay separate

---

## Directory Structure

```
movr-datahub-analytics/
├── src/movr/                   # Main package
│   ├── cli/                    # Command-line interface
│   │   ├── main.py            # Entry point
│   │   └── commands/          # Individual commands
│   ├── config/                 # Configuration management
│   ├── data/                   # Data loading/conversion
│   ├── wrangling/              # Data transformations
│   ├── cohorts/                # Cohort management
│   ├── analytics/              # Analysis framework
│   ├── dictionary/             # Data dictionary tools
│   └── utils/                  # Shared utilities
├── config/                     # Configuration files
│   ├── config.yaml            # Main config
│   ├── field_mappings.yaml    # Field name mappings
│   └── wrangling_rules.yaml   # Transformation rules
├── data/                       # Data storage (gitignored)
│   ├── parquet/               # Converted data
│   ├── metadata/              # Data dictionary
│   └── .audit/                # Audit logs
├── plugins/                    # Custom plugins
├── proposals/                  # RFCs and proposals
├── docs/                       # Documentation
└── tests/                      # Test suite
```

---

## Future Architecture (Proposal 001)

### Configuration-Driven Cohort Building

```
config/cohort_building/
├── baseline_fields.yaml          # Baseline field selection
├── derived_age_fields.yaml       # Age calculations
├── temporal_resolution.yaml      # Temporal strategies
├── disease_rules/
│   ├── dmd.yaml                  # DMD-specific rules
│   ├── als.yaml                  # ALS-specific rules
│   └── sma.yaml                  # SMA-specific rules
└── ecrf_rules/
    ├── pulmonary_function.yaml   # PFT handling
    └── medications.yaml          # Medication rules
```

### Cohort Builder API

```python
from movr.cohorts import CohortBuilder

builder = CohortBuilder()

# Simple cohort
cohort = builder.create_cohort(
    base_table="demographics",
    temporal_strategy="last_encounter",
    disease="DMD"
)

# Complex cohort with disease rules
cohort = builder.create_cohort_from_template(
    disease="DMD",
    template="ambulatory"
)
```

See [Proposal 001: Cohort Builder Architecture](proposals/001-cohort-builder-architecture.md) for full details.

---

## Security Considerations

### PHI Handling

- PHI files excluded by default (`*_PHI.xlsx` skipped)
- No PHI committed to git (`.gitignore` rules)
- Audit logging for PHI access (planned)
- Export filtering for public reports

### Data Integrity

- Source files are read-only
- Parquet files include checksums
- Audit logs track all transformations
- Validation ensures data quality

---

## Performance Considerations

### Optimization Strategies

1. **Parquet Column Pruning:** Load only needed columns
2. **Lazy Evaluation:** Defer computation until needed
3. **Chunked Processing:** Handle large datasets in batches
4. **Caching:** Cache expensive computations

### Targets

- Excel → Parquet: < 30 seconds for 50MB
- Data loading: < 5 seconds for 10K participants
- Cohort filtering: < 1 second for complex filters
- Summary statistics: < 5 seconds for full dataset

---

## Related Documentation

- [README.md](README.md) - Project overview
- [FEATURES.md](FEATURES.md) - Feature roadmap
- [DATA_WRANGLING_RULES.md](DATA_WRANGLING_RULES.md) - Data processing rules
- [docs/DATA_WRANGLING_PATTERNS.md](docs/DATA_WRANGLING_PATTERNS.md) - Implemented patterns
- [proposals/001-cohort-builder-architecture.md](proposals/001-cohort-builder-architecture.md) - Cohort builder proposal

---

**Last Updated:** 2025-11-20
