"""
Gradio UI and event handlers.
"""

import html

import gradio as gr

from social_agents import AGENTS, generate_topic, start_discussion, step_discussion, summarize_discussion
from social_tools import (
    DEFAULT_AGENT_ICON,
    DEFAULT_AGENT_PERSONA,
    DEFAULT_AGENT_TONE,
    authenticate_user,
    create_agent,
    create_user,
    delete_agent,
    get_user_agents,
    get_user_id,
    update_agent,
)

INTRO_MD = """
# Social Media Agent Lounge

Design a cast of agents, pick the topic, and decide whether the conversation should run automatically or one turn at a time.
"""
TOPIC_PLACEHOLDER = "## Topic setup\nChoose your agents, enter a topic, or click **Generate Topic**."
SUMMARY_PLACEHOLDER = (
    "### Chief Agent\n"
    "No summary yet. Start a discussion and click **Summarize Now** whenever you want a recap."
)

CUSTOM_CSS = """
.app-shell {max-width: 1240px; margin: 0 auto;}
.hero-card, .panel-card {
  border: 1px solid var(--block-border-color);
  border-radius: 16px;
  padding: 18px;
  background: var(--block-background-fill);
}
.discussion-feed {
  border: 1px solid var(--block-border-color);
  border-radius: 16px;
  padding: 16px;
  min-height: 440px;
  background: var(--block-background-fill);
  overflow-y: auto;
}
.message-card {
  border: 1px solid var(--block-border-color);
  border-radius: 14px;
  padding: 12px 14px;
  margin-bottom: 12px;
}
.message-header {
  font-weight: 600;
  margin-bottom: 6px;
}
.empty-state {
  color: var(--body-text-color-subdued);
  padding: 32px 8px;
}
"""


def signup_action(
    name: str, username: str, email: str, password: str, agent_name: str
) -> tuple[str, str, str, str, str, str]:
    ok, msg, user_id = create_user(name, username, email, password)
    if ok:
        clean_agent_name = (agent_name or "").strip()
        if clean_agent_name:
            agent_ok, agent_msg = create_agent(user_id, clean_agent_name)
            if not agent_ok:
                return agent_msg, name, username, email, "", agent_name
        return (
            "Signup successful. Log in to customize your agent lounge.",
            "",
            "",
            "",
            "",
            "",
        )
    return msg, name, username, email, "", agent_name


def _status_message(text: str, success: bool = True) -> str:
    prefix = "Ready" if success else "Needs attention"
    return f"**{prefix}:** {text}"


def _empty_discussion_state(
    available_agents: list[dict] | None = None, selected_names: list[str] | None = None
) -> dict:
    return {
        "core": {},
        "available_agents": available_agents or list(AGENTS),
        "selected_names": selected_names or [agent["name"] for agent in AGENTS],
        "summary_text": SUMMARY_PLACEHOLDER,
        "max_rounds": 12,
        "running": False,
        "turn_interval": 4,
        "discussion_agents": [],
    }


def _normalize_selected_names(
    available_agents: list[dict], selected_names: list[str] | None
) -> list[str]:
    valid_names = [agent["name"] for agent in available_agents]
    selected = [name for name in (selected_names or []) if name in valid_names]
    return selected or valid_names


def _custom_agent_to_discussion_agent(agent: dict) -> dict:
    persona = " ".join(
        [
            f"You are {agent['name']}.",
            agent.get("persona", DEFAULT_AGENT_PERSONA).strip(),
            f"Your tone is {agent.get('tone', DEFAULT_AGENT_TONE).strip()}.",
        ]
    ).strip()
    return {
        "name": agent["name"],
        "persona": persona,
        "icon": agent.get("icon") or DEFAULT_AGENT_ICON,
    }


def _build_available_agents(custom_agents: list[dict]) -> list[dict]:
    return list(AGENTS) + [_custom_agent_to_discussion_agent(agent) for agent in custom_agents]


def _agent_selector_choices(available_agents: list[dict]) -> list[str]:
    return [f"{agent['icon']} {agent['name']}" for agent in available_agents]


