# Fix: "crewai not found" Error

## The Problem
The `crewai` command exists in `.venv/bin/crewai`, but your terminal doesn't have the virtual environment activated.

## Solutions

### Solution 1: Activate the Virtual Environment (Recommended)

**In Cursor's terminal:**
```bash
cd /Users/maneeshmukundan/projects/agents/3_crew/myfinances
source .venv/bin/activate
```

You should see `(.venv)` appear in your prompt. Then run:
```bash
crewai run
```

### Solution 2: Use UV Run (Easiest - No Activation Needed)

```bash
cd /Users/maneeshmukundan/projects/agents/3_crew/myfinances
uv run crewai run
```

This automatically uses the correct environment.

### Solution 3: Use Full Path

```bash
cd /Users/maneeshmukundan/projects/agents/3_crew/myfinances
.venv/bin/crewai run
```

### Solution 4: Run Python Module Directly

```bash
cd /Users/maneeshmukundan/projects/agents/3_crew/myfinances
.venv/bin/python -m myfinances.main
```

### Solution 5: Make Cursor Auto-Activate Venv

The `.vscode/settings.json` file should auto-activate the venv. If it's not working:

1. **Reload Cursor**: `Cmd+Shift+P` → `Developer: Reload Window`
2. **Open a new terminal**: The venv should auto-activate (you'll see `(.venv)`)

## Verify Setup

After activation, verify:
```bash
which crewai
# Should output: /Users/maneeshmukundan/projects/agents/3_crew/myfinances/.venv/bin/crewai

crewai --version
# Should show the version
```

## Quick Commands Reference

```bash
# Method 1: Activate then run
source .venv/bin/activate
crewai run

# Method 2: Use UV (no activation needed)
uv run crewai run

# Method 3: Direct path
.venv/bin/crewai run

# Method 4: Python module
.venv/bin/python -m myfinances.main
```


