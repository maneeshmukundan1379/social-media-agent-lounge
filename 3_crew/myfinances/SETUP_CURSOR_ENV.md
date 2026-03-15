# Setting Up .venv in Cursor IDE

## Quick Setup

I've created a `.vscode/settings.json` file that configures Cursor to use your `.venv` automatically.

## Methods to Set Python Interpreter in Cursor

### Method 1: Using Command Palette (Recommended)

1. **Open Command Palette**: 
   - Press `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Windows/Linux)

2. **Select Python Interpreter**:
   - Type: `Python: Select Interpreter`
   - Select it from the dropdown

3. **Choose the .venv interpreter**:
   - Look for: `./.venv/bin/python` or `.venv/bin/python3.12`
   - It should show Python 3.12.11

### Method 2: Using Status Bar

1. Look at the bottom-right of Cursor window
2. Click on the Python version displayed (e.g., "Python 3.9.6")
3. Select `.venv/bin/python` from the list

### Method 3: Automatic (Using settings.json)

The `.vscode/settings.json` file I created will automatically use `.venv/bin/python` for this workspace.

**To verify it's working:**
- Check the bottom-right corner of Cursor - it should show Python 3.12.11
- Open a terminal in Cursor (`Ctrl+` ` or View → Terminal)
- The terminal should automatically activate the .venv (you'll see `(.venv)` in the prompt)

### Method 4: Manual Terminal Activation

If automatic activation doesn't work, manually activate in the terminal:

```bash
cd /Users/maneeshmukundan/projects/agents/3_crew/myfinances
source .venv/bin/activate
```

You should see `(.venv)` appear in your terminal prompt.

## Verify Setup

Run this in Cursor's integrated terminal to verify:

```bash
which python
# Should output: /Users/maneeshmukundan/projects/agents/3_crew/myfinances/.venv/bin/python

python --version
# Should output: Python 3.12.11

python -c "import sys; print(sys.executable)"
# Should show the .venv path
```

## Troubleshooting

### If Python interpreter doesn't show up:

1. **Reload Cursor window**:
   - `Cmd+Shift+P` → `Developer: Reload Window`

2. **Check .venv exists**:
   ```bash
   ls -la .venv/bin/python*
   ```

3. **Recreate .venv if needed**:
   ```bash
   uv sync
   ```

4. **Manual selection**:
   - `Cmd+Shift+P` → `Python: Select Interpreter`
   - Click "Enter interpreter path..."
   - Enter: `${workspaceFolder}/.venv/bin/python`

### Settings File Location

The settings file is at:
```
.vscode/settings.json
```

You can also create/update it manually with:
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
    "python.terminal.activateEnvironment": true
}
```

## Using UV Run (Alternative)

If you prefer using `uv` directly without activating venv:

```bash
uv run crewai run
uv run python -m myfinances.main
```

This will automatically use the correct environment.