def _agent_name_lookup(available_agents: list[dict]) -> dict[str, dict]:
    return {agent["name"]: agent for agent in available_agents}


def _agent_selector_labels_to_names(
    choices: list[str], available_agents: list[dict]
) -> list[str]:
    label_to_name = {
        f"{agent['icon']} {agent['name']}": agent["name"] for agent in available_agents
    }
    return [label_to_name.get(choice, choice) for choice in choices]


def _selected_labels(available_agents: list[dict], selected_names: list[str]) -> list[str]:
    lookup = _agent_name_lookup(available_agents)
    return [
        f"{lookup[name]['icon']} {name}"
        for name in selected_names
        if name in lookup
    ]


def _agent_roster_markdown(available_agents: list[dict], selected_names: list[str]) -> str:
    lookup = _agent_name_lookup(available_agents)
    lines = ["### Active roster"]
    for name in selected_names:
        agent = lookup.get(name)
        if not agent:
            continue
        lines.append(
            f"- {agent['icon']} **{agent['name']}**: {agent['persona']}"
        )
    return "\n".join(lines)


def _render_transcript_html(transcript: list[tuple[str, str]], agents: list[dict]) -> str:
    if not transcript:
        return (
            "<div class='discussion-feed'>"
            "<div class='empty-state'>"
            "<h3>No live discussion yet</h3>"
            "<p>Start a discussion to watch your selected agents react to the topic.</p>"
            "</div>"
            "</div>"
        )

    icon_map = {agent["name"]: agent["icon"] for agent in agents}
    cards = []
    for turn_number, (speaker, text) in enumerate(transcript, start=1):
        safe_speaker = html.escape(speaker)
        safe_text = html.escape(text).replace("\n", "<br>")
        safe_icon = html.escape(icon_map.get(speaker, "💬"))
        cards.append(
            "<div class='message-card'>"
            f"<div class='message-header'>{safe_icon} {safe_speaker} · Turn {turn_number}</div>"
            f"<div>{safe_text}</div>"
            "</div>"
        )
    return f"<div class='discussion-feed'>{''.join(cards)}</div>"


def _topic_markdown(topic_text: str | None = None) -> str:
    clean_topic = (topic_text or "").strip()
    if not clean_topic:
        return TOPIC_PLACEHOLDER
    return f"## Topic\n{clean_topic}"


def _summary_from_state(state: dict) -> str:
    return state.get("summary_text") or SUMMARY_PLACEHOLDER


def _selected_agents_from_state(state: dict, selected_names: list[str] | None = None) -> list[dict]:
    available_agents = state.get("available_agents") or list(AGENTS)
    chosen_names = _normalize_selected_names(available_agents, selected_names or state.get("selected_names"))
    lookup = _agent_name_lookup(available_agents)
    return [lookup[name] for name in chosen_names if name in lookup]


def _refresh_agents_state(
    discussion_state: dict,
    custom_agents: list[dict],
    selected_names: list[str] | None = None,
) -> tuple[dict, list[str], list[str], str]:
    available_agents = _build_available_agents(custom_agents)
    normalized_names = _normalize_selected_names(available_agents, selected_names)
    next_state = dict(discussion_state or {})
    next_state["available_agents"] = available_agents
    next_state["selected_names"] = normalized_names
    agent_choices = _agent_selector_choices(available_agents)
    selected_labels = _selected_labels(available_agents, normalized_names)
    roster_md = _agent_roster_markdown(available_agents, normalized_names)
    return next_state, agent_choices, selected_labels, roster_md


def _custom_agent_form_values(agent: dict | None = None) -> tuple[str, str, str, str]:
    if not agent:
        return ("", DEFAULT_AGENT_PERSONA, DEFAULT_AGENT_TONE, DEFAULT_AGENT_ICON)
    return (
        agent["name"],
        agent.get("persona", DEFAULT_AGENT_PERSONA),
        agent.get("tone", DEFAULT_AGENT_TONE),
        agent.get("icon", DEFAULT_AGENT_ICON),
    )


