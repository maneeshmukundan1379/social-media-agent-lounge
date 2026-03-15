"""
Agent definitions and discussion logic.
"""

import os
import random
from typing import Dict, List, Tuple

from openai import OpenAI

GEMINI_BASE_URL = os.getenv(
    "GEMINI_BASE_URL",
    "https://generativelanguage.googleapis.com/v1beta/openai/",
)
MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    os.getenv("OPENAI_MODEL", "gemini-3.1-flash-lite-preview"),
)
TOPIC_SEED_PROMPT = (
    "Pick ONE engaging social media discussion topic. "
    "Return only the topic text, no quotes, no markdown."
)
CHIEF_SUMMARY_PROMPT = (
    "You are Chief Agent. Summarize the discussion so far in 3-5 bullet points, "
    "then provide a short conclusion (1-2 sentences) labeled 'Conclusion:'. "
    "Keep it concise and faithful to the discussion."
)


def cre_ai_create_agent(name: str, persona: str, icon: str) -> Dict[str, str]:
    # cre.ai-style agent creation (lightweight wrapper).
    return {"name": name, "persona": persona, "icon": icon}


AGENTS = [
    cre_ai_create_agent(
        "Alpha",
        "You are Alpha: bold, trend-focused, and concise.",
        "🧠",
    ),
    cre_ai_create_agent(
        "Beta",
        "You are Beta: practical, grounded, and example-driven.",
        "🛠️",
    ),
    cre_ai_create_agent(
        "Gamma",
        "You are Gamma: curious, analytical, and asks sharp questions.",
        "🔍",
    ),
    cre_ai_create_agent(
        "Theta",
        "You are Theta: creative, imaginative, and metaphorical.",
        "🎨",
    ),
    cre_ai_create_agent(
        "PI",
        "You are PI: data-minded, skeptical, and evidence-first.",
        "📊",
    ),
]


def _llm_client() -> OpenAI:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "Set GEMINI_API_KEY or GOOGLE_API_KEY to use the social media agents."
        )
    return OpenAI(api_key=api_key, base_url=GEMINI_BASE_URL)


def _chat_completion(system_prompt: str, user_prompt: str) -> str:
    client = _llm_client()
    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=200,
    )
    return resp.choices[0].message.content.strip()


def _normalize_topic_text(topic: str | None) -> str:
    text = (topic or "").strip()
    if text.lower().startswith("## topic:"):
        text = text.split(":", 1)[1].strip()
    return text


def _format_transcript(transcript: List[Tuple[str, str]]) -> str:
    return "\n".join([f"{speaker}: {text}" for speaker, text in transcript[-12:]])


def _format_transcript_full(transcript: List[Tuple[str, str]]) -> str:
    return "\n".join([f"{speaker}: {text}" for speaker, text in transcript])


def _format_transcript_display(
    transcript: List[Tuple[str, str]], agents: List[Dict[str, str]]
) -> str:
    icon_map = {agent["name"]: agent["icon"] for agent in agents}
    lines = [
        f"{icon_map.get(speaker, '')} {speaker}: {text}".strip()
        for speaker, text in transcript
    ]
    return "\n".join(lines)


def _pick_topic(agents: List[Dict[str, str]]) -> Tuple[str, str]:
    if not agents:
        raise ValueError("At least one agent is required.")
    picker = random.choice(agents)
    topic = _chat_completion(picker["persona"], TOPIC_SEED_PROMPT)
    return picker["name"], topic


def generate_topic(agents: List[Dict[str, str]]) -> str:
    _, topic = _pick_topic(agents)
    return topic


def _agent_reply(agent: Dict[str, str], topic: str, transcript: List[Tuple[str, str]]) -> str:
    context = _format_transcript(transcript)
    user_prompt = (
        f"Topic: {topic}\n"
        f"Recent discussion:\n{context}\n\n"
        "Respond as a social media commenter in 1-3 short sentences."
    )
    return _chat_completion(agent["persona"], user_prompt)


def _init_state(agents: List[Dict[str, str]], topic: str | None = None) -> dict:
    if not agents:
        raise ValueError("At least one agent is required.")
    custom_topic = _normalize_topic_text(topic)
    if custom_topic:
        picker_name = ""
        topic_text = custom_topic
    else:
        picker_name, topic_text = _pick_topic(agents)
    transcript: List[Tuple[str, str]] = []
    histories = {agent["name"]: [] for agent in agents}
    state = {
        "topic": topic_text,
        "picker": picker_name,
        "turn_idx": 0,
        "transcript": transcript,
        "histories": histories,
    }
    return state


def _next_agent_sequence(
    picker_name: str, agents: List[Dict[str, str]]
) -> List[Dict[str, str]]:
    if not picker_name:
        return list(agents)
    return [agent for agent in agents if agent["name"] != picker_name]


def start_discussion(
    agents: List[Dict[str, str]], topic: str | None = None
) -> Tuple[str, dict, str]:
    state = _init_state(agents, topic)
    topic = f"## Topic: {state['topic']}"
    transcript_text = _format_transcript_display(state["transcript"], agents)
    return topic, state, transcript_text


def step_discussion(state: dict, agents: List[Dict[str, str]]) -> Tuple[str, dict, str]:
    if not state:
        state = _init_state(agents)

    topic = f"## Topic: {state['topic']}"
    picker = state["picker"]
    transcript = state["transcript"]
    histories = state["histories"]
    turn_idx = state["turn_idx"]

    speakers = _next_agent_sequence(picker, agents)
    if not speakers:
        return topic, state, _format_transcript_display(transcript, agents)

    agent = speakers[turn_idx % len(speakers)]
    reply = _agent_reply(agent, topic, transcript)

    transcript.append((agent["name"], reply))
    histories[agent["name"]] = histories[agent["name"]] + [
        {"role": "assistant", "content": reply}
    ]

    state["turn_idx"] = turn_idx + 1
    return topic, state, _format_transcript_display(transcript, agents)


def summarize_discussion(state: dict) -> str:
    if not state:
        return "👑 Chief Agent: No discussion yet."

    transcript = state.get("transcript") or []
    if not transcript:
        return "👑 Chief Agent: No discussion yet."

    discussion_text = _format_transcript_full(transcript)
    summary = _chat_completion(
        CHIEF_SUMMARY_PROMPT,
        f"Discussion so far:\n{discussion_text}",
    )
    return f"👑 Chief Agent:\n{summary}"
