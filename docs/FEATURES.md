# Feature Roadmap & Implementation Tracker

**Comprehensive tracking of all features, enhancements, and planned capabilities**

> This document tracks feature implementation status and serves as the roadmap for the project. It informs the architecture and guides development priorities.

---

## Feature Status Legend

| Status | Symbol | Description |
|--------|--------|-------------|
| **Completed** | ✅ | Feature is implemented, tested, and documented |
| **In Progress** | 🚧 | Currently being developed |
| **Planned** | 📅 | Scheduled for implementation |
| **Proposed** | 💡 | Idea submitted, awaiting evaluation/approval |
| **Under Review** | 🔍 | Proposal being evaluated by team |
| **Blocked** | 🔴 | Cannot proceed due to dependency/issue |
| **Deferred** | ⏸️ | Postponed to future release |
| **Rejected** | ❌ | Proposal declined (with reason) |

---

## Quick Navigation

- [Phase 1: Core Library](#phase-1-core-library-foundation)
- [Phase 2: Advanced Features](#phase-2-advanced-features)
- [Phase 3: Visualization & Reporting](#phase-3-visualization--reporting)
- [Phase 4: Web Interface](#phase-4-web-interface)
- [Proposed Features](#proposed-features-awaiting-approval)
- [Under Consideration](#under-consideration-speculative)

---

## Phase 1: Core Library (Foundation)

**Target**: Q4 2025 (Current Phase)
**Focus**: Essential data pipeline and analysis capabilities

### 1.1 Package Infrastructure

| Feature ID | Feature | Status | Priority | Notes |
|------------|---------|--------|----------|-------|
| F-001 | Package structure (src layout) | ✅ Completed | High | Initial setup done |
| F-002 | PyPI packaging (pyproject.toml) | ✅ Completed | High | Ready for publishing |
| F-003 | Virtual environment support | ✅ Completed | High | Works with venv, conda |
| F-004 | CLI framework (Click) | ✅ Completed | High | `movr` command available |
| F-005 | Configuration management (YAML + Pydantic) | ✅ Completed | High | `config/config.yaml` |
| F-006 | Logging and error handling | ✅ Completed | Medium | Loguru integration |
| F-007 | Unit test framework (pytest) | 📅 Planned | High | Test suite needed |
| F-008 | CI/CD pipeline (GitHub Actions) | 📅 Planned | Medium | Automated testing |

### 1.2 Data Ingestion & Conversion

| Feature ID | Feature | Status | Priority | Notes |
|------------|---------|--------|----------|-------|
| F-010 | Excel file reading (openpyxl) | ✅ Completed | High | Multi-sheet support |
| F-011 | Parquet conversion | ✅ Completed | High | Using pyarrow |
| F-012 | Audit trail logging | ✅ Completed | High | Conversion metadata tracked |
| F-013 | Setup wizard CLI (`movr setup`) | ✅ Completed | High | Interactive configuration |
| F-014 | Auto-discovery of Excel files | ✅ Completed | Medium | Scans source directory |
| F-015 | PHI file auto-skipping | ✅ Completed | High | Skips `_PHI` files |
| F-016 | Data dictionary file skipping | ✅ Completed | Medium | Auto-detects dictionary files |
| F-016a | Multi-sheet conversion with repeat group detection | ✅ Completed | High | Converts all sheets, detects `_rg` patterns |
| F-016b | Clean conversion flag (`--clean`) | ✅ Completed | Medium | Remove old Parquet files before conversion |
| F-017 | Incremental conversion (only changed files) | 📅 Planned | Low | Performance optimization |
| F-018 | CSV input support | 💡 Proposed | Low | Alternative to Excel |
| F-019 | Delta Lake format support | 💡 Proposed | Low | For versioning |

### 1.3 Data Wrangling

| Feature ID | Feature | Status | Priority | Notes |
|------------|---------|--------|----------|-------|
| F-030 | YAML-based wrangling rules | ✅ Completed | High | `config/wrangling_rules.yaml` |
| F-031 | Core transformations (dedup, type conversion) | ✅ Completed | High | Basic rules implemented |
| F-032 | Plugin architecture for custom rules | 🚧 In Progress | High | `plugins/` directory created |
| F-033 | Strictness modes (strict/permissive/interactive) | ✅ Completed | Medium | Configurable behavior |
| F-034 | Data validation pipeline | 🚧 In Progress | High | `movr validate` command |
| F-035 | Cleaning report generation | 📅 Planned | Medium | Summary of applied rules |
| F-036 | Rule dependency management | 💡 Proposed | Low | Order-dependent rules |
| F-037 | Conditional rule application | 💡 Proposed | Medium | Apply rules based on conditions |

### 1.4 Cohort Management

| Feature ID | Feature | Status | Priority | Notes |
|------------|---------|--------|----------|-------|
| F-050 | Base cohort creation (enrollment validation) | ✅ Completed | High | Requires 3 forms |
| F-051 | Simple filtering (equality, range) | ✅ Completed | High | Disease, age, etc. |
| F-052 | Cohort summary statistics | ✅ Completed | Medium | Patient counts, registry dist |
| F-053 | YAML-based cohort definitions | ✅ Completed | Medium | `config/cohort_definitions.yaml` |
| F-054 | Cohort hierarchy (parent → child cohorts) | ✅ Completed | Medium | Build on existing cohorts |
| F-055 | Custom filter functions | ✅ Completed | Medium | User-defined logic |
| F-055a | Field name resolution | ✅ Completed | High | Canonical → actual column names |
| F-055b | Registry filtering (USNDR/DataHub) | ✅ Completed | High | `registry: true/false` filter |
| F-055c | Age calculation from DOB | ✅ Completed | High | Derived field support |
| F-055d | Disease filtering | ✅ Completed | High | `disease: "DMD"` or list |
| F-056 | Cohort comparison tools | 💡 Proposed | Low | Compare demographics |
| F-057 | Cohort persistence (save/load) | 💡 Proposed | Low | Reuse cohorts across sessions |
| F-058 | Dynamic cohort updates | 💡 Proposed | Low | Auto-update when data changes |

### 1.5 Data Dictionary & Metadata

| Feature ID | Feature | Status | Priority | Notes |
|------------|---------|--------|----------|-------|
| F-060 | Data dictionary Excel import | ✅ Completed | High | `movr import-dictionary` |
| F-061 | Data dictionary auto-detection | ✅ Completed | High | Finds dictionary files automatically |
| F-062 | Dictionary to Parquet conversion | ✅ Completed | High | Stored in `data/metadata/` |
| F-063 | Dictionary search CLI | ✅ Completed | High | `movr dictionary search` |
| F-064 | Disease filtering in search | ✅ Completed | Medium | `--diseases "DMD,SMA"` |
| F-065 | Form/table filtering in search | ✅ Completed | Medium | `--form "Encounter"` |
| F-066 | Field listing | ✅ Completed | Medium | `movr dictionary list-fields` |
| F-067 | Field detail view | ✅ Completed | Medium | `movr dictionary show-field` |
| F-068 | Field mappings fallback config | ✅ Completed | Medium | `config/field_mappings.yaml` |
| F-069 | Modular config architecture | ✅ Completed | Medium | Scalable for 33+ tables |

### 1.6 Analytics & Reporting

| Feature ID | Feature | Status | Priority | Notes |
|------------|---------|--------|----------|-------|
| F-070 | Descriptive statistics analyzer | ✅ Completed | High | Mean, median, counts |
| F-071 | Export to Excel | ✅ Completed | High | `.to_excel()` method |
| F-072 | Export to JSON | ✅ Completed | Medium | `.to_json()` method |
| F-073 | Summary statistics CLI | ✅ Completed | High | `movr summary` command |
| F-073a | Enrollment by disease | ✅ Completed | High | Participant counts |
| F-073b | Annual recruitment tracking | ✅ Completed | Medium | Enrollment by year |
| F-073c | Encounter statistics | ✅ Completed | High | Total and by year |
| F-073d | Average encounters per participant | ✅ Completed | Medium | Overall and by disease/year |
| F-073e | Registry filtering | ✅ Completed | Medium | DataHub, USNDR, all |
| F-074 | Summary report generation | 📅 Planned | Medium | PDF/HTML reports |
| F-075 | Jupyter notebook examples | ✅ Completed | High | `notebooks/01_getting_started.ipynb` |
| F-076 | Cross-tabulation | 💡 Proposed | Medium | Disease x Age group |
| F-077 | Longitudinal analysis helpers | 💡 Proposed | Medium | Time-series data |

### 1.7 Documentation

| Feature ID | Feature | Status | Priority | Notes |
|------------|---------|--------|----------|-------|
| F-090 | README with quick start | ✅ Completed | High | Updated with dictionary commands |
| F-091 | Architecture documentation | ✅ Completed | High | ARCHITECTURE_PLAN.md |
| F-092 | Data wrangling rules documentation | ✅ Completed | High | DATA_WRANGLING_RULES.md |
| F-093 | Getting started guide | ✅ Completed | High | GETTING_STARTED.md |
| F-094 | Platform-specific quick start | ✅ Completed | High | QUICK_START.md |
| F-095 | Data wrangling tracker | ✅ Completed | Medium | DATA_WRANGLING_TRACKER.md |
| F-096 | Feature roadmap (this document) | ✅ Completed | Medium | FEATURES.md |
| F-096a | Summary command documentation | ✅ Completed | Medium | docs/SUMMARY_COMMAND.md |
| F-097 | Contributing guidelines | 🚧 In Progress | High | CONTRIBUTING.md |
| F-098 | API reference documentation | 📅 Planned | Medium | Sphinx/MkDocs |
| F-099 | Best practices guide | 🚧 In Progress | Medium | BEST_PRACTICES.md |

---

## Phase 2: Advanced Features

**Target**: Q1-Q2 2026
**Focus**: Enhanced capabilities, workflow automation, advanced analytics

### 2.1 Workflow Orchestration

| Feature ID | Feature | Status | Priority | Notes |
|------------|---------|--------|----------|-------|
| F-200 | DAG-based pipeline execution | 📅 Planned | High | Define workflows as DAGs |
| F-201 | Task dependencies | 📅 Planned | High | Automatic ordering |
| F-202 | Parallel execution | 📅 Planned | Medium | Speed up processing |
| F-203 | Workflow templates | 💡 Proposed | Low | Common analysis patterns |
| F-204 | Checkpoint/resume support | 💡 Proposed | Medium | Resume failed workflows |

### 2.2 Advanced Dictionary Features

| Feature ID | Feature | Status | Priority | Notes |
|------------|---------|--------|----------|-------|
| F-220 | Field usage tracking | 💡 Proposed | Low | Which fields are used |
| F-221 | Field value distributions | 💡 Proposed | Medium | Value frequency analysis |
| F-222 | Dictionary versioning | 💡 Proposed | Low | Track dictionary changes |
| F-223 | Field relationship mapping | 💡 Proposed | Medium | FK relationships |

### 2.3 Advanced Cohort Features

**See also:** [Proposal 001: Cohort Builder Architecture](proposals/001-cohort-builder-architecture.md)

| Feature ID | Feature | Status | Priority | Notes |
|------------|---------|--------|----------|-------|
| F-240 | Complex boolean filters (AND/OR/NOT) | 📅 Planned | High | Advanced logic |
| F-241 | Time-based filtering | 📅 Planned | Medium | Date range cohorts |
| F-242 | Cohort algebra (union, intersection) | 💡 Proposed | Medium | Combine cohorts |
| F-243 | Cohort versioning | 💡 Proposed | Low | Track cohort changes |
| F-244 | Visual cohort builder (CLI-based) | 💡 Proposed | Low | Interactive cohort creation |
| F-245 | Temporal resolution strategies | 💡 Proposed | High | First/last encounter, field-specific ([Proposal 001](proposals/001-cohort-builder-architecture.md)) |
| F-246 | Disease-specific cohort rules | 💡 Proposed | High | DMD, ALS, SMA rules ([Proposal 001](proposals/001-cohort-builder-architecture.md)) |
| F-247 | eCRF-specific cohort rules | 💡 Proposed | Medium | Pulmonary, cardiac rules ([Proposal 001](proposals/001-cohort-builder-architecture.md)) |
| F-248 | Derived age field calculations | 💡 Proposed | High | Age_At_Enrollment, Age_At_Diagnosis ([Proposal 001](proposals/001-cohort-builder-architecture.md)) |
| F-249 | Configuration-driven cohort builder | 💡 Proposed | High | YAML configs for baseline, temporal, disease rules ([Proposal 001](proposals/001-cohort-builder-architecture.md)) |

### 2.4 Advanced Analytics

| Feature ID | Feature | Status | Priority | Notes |
|------------|---------|--------|----------|-------|
| F-260 | Survival analysis | 📅 Planned | Medium | Time-to-event analysis |
| F-261 | Longitudinal modeling | 📅 Planned | Medium | Repeated measures |
| F-262 | Statistical testing framework | 💡 Proposed | Medium | t-tests, chi-square, etc. |
| F-263 | Effect size calculations | 💡 Proposed | Low | Cohen's d, odds ratios |
| F-264 | Regression modeling | 💡 Proposed | Low | Linear, logistic regression |

### 2.5 Quality Assurance

| Feature ID | Feature | Status | Priority | Notes |
|------------|---------|--------|----------|-------|
| F-280 | Automated data quality checks | 📅 Planned | High | Validation rules |
| F-281 | Anomaly detection | 💡 Proposed | Medium | Statistical outlier detection |
| F-282 | Data completeness metrics | 📅 Planned | Medium | Missing data reporting |
| F-283 | Data quality dashboard | 💡 Proposed | Low | Visual QA summary |

---

## Phase 3: Visualization & Reporting

**Target**: Q2-Q3 2026
**Focus**: Publication-ready visualizations and reports

### 3.1 Static Visualizations

| Feature ID | Feature | Status | Priority | Notes |
|------------|---------|--------|----------|-------|
| F-300 | Matplotlib integration | 📅 Planned | High | Basic plots |
| F-301 | Seaborn integration | 📅 Planned | High | Statistical plots |
| F-302 | Publication-ready figure export | 📅 Planned | Medium | High-res PNG, SVG |
| F-303 | Plot templates | 💡 Proposed | Low | Reusable plot configurations |
| F-304 | Multi-panel figures | 💡 Proposed | Low | Composite visualizations |

### 3.2 Interactive Visualizations

| Feature ID | Feature | Status | Priority | Notes |
|------------|---------|--------|----------|-------|
| F-320 | Plotly integration | 📅 Planned | Medium | Interactive plots |
| F-321 | Interactive dashboards | 💡 Proposed | Medium | Plotly Dash |
| F-322 | Jupyter widget integration | 💡 Proposed | Low | Interactive notebooks |

### 3.3 Report Generation

| Feature ID | Feature | Status | Priority | Notes |
|------------|---------|--------|----------|-------|
| F-340 | HTML report templates | 📅 Planned | Medium | Web-based reports |
| F-341 | PDF report generation | 📅 Planned | Medium | Printable reports |
| F-342 | Markdown report export | 💡 Proposed | Low | For documentation |
| F-343 | PowerPoint export | 💡 Proposed | Low | Presentation slides |

---

## Phase 4: Web Interface

**Target**: Q3-Q4 2026
**Focus**: Browser-based interface for non-programmers

### 4.1 Backend API

| Feature ID | Feature | Status | Priority | Notes |
|------------|---------|--------|----------|-------|
| F-400 | FastAPI REST API | 📅 Planned | High | Backend service |
| F-401 | Authentication & authorization | 📅 Planned | High | User management |
| F-402 | API documentation (OpenAPI) | 📅 Planned | Medium | Auto-generated docs |
| F-403 | Rate limiting | 💡 Proposed | Low | Prevent abuse |

### 4.2 Frontend

| Feature ID | Feature | Status | Priority | Notes |
|------------|---------|--------|----------|-------|
| F-420 | React web app | 📅 Planned | High | Modern UI |
| F-421 | Visual cohort builder | 📅 Planned | High | Drag-and-drop filters |
| F-422 | Data explorer interface | 📅 Planned | Medium | Browse tables |
| F-423 | Dashboard view | 💡 Proposed | Medium | Summary statistics |
| F-424 | Report download | 📅 Planned | Medium | Export from web UI |

---

## Proposed Features (Awaiting Approval)

**These features have been formally proposed but not yet approved for implementation.**

### Security & Privacy

| Feature ID | Feature | Proposer | Date | Status |
|------------|---------|----------|------|--------|
| F-500 | PHI encryption at rest | TBD | TBD | 💡 Proposed |
| F-501 | Audit logging for data access | TBD | TBD | 💡 Proposed |
| F-502 | Role-based access control | TBD | TBD | 💡 Proposed |
| F-503 | De-identification tools | TBD | TBD | 💡 Proposed |

### Integration & Export

| Feature ID | Feature | Proposer | Date | Status |
|------------|---------|----------|------|--------|
| F-520 | REDCap integration | TBD | TBD | 💡 Proposed |
| F-521 | SQL database export | TBD | TBD | 💡 Proposed |
| F-522 | FHIR format export | TBD | TBD | 💡 Proposed |
| F-523 | Cloud storage integration (S3, Azure) | TBD | TBD | 💡 Proposed |

### Machine Learning

| Feature ID | Feature | Proposer | Date | Status |
|------------|---------|----------|------|--------|
| F-540 | Feature engineering helpers | TBD | TBD | 💡 Proposed |
| F-541 | Scikit-learn integration | TBD | TBD | 💡 Proposed |
| F-542 | Model training framework | TBD | TBD | 💡 Proposed |
| F-543 | Prediction export | TBD | TBD | 💡 Proposed |

---

## Under Consideration (Speculative)

**Ideas being explored, not yet formal proposals.**

### Performance & Scalability

- Dask integration for large datasets
- GPU acceleration for analytics
- Distributed processing (Spark)
- Query optimization for large cohorts

### Collaboration Features

- Multi-user workspaces
- Shared cohort library
- Comment/annotation system
- Version control for analyses

### Advanced Analytics

- Propensity score matching
- Causal inference tools
- Network analysis
- Natural language processing for clinical notes

---

## Rejected Features

**Features that were proposed but declined, with reasoning.**

| Feature ID | Feature | Reason for Rejection | Date |
|------------|---------|---------------------|------|
| (None yet) | | | |

---

## Deferred Features

**Features postponed to later releases.**

| Feature ID | Feature | Reason for Deferral | Target Phase |
|------------|---------|---------------------|--------------|
| (None yet) | | | |

---

## Feature Request Process

1. **Submit Proposal**: Create a detailed proposal in `proposals/` directory (see [CONTRIBUTING.md](CONTRIBUTING.md))
2. **Review**: Team reviews proposal and assigns status
3. **Approval**: If approved, feature moves to "Planned" and assigned to phase
4. **Implementation**: Feature is built, tested, documented
5. **Release**: Feature marked as "Completed" and included in changelog

---

## Priority Guidelines

- **High**: Core functionality, blocking other features, critical for users
- **Medium**: Important for usability/quality, not immediately blocking
- **Low**: Nice-to-have, optimization, edge cases, long-term vision

---

## Related Documentation

- [ARCHITECTURE_PLAN.md](ARCHITECTURE_PLAN.md) - System architecture and design decisions
- [DATA_WRANGLING_TRACKER.md](DATA_WRANGLING_TRACKER.md) - Data rule implementation status
- [CONTRIBUTING.md](CONTRIBUTING.md) - How to propose features and contribute
- [CHANGELOG.md](CHANGELOG.md) - Release notes and version history
- [proposals/](proposals/) - Detailed feature proposals

---

**Last Updated**: 2025-11-21
**Created By**: Andre Daniel Paredes
**Maintained By**: Andre Daniel Paredes

**Questions?** Open an issue on GitHub or start a discussion.
