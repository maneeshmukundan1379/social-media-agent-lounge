#!/usr/bin/env python3
"""
Quick test script for Stock_assistant_web.py
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Stock_assistant_web import process_question

def test_question(question):
    """Test a question"""
    print(f"\n{'='*60}")
    print(f"Testing Question: {question}")
    print(f"{'='*60}\n")
    
    # Initialize empty history
    history = []
    
    # Process the question
    new_history, _ = process_question(question, history)
    
    # Print the response
    if len(new_history) >= 2:
        user_msg = new_history[-2]
        assistant_msg = new_history[-1]
        
        print(f"User: {user_msg.get('content', '')}")
        print(f"\nAssistant Response:")
        print(f"{'-'*60}")
        print(assistant_msg.get('content', ''))
        print(f"{'-'*60}\n")
    else:
        print("Error: Unexpected response format")
        print(new_history)

if __name__ == "__main__":
    question = "Will tesla stock grow in the next 2 weeks?"
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    
    test_question(question)