def _custom_agent_choices(custom_agents: list[dict]) -> list[str]:
    return [agent["name"] for agent in custom_agents]


def login_action(identifier: str, password: str, auth_state: dict) -> tuple:
    ok, msg = authenticate_user(identifier, password)
    if not ok:
        return (
            msg,
            auth_state,
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(active=False),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
        )

    user_id = get_user_id(identifier)
    custom_agents = get_user_agents(user_id) if user_id else []
    available_agents = _build_available_agents(custom_agents)
    selected_names = [agent["name"] for agent in available_agents]
    discussion_state = _empty_discussion_state(available_agents, selected_names)
    roster_md = _agent_roster_markdown(available_agents, selected_names)
    auth_state = {
        "authenticated": True,
        "username": identifier.strip().lower(),
        "user_id": user_id,
    }
    return (
        msg,
        auth_state,
        gr.update(visible=False),
        gr.update(visible=True),
        f"## Welcome, {identifier.strip()}\nSet up the next discussion before anything starts.",
        _status_message("Pick a topic and roster, then click Start Discussion."),
        gr.update(choices=_agent_selector_choices(available_agents), value=_selected_labels(available_agents, selected_names)),
        roster_md,
        "",
        _topic_markdown(),
        _render_transcript_html([], []),
        SUMMARY_PLACEHOLDER,
        discussion_state,
        gr.update(active=False),
        gr.update(choices=_custom_agent_choices(custom_agents), value=None),
        "",
        DEFAULT_AGENT_PERSONA,
        DEFAULT_AGENT_TONE,
        DEFAULT_AGENT_ICON,
    )


def generate_topic_action(
    selected_labels: list[str],
    discussion_state: dict,
    topic_input: str,
) -> tuple[str, str]:
    selected_agents = _selected_agents_from_state(
        discussion_state,
        _agent_selector_labels_to_names(
            selected_labels or [], discussion_state.get("available_agents") or list(AGENTS)
        ),
    )
    if not selected_agents:
        return topic_input, _status_message("Choose at least one agent before generating a topic.", success=False)

    try:
        topic = generate_topic(selected_agents)
    except Exception as exc:  # pragma: no cover - external API surface
        return topic_input, _status_message(f"Could not generate a topic: {exc}", success=False)
    return topic, _status_message("Generated a fresh topic suggestion.")


def start_discussion_action(
    topic_input: str,
    selected_labels: list[str],
    auto_run: bool,
    auto_summary: bool,
    turn_interval: int,
    max_rounds: int,
    discussion_state: dict,
) -> tuple[str, str, str, str, dict, str, gr.update]:
    available_agents = discussion_state.get("available_agents") or list(AGENTS)
    selected_names = _agent_selector_labels_to_names(selected_labels or [], available_agents)
    selected_agents = _selected_agents_from_state(discussion_state, selected_names)
    if not selected_agents:
        return (
            _topic_markdown(),
            _render_transcript_html([], []),
            SUMMARY_PLACEHOLDER,
            _status_message("Choose at least one agent before starting.", success=False),
            discussion_state,
            topic_input,
            gr.update(active=False),
        )

    try:
        topic_md, core_state, _ = start_discussion(selected_agents, topic_input or None)
    except Exception as exc:  # pragma: no cover - external API surface
        return (
            _topic_markdown(),
            _render_transcript_html([], []),
            SUMMARY_PLACEHOLDER,
            _status_message(f"Could not start discussion: {exc}", success=False),
            discussion_state,
            topic_input,
            gr.update(active=False),
        )

    new_state = dict(discussion_state or {})
    new_state.update(
        {
            "core": core_state,
            "discussion_agents": selected_agents,
            "selected_names": selected_names,
            "max_rounds": int(max_rounds),
            "running": bool(auto_run),
            "turn_interval": int(turn_interval),
            "auto_summary": bool(auto_summary),
            "summary_text": SUMMARY_PLACEHOLDER,
        }
    )
    transcript_html = _render_transcript_html(core_state.get("transcript") or [], selected_agents)
    status = _status_message(
        "Discussion started. Use Next Turn for manual pacing or let auto-run continue."
    )
    return (
        topic_md,
        transcript_html,
        SUMMARY_PLACEHOLDER,
        status,
        new_state,
        core_state.get("topic", topic_input or ""),
        gr.update(value=int(turn_interval), active=bool(auto_run)),
    )


