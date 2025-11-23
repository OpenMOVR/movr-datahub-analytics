# Interactive Python (`# %%`) Notes

Personal notes for working with percent-format interactive Python files in VS Code.

---

## Naming Conventions

- Use `_interactive.py` suffix to make intent explicit
- Keep parity with notebooks: `01_getting_started.ipynb` ↔ `01_getting_started_interactive.py`
- Prefix with two-digit index `NN_` for ordering

---

## Jupytext: Keep `.py` and `.ipynb` in Sync

### Why pair them?
- Plain `.py` files are easier to review, version, and diff in git
- Work either as notebook or script, both stay in sync

### Manual Commands

```bash
# Convert notebook → python percent format
jupytext --to py:percent notebooks/NAME.ipynb

# Convert python → notebook
jupytext --to ipynb notebooks/NAME.py

# Sync both directions
jupytext --sync notebooks/NAME.ipynb
```

### Make it Automatic

**VS Code:** Install Jupytext extension, enable save-time pairing.

**Pre-commit hook** (add to `.pre-commit-config.yaml`):
```yaml
- repo: local
  hooks:
    - id: jupytext-sync
      name: Jupytext sync
      entry: jupytext --sync
      language: system
      files: '\.(ipynb|py)$'
      stages: [commit]
```

---

## VS Code Troubleshooting

### The Problem

When clicking "Run Cell" or pressing `Shift+Enter` on a `# %%` cell:
- Shows **"Connecting to kernel: .venv (Python 3.12.3)"** forever
- Spinning indicator never stops
- Cell never executes

### Quick Fixes (Try in Order)

**1. Reload VS Code Window**
```
Ctrl+Shift+P → "Developer: Reload Window"
```

**2. Select the Right Python Interpreter**
```
Ctrl+Shift+P → "Python: Select Interpreter"
→ Choose: .venv/bin/python (the one with 3.12.3)
```

**3. Clear Jupyter Kernel Cache**
```
Ctrl+Shift+P → "Jupyter: Clear Jupyter Kernel Cache"
```
Then reload window again.

**4. Register the Kernel Manually**

```bash
source .venv/bin/activate
python -m ipykernel install --user --name=movr-venv --display-name="MOVR (.venv)"
```

Then in VS Code:
- Reload window
- Run a cell
- Select **"MOVR (.venv)"** when prompted for kernel

**5. Check VS Code Settings**

Make sure `.vscode/settings.json` has:

```json
{
  "python.analysis.indexing": false,
  "python.analysis.autoSearchPaths": false,
  "jupyter.disableJupyterAutoStart": false
}
```

**Important:** `jupyter.disableJupyterAutoStart` must be `false` (not `true`).

### Nuclear Option: Full Reset

If nothing works:

```bash
# Kill any zombie Jupyter processes
pkill -f jupyter

# Remove kernel specs and re-register
jupyter kernelspec list
jupyter kernelspec remove movr-venv  # if exists
rm -rf ~/.local/share/jupyter/runtime/*

# Re-register
source .venv/bin/activate
python -m ipykernel install --user --name=movr-venv --display-name="MOVR (.venv)"
```

Then restart VS Code completely (not just reload).

### Why This Happens

VS Code's Jupyter extension needs to:
1. Find your Python interpreter
2. Start a Jupyter kernel server
3. Connect to it

If any step fails or times out → infinite "Connecting to kernel" spinner.

Common causes:
- Wrong Python interpreter selected
- Stale kernel cache
- `ipykernel` not installed in the venv
- VS Code settings preventing auto-start
- Zombie Jupyter processes blocking ports

---

## Alternative: Just Use Browser Jupyter

If VS Code keeps being annoying:

```bash
source .venv/bin/activate
jupyter notebook notebooks/
```

Browser Jupyter doesn't have these kernel connection issues. It's faster anyway.

---

## Verify Everything is Installed

```bash
source .venv/bin/activate
python -m ipykernel --version    # Should show version
jupyter --version                 # Should show versions
jupyter kernelspec list           # Should show movr-venv
```

---

*Last updated: 2025-11-23*
