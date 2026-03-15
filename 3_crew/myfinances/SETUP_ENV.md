# Setting Up Virtual Environment for myfinances

## Option 1: Using UV (Recommended - Already Set Up)

Since this project uses `uv` for dependency management, the easiest way is:

### Step 1: Install uv (if not already installed)
```bash
pip install uv
# or
brew install uv  # on macOS
```

### Step 2: Sync dependencies (creates and activates virtual environment)
```bash
cd /Users/maneeshmukundan/projects/agents/3_crew/myfinances
uv sync
```

This command will:
- Create a virtual environment automatically
- Install all dependencies from `pyproject.toml` and `uv.lock`
- Make the environment ready to use

### Step 3: Activate the environment
```bash
# UV automatically manages the environment, but you can activate it manually:
source .venv/bin/activate  # On macOS/Linux
# or on Windows:
.venv\Scripts\activate
```

### Step 4: Run your crew
```bash
crewai run
# or
python -m myfinances.main
```

---

## Option 2: Using Traditional Python venv

If you prefer using the standard Python venv:

### Step 1: Create virtual environment
```bash
cd /Users/maneeshmukundan/projects/agents/3_crew/myfinances
python3 -m venv .venv
```

### Step 2: Activate virtual environment
```bash
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

### Step 3: Install dependencies
```bash
# If using pip:
pip install -e .

# Or install from pyproject.toml:
pip install "crewai[tools]==1.7.2"
```

### Step 4: Run your crew
```bash
crewai run
```

---

## Option 3: Using pip with pyproject.toml

### Step 1: Create virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
```

### Step 2: Install the project
```bash
pip install -e .
```

This will install all dependencies listed in `pyproject.toml`.

---

## Setting Up .env File (for API Keys)

You'll also need to create a `.env` file for your API keys:

```bash
cd /Users/maneeshmukundan/projects/agents/3_crew/myfinances
touch .env
```

Then add your API key:
```env
OPENAI_API_KEY=your_api_key_here
```

---

## Quick Commands Reference

```bash
# Using UV (Recommended)
uv sync                    # Install dependencies
uv run crewai run          # Run without activating
source .venv/bin/activate  # Activate manually (if needed)
crewai run                 # Run the crew

# Using venv
python3 -m venv .venv      # Create venv
source .venv/bin/activate  # Activate
pip install -e .           # Install
crewai run                 # Run
```

---

## Verify Installation

Check that everything is installed correctly:
```bash
python -c "import crewai; print(crewai.__version__)"
```