def _run_discussion_step(state: dict, auto_summary: bool) -> tuple[str, str, str, str, dict, gr.update]:
    core_state = state.get("core") or {}
    agents = state.get("discussion_agents") or []
    if not core_state or not agents:
        return (
            _topic_markdown(),
            _render_transcript_html([], []),
            _summary_from_state(state),
            _status_message("Start a discussion before stepping through turns.", success=False),
            state,
            gr.update(active=False),
        )

    transcript = core_state.get("transcript") or []
    max_rounds = int(state.get("max_rounds") or 12)
    if len(transcript) >= max_rounds:
        state["running"] = False
        return (
            _topic_markdown(core_state.get("topic", "")),
            _render_transcript_html(transcript, agents),
            _summary_from_state(state),
            _status_message("Reached the max number of turns for this discussion."),
            state,
            gr.update(active=False),
        )

    try:
        topic_md, next_core_state, _ = step_discussion(core_state, agents)
    except Exception as exc:  # pragma: no cover - external API surface
        state["running"] = False
        return (
            _topic_markdown(core_state.get("topic", "")),
            _render_transcript_html(transcript, agents),
            _summary_from_state(state),
            _status_message(f"Could not generate the next turn: {exc}", success=False),
            state,
            gr.update(active=False),
        )

    new_state = dict(state)
    new_state["core"] = next_core_state
    new_transcript = next_core_state.get("transcript") or []
    summary_text = _summary_from_state(new_state)
    if auto_summary and len(new_transcript) % 3 == 0:
        try:
            summary_text = summarize_discussion(next_core_state)
            new_state["summary_text"] = summary_text
        except Exception as exc:  # pragma: no cover - external API surface
            summary_text = _summary_from_state(new_state)
            new_state["summary_text"] = summary_text
            new_state["running"] = False
            return (
                topic_md,
                _render_transcript_html(new_transcript, agents),
                summary_text,
                _status_message(f"Turn added, but summary failed: {exc}", success=False),
                new_state,
                gr.update(active=False),
            )

    keep_running = bool(new_state.get("running"))
    if len(new_transcript) >= max_rounds:
        keep_running = False
        new_state["running"] = False
        status = _status_message("Reached the max turn limit. Pause, summarize, or reset for a new topic.")
    else:
        status = _status_message(f"Turn {len(new_transcript)} added to the discussion.")
    return (
        topic_md,
        _render_transcript_html(new_transcript, agents),
        summary_text,
        status,
        new_state,
        gr.update(value=int(new_state.get("turn_interval") or 4), active=keep_running),
    )


def next_turn_action(state: dict, auto_summary: bool) -> tuple[str, str, str, str, dict, gr.update]:
    next_state = dict(state or {})
    next_state["running"] = False
    return _run_discussion_step(next_state, auto_summary)


def timer_step_action(state: dict, auto_summary: bool) -> tuple[str, str, str, str, dict, gr.update]:
    if not state.get("running"):
        return (
            _topic_markdown((state.get("core") or {}).get("topic", "")),
            _render_transcript_html(
                (state.get("core") or {}).get("transcript") or [],
                state.get("discussion_agents") or [],
            ),
            _summary_from_state(state),
            _status_message("Auto-run is paused."),
            state,
            gr.update(active=False),
        )
    return _run_discussion_step(state, auto_summary)


def pause_action(state: dict) -> tuple[str, dict, gr.update]:
    next_state = dict(state or {})
    next_state["running"] = False
    return (
        _status_message("Auto-run paused. Use Next Turn or Resume when you're ready."),
        next_state,
        gr.update(active=False),
    )


