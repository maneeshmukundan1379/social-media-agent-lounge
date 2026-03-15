"""
Database and auth utilities.
"""

import hashlib
import os
import sqlite3
from typing import Any, Tuple

DB_FILE = os.path.join(os.path.dirname(__file__), "social_media_users.db")
DEFAULT_AGENT_PERSONA = (
    "You are thoughtful, conversational, and add a fresh perspective to social debates."
)
DEFAULT_AGENT_TONE = "balanced and engaging"
DEFAULT_AGENT_ICON = "✨"


def _connect_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def _table_columns(conn: sqlite3.Connection, table_name: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return {str(row["name"]) for row in rows}


def _ensure_agent_columns(conn: sqlite3.Connection) -> None:
    columns = _table_columns(conn, "agents")
    migrations = {
        "persona": (
            "ALTER TABLE agents ADD COLUMN persona TEXT "
            f"NOT NULL DEFAULT '{DEFAULT_AGENT_PERSONA}'"
        ),
        "tone": (
            "ALTER TABLE agents ADD COLUMN tone TEXT "
            f"NOT NULL DEFAULT '{DEFAULT_AGENT_TONE}'"
        ),
        "icon": (
            "ALTER TABLE agents ADD COLUMN icon TEXT "
            f"NOT NULL DEFAULT '{DEFAULT_AGENT_ICON}'"
        ),
    }
    for column_name, sql in migrations.items():
        if column_name not in columns:
            conn.execute(sql)


def init_db() -> None:
    with _connect_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS agents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL UNIQUE,
                persona TEXT NOT NULL DEFAULT 'You are thoughtful, conversational, and add a fresh perspective to social debates.',
                tone TEXT NOT NULL DEFAULT 'balanced and engaging',
                icon TEXT NOT NULL DEFAULT '✨',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
        )
        _ensure_agent_columns(conn)


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _normalize_agent_fields(
    agent_name: str,
    persona: str = DEFAULT_AGENT_PERSONA,
    tone: str = DEFAULT_AGENT_TONE,
    icon: str = DEFAULT_AGENT_ICON,
) -> tuple[str, str, str, str]:
    clean_name = (agent_name or "").strip()
    clean_persona = (persona or DEFAULT_AGENT_PERSONA).strip()
    clean_tone = (tone or DEFAULT_AGENT_TONE).strip()
    clean_icon = (icon or DEFAULT_AGENT_ICON).strip()
    return clean_name, clean_persona, clean_tone, clean_icon


def _agent_row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": int(row["id"]),
        "name": str(row["name"]),
        "persona": str(row["persona"] or DEFAULT_AGENT_PERSONA),
        "tone": str(row["tone"] or DEFAULT_AGENT_TONE),
        "icon": str(row["icon"] or DEFAULT_AGENT_ICON),
        "created_at": str(row["created_at"] or ""),
    }


def create_user(
    name: str, username: str, email: str, password: str
) -> Tuple[bool, str, int | None]:
    name = (name or "").strip()
    username = (username or "").strip().lower()
    email = (email or "").strip().lower()
    password = password or ""

    if not all([name, username, email, password]):
        return False, "Please fill in all signup fields.", None

    password_hash = _hash_password(password)
    try:
        with _connect_db() as conn:
            cursor = conn.execute(
                "INSERT INTO users (name, username, email, password_hash) VALUES (?, ?, ?, ?)",
                (name, username, email, password_hash),
            )
            user_id = cursor.lastrowid
        return True, "Signup successful. Please log in.", user_id
    except sqlite3.IntegrityError:
        return False, "Username or email already exists.", None


def create_agent(
    user_id: int,
    agent_name: str,
    persona: str = DEFAULT_AGENT_PERSONA,
    tone: str = DEFAULT_AGENT_TONE,
    icon: str = DEFAULT_AGENT_ICON,
) -> Tuple[bool, str]:
    clean_name, clean_persona, clean_tone, clean_icon = _normalize_agent_fields(
        agent_name, persona, tone, icon
    )
    if not clean_name:
        return False, "Please provide an agent name."

    try:
        with _connect_db() as conn:
            conn.execute(
                """
                INSERT INTO agents (user_id, name, persona, tone, icon)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, clean_name, clean_persona, clean_tone, clean_icon),
            )
        return True, "Agent created."
    except sqlite3.IntegrityError:
        return False, "Agent name already exists."


def update_agent(
    user_id: int,
    current_name: str,
    new_name: str,
    persona: str,
    tone: str,
    icon: str,
) -> Tuple[bool, str]:
    clean_current = (current_name or "").strip()
    clean_name, clean_persona, clean_tone, clean_icon = _normalize_agent_fields(
        new_name, persona, tone, icon
    )
    if not clean_current:
        return False, "Choose an existing custom agent to update."
    if not clean_name:
        return False, "Please provide an agent name."

    try:
        with _connect_db() as conn:
            cursor = conn.execute(
                """
                UPDATE agents
                SET name = ?, persona = ?, tone = ?, icon = ?
                WHERE user_id = ? AND name = ?
                """,
                (clean_name, clean_persona, clean_tone, clean_icon, user_id, clean_current),
            )
        if cursor.rowcount == 0:
            return False, "Custom agent not found."
        return True, "Agent updated."
    except sqlite3.IntegrityError:
        return False, "Agent name already exists."


def delete_agent(user_id: int, agent_name: str) -> Tuple[bool, str]:
    clean_name = (agent_name or "").strip()
    if not clean_name:
        return False, "Choose an agent to delete."

    with _connect_db() as conn:
        cursor = conn.execute(
            "DELETE FROM agents WHERE user_id = ? AND name = ?",
            (user_id, clean_name),
        )
    if cursor.rowcount == 0:
        return False, "Custom agent not found."
    return True, "Agent deleted."


def get_user_agents(user_id: int) -> list[dict[str, Any]]:
    with _connect_db() as conn:
        rows = conn.execute(
            """
            SELECT id, name, persona, tone, icon, created_at
            FROM agents
            WHERE user_id = ?
            ORDER BY created_at ASC, id ASC
            """,
            (user_id,),
        ).fetchall()
    return [_agent_row_to_dict(row) for row in rows]


def authenticate_user(identifier: str, password: str) -> Tuple[bool, str]:
    identifier = (identifier or "").strip().lower()
    if identifier.startswith("@"):
        identifier = identifier[1:]
    password = password or ""

    if not identifier or not password:
        return False, "Please enter username/email and password."

    password_hash = _hash_password(password)
    with _connect_db() as conn:
        user_row = conn.execute(
            "SELECT password_hash FROM users WHERE username = ?",
            (identifier,),
        ).fetchone()
        if user_row:
            if user_row["password_hash"] == password_hash:
                return True, "Login successful."
            return False, "Invalid password."

        email_row = conn.execute(
            "SELECT password_hash FROM users WHERE email = ?",
            (identifier,),
        ).fetchone()
        if email_row:
            if email_row["password_hash"] == password_hash:
                return True, "Login successful."
            return False, "Invalid password."

    return False, "User not found."


def get_user_id(identifier: str) -> int | None:
    identifier = (identifier or "").strip().lower()
    if identifier.startswith("@"):
        identifier = identifier[1:]

    with _connect_db() as conn:
        row = conn.execute(
            "SELECT id FROM users WHERE username = ? OR email = ?",
            (identifier, identifier),
        ).fetchone()

    if row:
        return int(row["id"])
    return None
