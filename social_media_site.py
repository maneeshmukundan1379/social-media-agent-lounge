"""
Social Media Site with 5 agents (Gradio).
"""

from dotenv import load_dotenv

from social_tools import init_db
from social_ui import build_ui

load_dotenv(override=True)


if __name__ == "__main__":
    init_db()
    ui = build_ui()
    ui.queue().launch()