def resume_action(state: dict, turn_interval: int) -> tuple[str, dict, gr.update]:
    core_state = state.get("core") or {}
    transcript = core_state.get("transcript") or []
    if not core_state:
        return (
            _status_message("Start a discussion before resuming.", success=False),
            state,
            gr.update(active=False),
        )
    if len(transcript) >= int(state.get("max_rounds") or 12):
        return (
            _status_message("This discussion already hit its max turn count. Reset to start again.", success=False),
            state,
            gr.update(active=False),
        )
    next_state = dict(state or {})
    next_state["running"] = True
    next_state["turn_interval"] = int(turn_interval)
    return (
        _status_message("Auto-run resumed."),
        next_state,
        gr.update(value=int(turn_interval), active=True),
    )


def summarize_action(state: dict) -> tuple[str, dict]:
    core_state = state.get("core") or {}
    transcript = core_state.get("transcript") or []
    if not transcript:
        return _status_message("Add a few turns before requesting a summary.", success=False), state
    try:
        summary_text = summarize_discussion(core_state)
    except Exception as exc:  # pragma: no cover - external API surface
        return _status_message(f"Could not summarize discussion: {exc}", success=False), state
    next_state = dict(state or {})
    next_state["summary_text"] = summary_text
    return summary_text, next_state


def reset_discussion_action(discussion_state: dict) -> tuple[str, str, str, dict, gr.update, str]:
    available_agents = discussion_state.get("available_agents") or list(AGENTS)
    selected_names = discussion_state.get("selected_names") or [agent["name"] for agent in available_agents]
    next_state = _empty_discussion_state(available_agents, selected_names)
    return (
        _topic_markdown(),
        _render_transcript_html([], []),
        SUMMARY_PLACEHOLDER,
        next_state,
        gr.update(active=False),
        _status_message("Discussion reset. Adjust the topic or roster and start again."),
    )


def load_custom_agent_action(selected_agent_name: str, auth_state: dict) -> tuple[str, str, str, str, str]:
    user_id = auth_state.get("user_id")
    if not user_id or not selected_agent_name:
        name, persona, tone, icon = _custom_agent_form_values()
        return name, persona, tone, icon, _status_message("Creating a new custom agent.")

    custom_agents = get_user_agents(user_id)
    agent = next((item for item in custom_agents if item["name"] == selected_agent_name), None)
    name, persona, tone, icon = _custom_agent_form_values(agent)
    return name, persona, tone, icon, _status_message("Loaded custom agent details.")


def save_custom_agent_action(
    selected_agent_name: str,
    name: str,
    persona: str,
    tone: str,
    icon: str,
    auth_state: dict,
    discussion_state: dict,
    selected_labels: list[str],
) -> tuple:
    user_id = auth_state.get("user_id")
    if not user_id:
        return (
            _status_message("Log in before saving custom agents.", success=False),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            discussion_state,
        )

    selected_names = _agent_selector_labels_to_names(
        selected_labels or [], discussion_state.get("available_agents") or list(AGENTS)
    )
    if selected_agent_name:
        ok, msg = update_agent(user_id, selected_agent_name, name, persona, tone, icon)
    else:
        ok, msg = create_agent(user_id, name, persona, tone, icon)
        if ok:
            selected_names = selected_names + [name]
    if not ok:
        return (
            _status_message(msg, success=False),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            discussion_state,
        )

    custom_agents = get_user_agents(user_id)
    discussion_state, agent_choices, selected_values, roster_md = _refresh_agents_state(
        discussion_state,
        custom_agents,
        selected_names,
    )
    saved_agent = next((agent for agent in custom_agents if agent["name"] == name), None)
    form_name, form_persona, form_tone, form_icon = _custom_agent_form_values(saved_agent)
    return (
        _status_message(f"{msg} Changes apply to the next discussion you start."),
        gr.update(choices=_custom_agent_choices(custom_agents), value=form_name),
        form_name,
        form_persona,
        form_tone,
        form_icon,
        gr.update(choices=agent_choices, value=selected_values),
        roster_md,
        discussion_state,
    )


