# MOVR DataHub Analytics

**Clinical data analytics framework for neuromuscular disease registries**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Platform Support:** ✅ Linux | ✅ Windows (WSL) | ✅ macOS

---

## Overview
MOVR DataHub Analytics is an open-source Python package for analyzing clinical registry data from the [MOVR (neuroMuscular ObserVational Research) Data Hub](https://openmovr.github.io/). Designed as a PyPI-installable library, it provides researchers and data scientists with standardized tools for processing, analyzing, and visualizing neuromuscular disease registry data.

*Future State: This package transforms raw Excel registry exports into analysis-ready datasets through automated data wrangling, quality validation, and cohort management. Whether you're conducting descriptive studies, building patient cohorts, or exploring data dictionaries, MOVR DataHub Analytics streamlines the analytical workflow while maintaining data integrity and audit trails.*

**Key Features:**
- **Excel → Parquet conversion** with audit trails
- **Automated data wrangling** with YAML-configurable rules
- **Cohort management** with flexible filtering
- **Built-in analytics** for descriptive statistics and reporting
- **Data dictionary explorer** for field search and metadata
- **Plugin architecture** for custom transformations
- **Comprehensive documentation** with example notebooks

---

## Quick Start

> **Note:** This package is **not yet on PyPI**. You install it locally in editable mode.
> See **[Development Environment Guide](docs/DEVELOPMENT_ENVIRONMENT.md)** for why and how this works.

```bash
# Clone and install
git clone https://github.com/OpenMOVR/movr-datahub-analytics.git
cd movr-datahub-analytics
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,viz,notebooks]"

# Setup and convert data
movr setup
movr convert
movr validate
```

See **[QUICK_START.md](QUICK_START.md)** for complete installation and platform-specific instructions.
---
## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [CLI Usage](#cli-usage)
- [Project Structure](#project-structure)
- [Data Wrangling Rules](#data-wrangling-rules)
- [Working with PHI Data](#working-with-phi-data)
- [Documentation](#documentation)
- [Development](#development)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [About This Project](#about-this-project)
- [Citation](#citation)
- [Support](#support)
- [Acknowledgments](#acknowledgments)
- [Community Engagement](#community-engagement)
---

## CLI Usage

```bash
# Interactive setup wizard (first time)
movr setup

# Import data dictionary (auto-detects or specify path)
movr import-dictionary
movr import-dictionary path/to/dictionary.xlsx

# Convert Excel to Parquet
movr convert
movr convert --clean  # Remove old parquet files first

# Validate data quality
movr validate

# Check system status
movr status

# View summary statistics
movr summary --registry datahub --metric all

# Data dictionary exploration
movr dictionary search "age"
movr dictionary search "medication" --diseases "DMD,SMA"
movr dictionary search "ambulation" --diseases "all"  # Show all disease columns
movr dictionary search "vital" --form "Encounter"
movr dictionary list-fields
movr dictionary show-field FACPATID

# Future commands (coming in Phase 2):
# movr cohorts create --name dmd_pediatric --filter "DISEASE=DMD,AGE=0-18"
# movr analyze --cohort dmd_pediatric --type descriptive --output output/report.xlsx
```

---

## Project Structure

```
movr-datahub-analytics/
├── src/movr/                   # Main package / library (The PyPI installable)
│   ├── config/                # Configuration management
│   ├── data/                  # Excel/Parquet loading (data loading)
│   ├── wrangling/             # Data cleaning & transformation
│   ├── cohorts/               # Cohort management
│   ├── analytics/             # Analysis framework (analysis tools)
│   ├── dictionary/            # Data dictionary tools
│   ├── workflows/             # Pipeline orchestration
│   ├── utils/                 # Shared utilities
│   └── cli/                   # Command-line interface
├── config/                     # Configuration files
│   ├── config.yaml            # Main configuration
│   ├── wrangling_rules.yaml   # Transformation rules
│   └── field_mappings.yaml    # Field name mappings (fallback)
├── data/                       # Data storage (gitignored)
│   ├── parquet/               # Converted Parquet files
│   ├── metadata/              # Data dictionary and metadata
│   └── .audit/                # Audit logs
├── scripts/                    # Standalone helper scripts
├── plugins/                    # Custom user plugins
├── notebooks/                  # Example Jupyter notebooks
├── tests/                      # Test suite
└── docs/                       # Documentation
```
| Location   | Purpose                                  | Part of PyPI package? |
|------------|------------------------------------------|-----------------------|
| src/movr/  | Library code (classes, functions, utils) | Yes                   |
| scripts/   | Standalone scripts that use the library  | No (and shouldn't be) |
| notebooks/ | Exploratory/example notebooks            | No (and shouldn't be) |

#### Note: For contributors buliding new utils/features:
1. Create code in ```src/movr/``` (e.g., ```src/movr/utils/new_helper.py```)
2. Export it in appropriate ```__init__.py```
3. Test it in ``notebooks/`` or ``scripts/``


## Core Concepts

- [Core Concepts](#core-concepts)
  - [1 Excel → Parquet Pipeline](#1-excel--parquet-pipeline)
  - [2 Data Wrangling](#2-data-wrangling)
  - [3 Cohort Building](#3-cohort-building)
  - [4 Custom Transformations](#4-custom-transformations)

### 1. Excel → Parquet Pipeline

Convert Excel files to efficient Parquet format with audit logging.

**The setup wizard automatically creates your configuration:**

```yaml
# config/config.yaml (auto-generated by `movr setup`)
data_sources:
  - name: demographics
    excel_path: ../source-movr-data/Demographics_noPHI.xlsx
    sheet_mappings:
      MainData: demographics_maindata
    skip_sheets: []
  - name: encounter
    excel_path: ../source-movr-data/Encounter.xlsx
    sheet_mappings:
      MainData: encounter_maindata
    skip_sheets: []
```

**Then convert:**
```bash
movr convert
```

**What it does:**
- Reads Excel files from configured paths
- Converts sheets to Parquet format
- Stores in `data/parquet/`
- Creates audit logs in `data/.audit/`
- Preserves original Excel files (read-only)

### 2. Data Wrangling

Apply standardized cleaning rules via YAML:

```yaml
# config/wrangling_rules.yaml
rules:
  - name: "deduplicate_encounters"
    tables: ["encounter_maindata"]
    action: "drop_duplicates"
    subset: ["FACPATID", "CASE_ID", "FORM_NAME"]

  - name: "parse_dates"
    tables: ["all"]
    action: "parse_dates"
    columns: ["ADMIT_DATE", "DISCHARGE_DATE", "BIRTH_DATE"]
```

### 3. Cohort Building

```python
# Programmatic API
cohorts = CohortManager(tables)
base = cohorts.create_base_cohort()
dmd = cohorts.filter_cohort("base", "dmd", filters={"DISEASE": "DMD"})

# Or via YAML config
# config/cohort_definitions.yaml
cohorts:
  - name: "dmd_pediatric"
    source: "base"
    filters:
      DISEASE: "DMD"
      AGE: {min: 0, max: 18}
```

### 4. Custom Transformations

Create plugins for complex logic:

```python
# plugins/my_transform.py
from movr.wrangling.plugins import register_plugin

@register_plugin("my_custom_rule")
def my_transform(df, **kwargs):
    # Your custom logic
    df["NEW_FIELD"] = df["OLD_FIELD"].apply(my_function)
    return df
```

```yaml
# Reference in wrangling_rules.yaml
rules:
  - name: "apply_custom_logic"
    tables: ["encounter_maindata"]
    action: "plugin"
    plugin: "plugins.my_transform.my_custom_rule"
```

---

## Data Wrangling Rules

All data processing follows documented rules in [`docs/DATA_WRANGLING_RULES.md`](docs/DATA_WRANGLING_RULES.md):

- **Deduplication:** Table-specific unique keys
- **Data types:** String IDs, parsed dates, proper numerics
- **Missing values:** Standardized NA handling
- **Dates:** Validation, age calculations, ordering checks
- **Referential integrity:** Foreign key validation
- **Value normalization:** Text cleaning, range validation

**Strictness Modes:**
- `strict`: Raise errors on violations
- `permissive`: Flag issues, continue processing (default)
- `interactive`: Prompt user for decisions

---

## Working with PHI Data

⚠️ **PHI (Protected Health Information) is NOT included in the standard workflow by default.**

**The setup wizard automatically:**
- Skips files with `_PHI` in the name (e.g., `Demographics_PHI.xlsx`)
- Includes files with `_noPHI` in the name (e.g., `Demographics_noPHI.xlsx`)
- Skips data dictionary files

**Important: Excel files are your source of truth**
- Never edit the original Excel files in `source-movr-data/` directly
- If you need to modify data, copy the file first and work with the copy
- Keep `source-movr-data/` read-only when possible
- Back up the original files regularly

For limited datasets requiring geographic or other PHI fields (future feature):

```python
from movr.data import load_excel_with_phi

# Specify allowed PHI columns
tables = load_excel_with_phi(
    excel_path="source-movr-data/Demographics_PHI.xlsx",
    allowed_phi_columns=["ZIP_CODE", "CITY", "STATE"]
)

# Process and ensure PHI is removed before export
clean_tables = remove_phi_columns(tables, export_mode=True)
```

**Best Practices:**
- Never commit PHI files to git (already in .gitignore)
- Only load PHI when absolutely necessary
- Document PHI usage in audit logs
- Remove PHI before generating public reports

---

## Documentation

### Getting Started
- **[Development Environment Guide](docs/DEVELOPMENT_ENVIRONMENT.md)** - Understanding editable mode, venv vs conda, project structure
- **[Quick Start Guide](QUICK_START.md)** - Installation, setup, and usage examples
- **[Example Notebooks](notebooks/)** - Jupyter notebook examples
  - `03_exploratory_interpreter_example.ipynb` — programmatic demo of `scripts/exploratory_interpreter.py` showing how to load the helper module, create in-memory cohorts, and run `DescriptiveAnalyzer` comparisons
  - `04_exploratory_interpreter_example.ipynb` — minimal parquet-loader + interpreter example demonstrating batch cohort creation and abbreviation configs
  - See `scripts/README.md` for small helpers and CLI usage (quick, in-memory cohort creation)

### Project Planning & Tracking
- **[Feature Roadmap](docs/FEATURES.md)** - Complete feature tracking and implementation status
- **[Data Wrangling Tracker](docs/DATA_WRANGLING_TRACKER.md)** - Rule implementation status tracker
- **[Architecture Plan](docs/ARCHITECTURE_PLAN.md)** - System design and technical decisions

### Reference Documentation
- **[Data Wrangling Rules](docs/DATA_WRANGLING_RULES.md)** - Comprehensive data processing rules
- **[Data Wrangling Patterns](docs/DATA_WRANGLING_PATTERNS.md)** - Implemented patterns from summary command
- **[Best Practices](docs/BEST_PRACTICES.md)** - Standards for data handling, analysis, and code quality
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute code, propose features, and submit RFCs
- **[Proposals Directory](proposals/)** - RFC-style feature and rule proposals
  - [Proposal 001: Cohort Builder Architecture](proposals/001-cohort-builder-architecture.md) - Configuration-driven cohort building system

### API Documentation
- **[API Reference](docs/api-reference/)** - Full API documentation (coming in Phase 2)

---

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/ tests/
```

### Type Checking

```bash
mypy src/
```

### Pre-commit Hooks

```bash
pre-commit install
pre-commit run --all-files
```

---

## Roadmap

### Phase 1: Core Library (Current)
- ✅ Package structure
- ✅ Excel → Parquet conversion (all sheets, repeat groups, --clean flag)
- ✅ Basic data wrangling
- ✅ Cohort management
- ✅ Descriptive analytics
- ✅ CLI implementation (setup, convert, validate, summary, dictionary)
- ✅ Data dictionary import and search
- ✅ Summary statistics CLI
- ⏳ Test coverage >80%

### Phase 2: Advanced Features (Q1 2026)
- Configuration-driven cohort builder (see [Proposal 001](proposals/001-cohort-builder-architecture.md))
  - Temporal resolution strategies (first/last encounter, field-specific)
  - Disease-specific rules (DMD, ALS, SMA)
  - eCRF-specific rules (pulmonary function, cardiac assessment)
  - Derived age field calculations
- Plugin system
- Workflow orchestration (DAG)
- Advanced cohort filters (boolean logic, cohort algebra)
- Advanced dictionary features (field usage tracking, value distributions)
- Report generation (PDF/HTML)

### Phase 3: Visualization (Q2 2026)
- Matplotlib/Seaborn integration
- Plotly dashboards
- Publication-ready figures

### Phase 4: Web Interface (Q3 2026)
- FastAPI backend
- React frontend
- Visual cohort builder

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests
5. Run tests and linters
6. Commit with clear messages
7. Push and create a Pull Request

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## About This Project

**MOVR DataHub Analytics** is an open-source initiative created and maintained by **Andre Daniel Paredes**.

**Creator & Architect**: Andre Daniel Paredes
**Affiliation**: Muscular Dystrophy Association (MDA)
**Project Type**: Independent open-source initiative

This project is an independent effort to advance neuromuscular disease research through better data analytics tools. While Andre is affiliated with MDA, this is a personal open-source initiative designed to benefit the broader research community and is open to collaboration with both software and scientific communities.

---

## Citation

If you use MOVR DataHub Analytics in your research, please cite:

```bibtex
@software{movr_datahub_analytics,
  title = {MOVR DataHub Analytics: Clinical Data Analytics Framework for Neuromuscular Disease Registries},
  author = {Paredes, Andre Daniel},
  year = {2025},
  url = {https://github.com/openmovr/movr-datahub-analytics},
  note = {Open-source initiative for MOVR registry data analysis}
}
```

---

## Support

- **Issues:** [GitHub Issues](https://github.com/openmovr/movr-datahub-analytics/issues)
- **Discussions:** [GitHub Discussions](https://github.com/openmovr/movr-datahub-analytics/discussions)
- **Documentation:** See the [Documentation](#documentation) section above

---

## Acknowledgments

**Project Creator & Maintainer**: Andre Daniel Paredes

**Contributors**:
- Open Source Community Contributors (see [CONTRIBUTORS.md](CONTRIBUTORS.md))

**Special Thanks**:
- Muscular Dystrophy Association (MDA) for supporting neuromuscular disease research
- MOVR (Muscular Dystrophy Outcomes and Value in Research) Data Hub community
- All contributors and collaborators from the research and open-source software communities

---

## Community Engagement

This project welcomes engagement from:
- **Research Community**: Clinical researchers, data scientists, epidemiologists working with registry data
- **Open-Source Software Community**: Developers interested in healthcare data analytics, Python libraries, and data science tools
- **Domain Experts**: Neuromuscular disease specialists, registry coordinators, data managers

We encourage cross-community collaboration between software engineers and clinical researchers to build better tools for advancing neuromuscular disease research.

---

**Built with ❤️ for better neuromuscular disease research**
