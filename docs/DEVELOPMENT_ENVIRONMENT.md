# Development Environment Guide

Current state of the `movr` package and how to set up your local environment.

---

## Current Package Status

**This package is NOT yet published to PyPI.**

You cannot run:
```bash
pip install movr-datahub-analytics  # This won't work (yet)
```

Instead, you install locally in **editable mode** from the cloned repository.

---

## What is Editable Mode (`-e`)?

When you run:
```bash
pip install -e ".[dev,notebooks]"
```

The `-e` flag means "editable" (also called "development mode"). Here's what happens:

| Without `-e` | With `-e` (editable) |
|--------------|----------------------|
| Copies `src/movr/` into your Python environment | Creates a link pointing to `src/movr/` |
| Changes require reinstall (`pip install .`) | Changes are immediately available |
| Used for stable releases | Used for active development |

**Why editable mode matters:**

1. **Live code changes** - Edit `src/movr/utils/something.py`, import it, changes work instantly
2. **No reinstall loop** - You don't have to run `pip install .` after every change
3. **Notebooks stay in sync** - Your notebooks always use the latest code
4. **Debugging is easier** - Stack traces point to your actual source files

**This is how all Python library development works.** Editable mode is your friend.

---

## venv vs Conda: Which Should You Use?

### Recommendation: Use `venv`

For this project, **`venv` is preferred** for these reasons:

| Aspect | venv | Conda |
|--------|------|-------|
| Simplicity | Built into Python, no extra install | Requires Anaconda/Miniconda |
| Size | Lightweight (~20MB) | Heavy (~3GB for Anaconda) |
| Speed | Fast environment creation | Slower, more complex solver |
| Reproducibility | `pip freeze` + requirements.txt | environment.yml (can diverge) |
| CI/CD | Standard in GitHub Actions | Extra setup needed |
| PyPI compatibility | Native | Can conflict with pip packages |

### When Conda Makes Sense

Use Conda if you need:
- Non-Python dependencies (e.g., CUDA, R, system libraries)
- Specific scientific packages that are hard to pip install (rare now)
- You're already in a Conda-based workflow

### Our Choice

We use **venv + pip** because:
1. All our dependencies are pure Python packages available on PyPI
2. Simpler contributor onboarding
3. Standard Python tooling (no Conda-specific quirks)
4. Easier CI/CD integration

---

## Setting Up Your Environment

### Step 1: Clone the Repository

```bash
mkdir -p ~/MDA && cd ~/MDA
git clone https://github.com/OpenMOVR/movr-datahub-analytics.git
cd movr-datahub-analytics
```

### Step 2: Create Virtual Environment

```bash
# Create the .venv directory
python3 -m venv .venv

# Activate it
source .venv/bin/activate  # Linux/macOS/WSL

# Windows (if not using WSL)
# .venv\Scripts\activate
```

**You should see `(.venv)` in your terminal prompt.**

### Step 3: Install in Editable Mode

```bash
# Full development setup (recommended)
pip install -e ".[dev,viz,notebooks]"

# Minimal setup (just core + notebooks)
pip install -e ".[notebooks]"
```

### Step 4: Verify Installation

```bash
# Check the CLI works
movr --help

# Check Python imports work
python -c "from movr import load_data; print('Success!')"
```

---

## Daily Workflow

```bash
# Always activate your environment first
cd ~/MDA/movr-datahub-analytics
source .venv/bin/activate

# Now you can:
# - Run CLI commands
movr status

# - Run notebooks
jupyter notebook notebooks/

# - Run tests
pytest

# - Edit code in src/movr/ (changes are live)
```

---

## What Goes Where

Understanding the project structure:

```
movr-datahub-analytics/
│
├── src/movr/              # THE LIBRARY (will be on PyPI)
│   ├── __init__.py        #   - Public API
│   ├── analytics/         #   - Analysis tools
│   ├── cohorts/           #   - Cohort management
│   ├── data/              #   - Data loading
│   └── utils/             #   - Shared utilities
│
├── notebooks/             # NOT part of PyPI package
│   └── *.ipynb            #   - Import FROM movr
│
├── scripts/               # NOT part of PyPI package
│   └── *.py               #   - Import FROM movr
│
└── tests/                 # NOT part of PyPI package
    └── test_*.py          #   - Test the movr package
```

