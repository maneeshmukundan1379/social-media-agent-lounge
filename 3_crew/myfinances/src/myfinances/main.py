#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from myfinances.crew import Myfinances

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")



def run():
    """
    Run the myfinances crew.
    """
    inputs = {
        'company': 'Molson Coors Brewing Company',
    }

    result = Myfinances().crew().kickoff(inputs=inputs)
    print(result.raw)
    print("\n\nReport has been saved to output/report.md")

    if __name__ == "__main__":
        run()
        