def delete_custom_agent_action(
    selected_agent_name: str,
    auth_state: dict,
    discussion_state: dict,
    selected_labels: list[str],
) -> tuple:
    user_id = auth_state.get("user_id")
    if not user_id:
        return (
            _status_message("Log in before deleting custom agents.", success=False),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            discussion_state,
        )

    ok, msg = delete_agent(user_id, selected_agent_name)
    if not ok:
        return (
            _status_message(msg, success=False),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            discussion_state,
        )

    custom_agents = get_user_agents(user_id)
    current_selected_names = [
        name
        for name in _agent_selector_labels_to_names(
            selected_labels or [], discussion_state.get("available_agents") or list(AGENTS)
        )
        if name != selected_agent_name
    ]
    discussion_state, agent_choices, selected_values, roster_md = _refresh_agents_state(
        discussion_state,
        custom_agents,
        current_selected_names,
    )
    form_name, form_persona, form_tone, form_icon = _custom_agent_form_values()
    return (
        _status_message("Custom agent deleted. Built-in agents are unchanged."),
        gr.update(choices=_custom_agent_choices(custom_agents), value=None),
        form_name,
        form_persona,
        form_tone,
        form_icon,
        gr.update(choices=agent_choices, value=selected_values),
        roster_md,
        discussion_state,
    )


def clear_custom_agent_form_action() -> tuple[str, str, str, str, str]:
    name, persona, tone, icon = _custom_agent_form_values()
    return (
        name,
        persona,
        tone,
        icon,
        _status_message("Custom agent form cleared. Enter details to create a new profile."),
    )


def sync_selected_agents_action(
    selected_labels: list[str], discussion_state: dict
) -> tuple[dict, str]:
    available_agents = discussion_state.get("available_agents") or list(AGENTS)
    selected_names = _agent_selector_labels_to_names(selected_labels or [], available_agents)
    discussion_state["selected_names"] = _normalize_selected_names(available_agents, selected_names)
    return discussion_state, _agent_roster_markdown(
        available_agents,
        discussion_state["selected_names"],
    )


