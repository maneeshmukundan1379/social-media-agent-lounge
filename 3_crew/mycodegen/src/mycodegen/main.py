#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from mycodegen.crew import Mycodegen

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

assignment = 'Write a python program to search the web for the various restaurants in and around Mundelein  IL,USA upto 10 miles and sort them by their ratings and return the top 50 restaurants.Use the query "restaurants in Mundelein IL,USA upto 10 miles" and use the SerperDevTool to search the web. Get the Serper API key from the .env file in this project when executing the code.'

def run():
    """
    Run the crew.
    """
    inputs = {
        'assignment': assignment
    }
    
    result = Mycodegen().crew().kickoff(inputs=inputs)
    print(result.raw)