**Key insight:** Only code in `src/movr/` becomes part of the installable library. Everything else (notebooks, scripts, tests) are *consumers* of that library.

---

## For Contributors: Adding New Code

### If you're building a new utility/feature:

1. Create it in `src/movr/` (e.g., `src/movr/utils/my_helper.py`)
2. Export it in the appropriate `__init__.py`
3. Test it in a notebook or script
4. Write tests in `tests/`

### If you're doing exploratory analysis:

1. Create a notebook in `notebooks/`
2. Import what you need: `from movr import load_data, CohortManager`
3. If you create something reusable, propose moving it to `src/movr/`

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'movr'"

Your environment isn't activated or the package isn't installed:

```bash
source .venv/bin/activate
pip install -e ".[dev,notebooks]"
```

### Changes to src/movr/ aren't reflected

If you installed without `-e`, reinstall properly:

```bash
pip uninstall movr-datahub-analytics
pip install -e ".[dev,notebooks]"
```

### Jupyter can't find movr

Make sure Jupyter is using the right kernel:

```bash
# Install the kernel for your venv
pip install ipykernel
python -m ipykernel install --user --name=movr-dev --display-name="MOVR Dev"

# Then select "MOVR Dev" kernel in Jupyter
```

---

## VS Code vs Browser Jupyter

**Browser Jupyter is faster for notebooks.** Here's why:

| Jupyter Browser | VS Code |
|-----------------|---------|
| Kernel starts once, stays running | Kernel may restart between sessions |
| No code analysis overhead | Pylance analyzes imports |
| Lightweight UI | Extension overhead |

### The "Connecting to kernel" Problem

In VS Code, you'll see this loading bar often:
```
Connecting to kernel: .venv (3.12.3) (Python 3.12.3)
```

This happens because VS Code's Jupyter extension spawns a new kernel process and Pylance analyzes your environment.

### Fixes

**1. Pre-warm the kernel**

Run any cell once when you open VS Code. Subsequent runs will be fast since the kernel stays alive.

**2. Disable unnecessary analysis**

Add to `.vscode/settings.json`:

```json
{
  "python.analysis.indexing": false,
  "python.analysis.autoSearchPaths": false,
  "jupyter.disableJupyterAutoStart": false
}
```

**3. Use Jupyter server directly (fastest)**

Start Jupyter yourself and connect VS Code to it:

```bash
# Terminal 1: Start Jupyter server
source .venv/bin/activate
jupyter notebook --no-browser
```

Then in VS Code:
- `Ctrl+Shift+P` → "Jupyter: Specify Jupyter Server for Connections"
- Paste the `http://localhost:8888/?token=...` URL
- Now VS Code uses the already-running kernel (no startup delay)

**4. Accept that first cell is slow**

If your notebook imports `movr`, that loads pandas, pyarrow, pydantic, etc. The first cell will always take a few seconds - that's unavoidable. But subsequent cells are fast.

### My Preference

- **Exploratory work** → Browser Jupyter (faster, cleaner)
- **Writing library code** → VS Code (better editing, git integration)
- **Debugging** → VS Code (breakpoints, variable inspection)

---

## Future: PyPI Publication

When we publish to PyPI, users will be able to:

```bash
pip install movr-datahub-analytics
```

**Contributors will still use editable mode** for development. The PyPI release is for end-users who just want to use the library without modifying it.

---

## Quick Reference

```bash
# Setup (one time)
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,viz,notebooks]"

# Daily
source .venv/bin/activate
# ... work ...
deactivate  # when done (optional)

# Update after pulling new code
pip install -e ".[dev,viz,notebooks]"  # picks up new dependencies
```

---

*Last Updated: 2025-11-23*
