
import hashlib
import hmac
import re
import secrets
import sqlite3
from pathlib import Path

# Use the existing project database directory.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
AUTH_DB = PROJECT_ROOT / "database" / "soc.db"

ITERATIONS = 600_000


def get_connection():
    AUTH_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(AUTH_DB, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_auth_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS soc_users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL COLLATE NOCASE UNIQUE,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'SOC Analyst',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)


def validate_username(username):
    username = username.strip()

    if not 4 <= len(username) <= 24:
        return False, "Username must contain 4–24 characters."

    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_.]*", username):
        return False, (
            "Start with a letter. Use only letters, numbers, "
            "underscores, and dots."
        )

    return True, ""


def validate_password(password):
    if len(password) < 8:
        return False, "Use at least 8 characters."

    if not re.search(r"[A-Z]", password):
        return False, "Include at least one uppercase letter (A–Z)."

    if not re.search(r"[a-z]", password):
        return False, "Include at least one lowercase letter (a–z)."

    if not re.search(r"\d", password):
        return False, "Include at least one number (0–9)."

    if not re.search(r"[^A-Za-z0-9]", password):
        return False, "Include at least one special character."

    return True, ""


def hash_password(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        ITERATIONS
    ).hex()


def register_user(username, password):
    initialize_auth_db()

    username = username.strip()

    valid, message = validate_username(username)
    if not valid:
        return False, message

    valid, message = validate_password(password)
    if not valid:
        return False, message

    salt = secrets.token_bytes(16).hex()
    password_hash = hash_password(password, salt)

    try:
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO soc_users
                    (username, password_hash, salt, role)
                VALUES (?, ?, ?, ?)
                """,
                (username, password_hash, salt, "SOC Analyst")
            )

        return True, "Account created successfully. You can now sign in."

    except sqlite3.IntegrityError:
        return False, "That username already exists. Choose another."


def authenticate_user(username, password):
    initialize_auth_db()

    with get_connection() as conn:
        user = conn.execute(
            """
            SELECT user_id, username, password_hash, salt, role
            FROM soc_users
            WHERE username = ?
            """,
            (username.strip(),)
        ).fetchone()

    if user is None:
        return None

    candidate_hash = hash_password(password, user["salt"])

    if not hmac.compare_digest(
        candidate_hash, user["password_hash"]
    ):
        return None

    return {
        "user_id": user["user_id"],
        "username": user["username"],
        "role": user["role"]
    }
