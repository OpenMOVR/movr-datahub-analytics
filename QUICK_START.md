# MOVR DataHub Analytics - Quick Start

Getting started guide with platform-specific installation and usage examples.

---

## Platform Compatibility

| Platform | Status | Notes |
|----------|--------|-------|
| Linux | Fully Supported | Native support |
| Windows WSL | Fully Supported | WSL 2 with Ubuntu recommended |
| macOS | Compatible | Requires Python 3.9+ via Homebrew |

---

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- git

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git
```

### Windows WSL

```bash
# In Windows PowerShell (Administrator):
wsl --install

# Then in Ubuntu:
sudo apt update
sudo apt install python3 python3-pip python3-venv git
```

### macOS

```bash
brew install python@3.11 git
```

---

## Directory Structure

Set up your workspace with this structure:

```
/your-workspace/
├── movr-datahub-analytics/     # This repository
└── source-movr-data/           # Sibling directory with Excel files
    ├── Demographics_noPHI.xlsx
    ├── Encounter.xlsx
    ├── Diagnosis.xlsx
    ├── Log.xlsx
    ├── Discontinuation.xlsx
    └── data_dictionary.xlsx    # Data dictionary file
```

**Important:**
- Keep `source-movr-data/` as a sibling to `movr-datahub-analytics/`
- Never edit the original Excel files directly - they are your source of truth
- PHI files (e.g., `Demographics_PHI.xlsx`) are automatically skipped

---

## Installation

> **Why editable mode?** This package is not yet on PyPI. We install locally with `-e` so code changes are immediately available without reinstalling.
> See **[Development Environment Guide](docs/DEVELOPMENT_ENVIRONMENT.md)** for details on venv vs conda, project structure, and how editable mode works.

```bash
# Create workspace
mkdir -p ~/MDA && cd ~/MDA

# Clone repository
git clone https://github.com/OpenMOVR/movr-datahub-analytics.git
cd movr-datahub-analytics

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install package in editable mode
pip install -e ".[dev,viz,notebooks]"
```

---

## First-Time Setup

### Step 1: Run Setup Wizard

```bash
movr setup
```

The wizard will prompt for:
1. **Excel files location** - Press Enter for default `../source-movr-data`
2. **Output directory** - Press Enter for default `output`
3. **Strictness mode** - Press Enter for default `permissive`

### Step 2: Import Data Dictionary (Optional)

```bash
movr import-dictionary
```

### Step 3: Convert Excel to Parquet

```bash
movr convert
```

### Step 4: Validate Data

```bash
movr validate
```

---

## CLI Reference

```bash
movr setup                           # Run setup wizard
movr import-dictionary               # Import data dictionary
movr convert                         # Convert Excel to Parquet
movr convert --clean                 # Clean old files first
movr validate                        # Validate data quality
movr status                          # Check system status
movr summary --metric all            # View summary statistics

# Data dictionary exploration
movr dictionary search "age"
movr dictionary search "medication" --diseases "DMD,SMA"
movr dictionary list-fields
movr dictionary show-field FACPATID
```

---

## Basic Usage

### Load Data and Create Cohort

```python
from movr import load_data, CohortManager, DescriptiveAnalyzer

# Load all tables
tables = load_data()

# Create cohort manager
cohorts = CohortManager(tables)

# Create base enrolled cohort
base = cohorts.create_base_cohort()
print(f"Enrolled patients: {len(base)}")
```

### Filter and Analyze

```python
# Filter for DMD pediatric patients
dmd_peds = cohorts.filter_cohort(
    source_cohort="base",
    name="dmd_pediatric",
    filters={"DISEASE": "DMD", "AGE": (0, 18)}
)

# Analyze
analyzer = DescriptiveAnalyzer(cohort=None, tables=tables, cohort_manager=cohorts, cohort_name='dmd_pediatric')
results = analyzer.run_analysis()

# Export
results.to_excel("output/dmd_pediatric_report.xlsx")
```

### Custom Plugins

Create `plugins/my_transform.py`:

```python
from movr.wrangling.plugins import register_plugin

@register_plugin("my_drug_standardization")
def standardize_drugs(df, **kwargs):
    drug_map = {'spinraza': 'Nusinersen', 'zolgensma': 'Onasemnogene abeparvovec'}
    df['DRUG_NAME_STD'] = df['DRUG_NAME'].str.lower().map(drug_map).fillna(df['DRUG_NAME'])
    return df
```

Reference in `config/wrangling_rules.yaml`:

```yaml
rules:
  - name: "standardize_medications"
    tables: ["encounter_medication"]
    action: "plugin"
    plugin: "plugins.my_transform.my_drug_standardization"
```

---

## Troubleshooting

### "Config file not found"

```bash
# Ensure you're in the project directory
cd ~/MDA/movr-datahub-analytics
movr setup
```

### "Parquet file not found"

```bash
movr convert --clean
```

### "Module not found"

```bash
pip install -e ".[dev]"
```

### WSL: Jupyter won't open browser

Copy the URL from terminal output (e.g., `http://localhost:8888/?token=...`) and paste into your Windows browser.

---

## Daily Workflow

```bash
cd ~/MDA/movr-datahub-analytics
source .venv/bin/activate
jupyter notebook notebooks/
```

---

## Next Steps

- [README.md](README.md) - Project overview and full documentation links
- [docs/DATA_WRANGLING_RULES.md](docs/DATA_WRANGLING_RULES.md) - Data processing rules
- [docs/ARCHITECTURE_PLAN.md](docs/ARCHITECTURE_PLAN.md) - System design
- [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute

## Example Notebooks

Explore the `notebooks/` directory for hands-on examples:

- **Getting Started** - Basic data loading and exploration
- **Cohort Analysis** - Creating and comparing patient cohorts  
- **Descriptive Analytics** - Summary statistics and visualizations
- **Advanced Queries** - Custom filtering and data manipulation

```bash
# Launch Jupyter to explore notebooks
jupyter notebook notebooks/
```

Each notebook includes:
- Step-by-step explanations
- Code examples you can run and modify
- Sample outputs and visualizations

See individual notebook files for specific use cases and detailed walkthroughs.
