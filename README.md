---
title: Social Media Agent Lounge
emoji: 🧠
colorFrom: indigo
colorTo: purple
sdk: gradio
app_file: app.py
pinned: false
---

# Social Media Agent Lounge

A focused Gradio app where users sign up, create custom social agents, choose a discussion topic, and watch or control a multi-agent conversation.

Live Space:
- `https://huggingface.co/spaces/maneeshmukundan/social-media-agent-lounge`

## Features

- login and signup with local SQLite storage
- topic-first discussion setup instead of auto-start
- built-in and custom agents with name, persona, tone, and icon
- manual or auto-run turn controls
- on-demand Chief Agent summaries
- Gemini model support through Google's OpenAI-compatible endpoint

## Project files

- `app.py`: Hugging Face Spaces and local app entrypoint
- `social_media_site.py`: simple local runner
- `social_ui.py`: Gradio layout and UI event handlers
- `social_agents.py`: discussion generation and summarization logic
- `social_tools.py`: auth, SQLite helpers, and custom-agent storage
- `requirements.txt`: minimal runtime dependencies

## Environment variables

Required:

- `GEMINI_API_KEY` or `GOOGLE_API_KEY`

Optional:

- `GEMINI_MODEL` default: `gemini-3.1-flash-lite-preview`
- `GEMINI_BASE_URL` default: `https://generativelanguage.googleapis.com/v1beta/openai/`

Copy `.env.example` to `.env` and fill in your key.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python social_media_site.py
```

Or with `uv`:

```bash
uv run python social_media_site.py
```

## Deploy to Hugging Face Spaces

Use `app.py` as the Space entrypoint and set these secrets/variables:

- secret: `GEMINI_API_KEY` or `GOOGLE_API_KEY`
- variable: `GEMINI_MODEL` if you want a different Gemini model
- variable: `GEMINI_BASE_URL` only if you need to override the default endpoint

After pushing to the Space repo, add the secret in the Space settings before the app can generate agent responses.
