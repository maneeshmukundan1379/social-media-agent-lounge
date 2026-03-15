# Fix: OpenTelemetry Import Error When Creating Crew Project

## Error
```
ImportError: cannot import name '_OTEL_PYTHON_EXPORTER_OTLP_HTTP_CREDENTIAL_PROVIDER'
```

## Cause
This error occurs due to version incompatibility between OpenTelemetry packages, specifically between:
- `opentelemetry-sdk`
- `opentelemetry-exporter-otlp-proto-http`

The private attribute `_OTEL_PYTHON_EXPORTER_OTLP_HTTP_CREDENTIAL_PROVIDER` was added/removed in different versions, causing import failures.

## Solutions

### Solution 1: Update crewai (Recommended)

If you're using an older version of crewai, update to the latest version which has compatible dependencies:

```bash
pip install --upgrade crewai[tools]
# or with uv
uv pip install --upgrade "crewai[tools]"
```

### Solution 2: Fix in pyproject.toml

Add explicit version constraints for OpenTelemetry packages in your `pyproject.toml`:

```toml
[project]
dependencies = [
    "crewai[tools]==1.4.1",
    "opentelemetry-api>=1.38.0,<2.0.0",
    "opentelemetry-sdk>=1.38.0,<2.0.0",
    "opentelemetry-exporter-otlp-proto-http>=1.38.0,<2.0.0",
    "opentelemetry-exporter-otlp-proto-common>=1.38.0,<2.0.0",
]
```

Then reinstall:
```bash
uv sync
# or
pip install -e .
```

### Solution 3: Clean Install

If the error persists, try a clean reinstall:

```bash
# Remove existing installation
pip uninstall opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp-proto-http -y

# Reinstall with compatible versions
pip install "opentelemetry-api>=1.38.0,<2.0.0"
pip install "opentelemetry-sdk>=1.38.0,<2.0.0"
pip install "opentelemetry-exporter-otlp-proto-http>=1.38.0,<2.0.0"

# Then reinstall crewai
pip install "crewai[tools]>=1.4.1"
```

### Solution 4: Use Virtual Environment

Create a fresh virtual environment and install:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install crewai
pip install crewai[tools]
```

### Solution 5: If Using UV

If using `uv` for dependency management:

```bash
# Sync dependencies (this should resolve versions correctly)
uv sync

# Or force reinstall
uv pip install --force-reinstall "crewai[tools]>=1.4.1"
```

## Verification

After applying the fix, verify the installation:

```python
# Test import
python3 -c "from opentelemetry.exporter.otlp.proto.http import OTLPExporter; print('OpenTelemetry import successful')"
```

Or test crewai:

```bash
crewai --version
```

## Additional Notes

- This issue is more common when upgrading from older crewai versions
- The error typically occurs during project creation (`crewai create`) or initialization
- Make sure all OpenTelemetry packages are at the same major version for compatibility
- Version 1.38.0+ of OpenTelemetry packages have been tested to work well together

