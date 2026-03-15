#!/usr/bin/env python3
"""
Direct runner for the man_debate crew to bypass shell environment issues.
Run this with: python3 run_crew_direct.py
"""
import sys
import os
import warnings
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set environment variables to avoid shell issues
os.environ.setdefault('SHELL', '/bin/bash')
os.environ.setdefault('PATH', os.environ.get('PATH', ''))

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

from man_debate.crew import ManDebateCrew

def main():
    """Run the crew directly."""
    inputs = {
        'motion': 'Aliens are real',
        'current_year': str(datetime.now().year)
    }

    try:
        print("Creating ManDebateCrew...")
        crew_instance = ManDebateCrew()
        
        print("Getting crew...")
        crew = crew_instance.crew()
        
        print("Starting kickoff...")
        result = crew.kickoff(inputs=inputs)
        
        print("\n" + "="*60)
        print("CREW EXECUTION COMPLETED SUCCESSFULLY")
        print("="*60)
        print(f"\nResult: {result}")
        
    except Exception as e:
        print(f"\n❌ Error occurred while running the crew: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

