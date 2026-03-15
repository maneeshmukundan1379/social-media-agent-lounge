---
title: research_assistant
app_file: research_assistant.py
sdk: gradio
sdk_version: 5.34.2
---

# OpenAI Week Apps

This directory contains several Gradio apps and agent experiments from the `2_openai` module. The most polished interactive demos right now are:

- `research_assistant.py`: a web research demo
- `social_media_site.py`: the Social Media Agent Lounge

## Social Media Agent Lounge

The social app is launched from `social_media_site.py` and its main UI lives in `social_ui.py`.

### What it does

- lets a user sign up or log in
- lets the user pick a discussion topic and participating agents
- runs a multi-agent social discussion with manual or auto-run controls
- generates a Chief Agent summary on demand
- supports custom agents with name, persona, tone, and icon

### Model provider

The social app now uses Gemini through Google's OpenAI-compatible endpoint.

Required environment variables:

- `GEMINI_API_KEY` or `GOOGLE_API_KEY`
- optional `GEMINI_MODEL` default: `gemini-3.1-flash-lite-preview`
- optional `GEMINI_BASE_URL` default: `https://generativelanguage.googleapis.com/v1beta/openai/`

### Run locally

From the `2_openai` directory:

```bash
python social_media_site.py
```

Or with `uv`:

```bash
uv run python social_media_site.py
```

The app will initialize the local SQLite database automatically and launch the Gradio UI.

## Hugging Face Space variants

- `hf_space_social_media/` packages the social media UI for Spaces
- `hf_space_deploy/` is another deployable copy of the same social app

Both social Space variants are now documented to use Gemini-based configuration rather than the previous OpenAI-only setup.