def logout_action(auth_state: dict) -> tuple:
    _ = auth_state
    return (
        "Logged out.",
        {"authenticated": False, "username": "", "user_id": None},
        gr.update(visible=True),
        gr.update(visible=False),
        "",
        "",
        gr.update(choices=[], value=[]),
        "",
        "",
        _topic_markdown(),
        _render_transcript_html([], []),
        SUMMARY_PLACEHOLDER,
        _empty_discussion_state(),
        gr.update(active=False),
        gr.update(choices=[], value=None),
        "",
        DEFAULT_AGENT_PERSONA,
        DEFAULT_AGENT_TONE,
        DEFAULT_AGENT_ICON,
    )


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="Social Media Agents", css=CUSTOM_CSS) as demo:
        gr.Markdown(INTRO_MD)

        auth_state = gr.State({"authenticated": False, "username": "", "user_id": None})
        discussion_state = gr.State(_empty_discussion_state())

        with gr.Column(visible=True, elem_classes=["app-shell"]) as auth_panel:
            gr.Markdown(
                "### What this app does\n"
                "- create a lounge of AI voices\n"
                "- choose who joins the discussion\n"
                "- control pacing with manual or auto-run turns"
            )
            with gr.Tabs():
                with gr.Tab("Log In"):
                    with gr.Column(elem_classes=["panel-card"]):
                        login_identifier = gr.Textbox(label="Username or Email")
                        login_password = gr.Textbox(label="Password", type="password")
                        login_btn = gr.Button("Log In", variant="primary")
                        login_status = gr.Markdown("")

                with gr.Tab("Sign Up"):
                    with gr.Column(elem_classes=["panel-card"]):
                        signup_name = gr.Textbox(label="Name")
                        signup_username = gr.Textbox(label="Username")
                        signup_email = gr.Textbox(label="Email")
                        signup_password = gr.Textbox(label="Password", type="password")
                        signup_agent_name = gr.Textbox(label="Starter Agent Name (optional)")
                        signup_btn = gr.Button("Create Account", variant="primary")
                        signup_status = gr.Markdown("")

        with gr.Column(visible=False, elem_classes=["app-shell"]) as app_panel:
            welcome_md = gr.Markdown("")
            app_status = gr.Markdown(_status_message("Pick a topic and a roster to begin."))

            with gr.Row():
                with gr.Column(scale=2, elem_classes=["hero-card"]):
                    topic_input = gr.Textbox(
                        label="Discussion topic",
                        placeholder="Should AI agents represent users in public online debates?",
                    )
                    with gr.Row():
                        generate_topic_btn = gr.Button("Generate Topic")
                        start_btn = gr.Button("Start Discussion", variant="primary")
                        reset_btn = gr.Button("Reset")
                    agent_selector = gr.CheckboxGroup(label="Agents in this discussion", choices=[])
                    roster_md = gr.Markdown("")
                    with gr.Row():
                        auto_run = gr.Checkbox(label="Auto-run turns", value=True)
                        auto_summary = gr.Checkbox(label="Auto-summary every 3 turns", value=True)
                    with gr.Row():
                        turn_interval = gr.Slider(
                            minimum=2,
                            maximum=10,
                            value=4,
                            step=1,
                            label="Turn cadence (seconds)",
                        )
                        max_rounds = gr.Slider(
                            minimum=4,
                            maximum=24,
                            value=12,
                            step=1,
                            label="Maximum turns",
                        )

                with gr.Column(scale=1, elem_classes=["panel-card"]):
                    topic_md = gr.Markdown(_topic_markdown())
                    with gr.Row():
                        next_turn_btn = gr.Button("Next Turn")
                        summarize_btn = gr.Button("Summarize Now")
                    with gr.Row():
                        pause_btn = gr.Button("Pause")
                        resume_btn = gr.Button("Resume")
                    logout_btn = gr.Button("Log Out", variant="stop")

            with gr.Row():
                transcript_html = gr.HTML(_render_transcript_html([], []), label="Discussion")
                summary_box = gr.Markdown(SUMMARY_PLACEHOLDER)

            with gr.Accordion("Manage Custom Agents", open=False):
                gr.Markdown(
                    "Create, update, and delete your own agent profiles. Changes apply to the next discussion you start."
                )
                custom_agent_selector = gr.Dropdown(
                    label="Existing custom agents",
                    choices=[],
                    value=None,
                )
                with gr.Row():
                    custom_agent_name = gr.Textbox(label="Agent Name")
                    custom_agent_icon = gr.Textbox(
                        label="Icon",
                        value=DEFAULT_AGENT_ICON,
                        placeholder="Use a short emoji or initials",
                    )
                custom_agent_persona = gr.Textbox(
                    label="Persona",
                    lines=3,
                    value=DEFAULT_AGENT_PERSONA,
                )
                custom_agent_tone = gr.Textbox(
                    label="Tone",
                    value=DEFAULT_AGENT_TONE,
                    placeholder="warm, skeptical, punchy, optimistic...",
                )
                with gr.Row():
                    save_custom_agent_btn = gr.Button("Save Agent", variant="primary")
                    delete_custom_agent_btn = gr.Button("Delete Agent")
                    clear_custom_agent_btn = gr.Button("New Agent Form")
                custom_agent_status = gr.Markdown("")

            timer = gr.Timer(4, active=False)

            generate_topic_btn.click(
                generate_topic_action,
                inputs=[agent_selector, discussion_state, topic_input],
                outputs=[topic_input, app_status],
            )

            start_btn.click(
                start_discussion_action,
                inputs=[
                    topic_input,
                    agent_selector,
                    auto_run,
                    auto_summary,
                    turn_interval,
                    max_rounds,
                    discussion_state,
                ],
                outputs=[
                    topic_md,
                    transcript_html,
                    summary_box,
                    app_status,
                    discussion_state,
                    topic_input,
                    timer,
                ],
            )

            next_turn_btn.click(
                next_turn_action,
                inputs=[discussion_state, auto_summary],
                outputs=[
                    topic_md,
                    transcript_html,
                    summary_box,
                    app_status,
                    discussion_state,
                    timer,
                ],
            )

            timer.tick(
                timer_step_action,
                inputs=[discussion_state, auto_summary],
                outputs=[
                    topic_md,
                    transcript_html,
                    summary_box,
                    app_status,
                    discussion_state,
                    timer,
                ],
            )

            pause_btn.click(
                pause_action,
                inputs=[discussion_state],
                outputs=[app_status, discussion_state, timer],
            )

            resume_btn.click(
                resume_action,
                inputs=[discussion_state, turn_interval],
                outputs=[app_status, discussion_state, timer],
            )

            summarize_btn.click(
                summarize_action,
                inputs=[discussion_state],
                outputs=[summary_box, discussion_state],
            )

            reset_btn.click(
                reset_discussion_action,
                inputs=[discussion_state],
                outputs=[topic_md, transcript_html, summary_box, discussion_state, timer, app_status],
            )

            agent_selector.change(
                sync_selected_agents_action,
                inputs=[agent_selector, discussion_state],
                outputs=[discussion_state, roster_md],
            )

            custom_agent_selector.change(
                load_custom_agent_action,
                inputs=[custom_agent_selector, auth_state],
                outputs=[
                    custom_agent_name,
                    custom_agent_persona,
                    custom_agent_tone,
                    custom_agent_icon,
                    custom_agent_status,
                ],
            )

            save_custom_agent_btn.click(
                save_custom_agent_action,
                inputs=[
                    custom_agent_selector,
                    custom_agent_name,
                    custom_agent_persona,
                    custom_agent_tone,
                    custom_agent_icon,
                    auth_state,
                    discussion_state,
                    agent_selector,
                ],
                outputs=[
                    custom_agent_status,
                    custom_agent_selector,
                    custom_agent_name,
                    custom_agent_persona,
                    custom_agent_tone,
                    custom_agent_icon,
                    agent_selector,
                    roster_md,
                    discussion_state,
                ],
            )

            delete_custom_agent_btn.click(
                delete_custom_agent_action,
                inputs=[custom_agent_selector, auth_state, discussion_state, agent_selector],
                outputs=[
                    custom_agent_status,
                    custom_agent_selector,
                    custom_agent_name,
                    custom_agent_persona,
                    custom_agent_tone,
                    custom_agent_icon,
                    agent_selector,
                    roster_md,
                    discussion_state,
                ],
            )

            clear_custom_agent_btn.click(
                clear_custom_agent_form_action,
                outputs=[
                    custom_agent_name,
                    custom_agent_persona,
                    custom_agent_tone,
                    custom_agent_icon,
                    custom_agent_status,
                ],
            )

        signup_btn.click(
            signup_action,
            inputs=[
                signup_name,
                signup_username,
                signup_email,
                signup_password,
                signup_agent_name,
            ],
            outputs=[
                signup_status,
                signup_name,
                signup_username,
                signup_email,
                signup_password,
                signup_agent_name,
            ],
        )

        login_btn.click(
            login_action,
            inputs=[login_identifier, login_password, auth_state],
            outputs=[
                login_status,
                auth_state,
                auth_panel,
                app_panel,
                welcome_md,
                app_status,
                agent_selector,
                roster_md,
                topic_input,
                topic_md,
                transcript_html,
                summary_box,
                discussion_state,
                timer,
                custom_agent_selector,
                custom_agent_name,
                custom_agent_persona,
                custom_agent_tone,
                custom_agent_icon,
            ],
        )

        logout_btn.click(
            logout_action,
            inputs=[auth_state],
            outputs=[
                login_status,
                auth_state,
                auth_panel,
                app_panel,
                welcome_md,
                app_status,
                agent_selector,
                roster_md,
                topic_input,
                topic_md,
                transcript_html,
                summary_box,
                discussion_state,
                timer,
                custom_agent_selector,
                custom_agent_name,
                custom_agent_persona,
                custom_agent_tone,
                custom_agent_icon,
            ],
        )
    return demo
