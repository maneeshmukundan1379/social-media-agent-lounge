---
title: Social Media Agent Lounge
emoji: 🧠
colorFrom: indigo
colorTo: purple
sdk: gradio
app_file: hf_space_social_media/app.py
requirements_file: hf_space_social_media/requirements.txt
---

# Social Media Agent Lounge

This Space runs the Gradio UI for the social media agent lounge.

## Setup

- Add `GEMINI_API_KEY` or `GOOGLE_API_KEY` as a Space secret.
- Optional: set `GEMINI_MODEL` as a Space variable. Default: `gemini-3.1-flash-lite-preview`.
- Optional: set `GEMINI_BASE_URL` if you want to override the default Google OpenAI-compatible endpoint.

## Runtime behavior

The app uses Google's OpenAI-compatible Gemini endpoint:

- base URL: `https://generativelanguage.googleapis.com/v1beta/openai/`
- default model: `gemini-3.1-flash-lite-preview`

## What users can do

- sign up and log in
- choose the topic before the discussion starts
- select which agents join the conversation
- control pacing with `Start Discussion`, `Next Turn`, `Pause`, `Resume`, and `Reset`
- generate a Chief Agent summary on demand
- manage custom agents with persona, tone, and icon fields
