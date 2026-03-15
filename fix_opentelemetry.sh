#!/bin/bash
# Quick fix script for OpenTelemetry import error when creating crew projects

set -e

echo "🔧 Fixing OpenTelemetry Import Error..."

# Check if uv is available
if command -v uv &> /dev/null; then
    echo "✅ Using uv for dependency management"
    
    # Update crewai
    echo "📦 Updating crewai..."
    uv pip install --upgrade "crewai[tools]>=1.4.1"
    
    # Ensure compatible OpenTelemetry versions
    echo "📦 Ensuring compatible OpenTelemetry versions..."
    uv pip install --upgrade \
        "opentelemetry-api>=1.38.0,<2.0.0" \
        "opentelemetry-sdk>=1.38.0,<2.0.0" \
        "opentelemetry-exporter-otlp-proto-http>=1.38.0,<2.0.0" \
        "opentelemetry-exporter-otlp-proto-common>=1.38.0,<2.0.0"
        
elif command -v pip3 &> /dev/null || command -v pip &> /dev/null; then
    PIP_CMD="pip3"
    if command -v pip &> /dev/null; then
        PIP_CMD="pip"
    fi
    
    echo "✅ Using $PIP_CMD for dependency management"
    
    # Update crewai
    echo "📦 Updating crewai..."
    $PIP_CMD install --upgrade "crewai[tools]>=1.4.1"
    
    # Ensure compatible OpenTelemetry versions
    echo "📦 Ensuring compatible OpenTelemetry versions..."
    $PIP_CMD install --upgrade \
        "opentelemetry-api>=1.38.0,<2.0.0" \
        "opentelemetry-sdk>=1.38.0,<2.0.0" \
        "opentelemetry-exporter-otlp-proto-http>=1.38.0,<2.0.0" \
        "opentelemetry-exporter-otlp-proto-common>=1.38.0,<2.0.0"
else
    echo "❌ Error: Neither uv nor pip found. Please install one of them."
    exit 1
fi

echo ""
echo "✅ Fix applied! Try creating your crew project again:"
echo "   crewai create"
echo ""
echo "If you're in an existing project, you can also run:"
echo "   uv sync"
echo "   # or"
echo "   pip install -e ."

