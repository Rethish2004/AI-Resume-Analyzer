import sqlite3
import json

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


DATABASE_NAME = "resume_analysis.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    connection = sqlite3.connect(
        DATABASE_NAME
    )

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# CREATE TABLES
# ============================================================

def create_table():

    connection = get_connection()

    cursor = connection.cursor()

    # --------------------------------------------------------
    # USERS TABLE
    # --------------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT NOT NULL UNIQUE,

            password_hash TEXT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
        """
    )

    # --------------------------------------------------------
    # ANALYSIS TABLE
    # --------------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS analyses (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER,

            resume_name TEXT,

            resume_score REAL,

            similarity_score REAL,

            skill_match REAL,

            matched_skills TEXT,

            missing_skills TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id)
                REFERENCES users(id)

        )
        """
    )

    # --------------------------------------------------------
    # MIGRATION FOR OLD DATABASE
    # --------------------------------------------------------
    # If your old analyses table already exists without
    # user_id, add the new column.

    cursor.execute(
        "PRAGMA table_info(analyses)"
    )

    columns = [
        row["name"]
        for row in cursor.fetchall()
    ]

    if "user_id" not in columns:

        cursor.execute(
            """
            ALTER TABLE analyses
            ADD COLUMN user_id INTEGER
            """
        )

    connection.commit()

    connection.close()


# ============================================================
# CREATE USER
# ============================================================

def create_user(
    name,
    email,
    password
):

    connection = get_connection()

    cursor = connection.cursor()

    normalized_email = email.strip().lower()

    password_hash = generate_password_hash(
        password
    )

    try:

        cursor.execute(
            """
            INSERT INTO users
            (
                name,
                email,
                password_hash
            )
            VALUES (?, ?, ?)
            """,
            (
                name.strip(),
                normalized_email,
                password_hash
            )
        )

        user_id = cursor.lastrowid

        connection.commit()

        return user_id

    except sqlite3.IntegrityError:

        return None

    finally:

        connection.close()


# ============================================================
# FIND USER BY EMAIL
# ============================================================

def get_user_by_email(email):

    connection = get_connection()

    cursor = connection.cursor()

    normalized_email = email.strip().lower()

    cursor.execute(
        """
        SELECT
            id,
            name,
            email,
            password_hash,
            created_at
        FROM users
        WHERE email = ?
        """,
        (
            normalized_email,
        )
    )

    user = cursor.fetchone()

    connection.close()

    if user:
        return dict(user)

    return None


# ============================================================
# VERIFY PASSWORD
# ============================================================

def verify_user_password(
    stored_password_hash,
    password
):

    return check_password_hash(
        stored_password_hash,
        password
    )


# ============================================================
# GET USER BY ID
# ============================================================

def get_user_by_id(user_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            name,
            email,
            created_at
        FROM users
        WHERE id = ?
        """,
        (
            user_id,
        )
    )

    user = cursor.fetchone()

    connection.close()

    if user:
        return dict(user)

    return None


# ============================================================
# SAVE ANALYSIS
# ============================================================

def save_analysis(
    resume_name,
    resume_score,
    similarity_score,
    skill_match,
    matched_skills,
    missing_skills,
    user_id=None
):

    connection = get_connection()

    cursor = connection.cursor()

    matched_skills_json = json.dumps(
        matched_skills or []
    )

    missing_skills_json = json.dumps(
        missing_skills or []
    )

    cursor.execute(
        """
        INSERT INTO analyses
        (
            user_id,
            resume_name,
            resume_score,
            similarity_score,
            skill_match,
            matched_skills,
            missing_skills
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            resume_name,
            resume_score,
            similarity_score,
            skill_match,
            matched_skills_json,
            missing_skills_json
        )
    )

    analysis_id = cursor.lastrowid

    connection.commit()

    connection.close()

    return analysis_id


# ============================================================
# GET ANALYSIS HISTORY
# ============================================================

def get_analysis_history(
    user_id=None
):

    connection = get_connection()

    cursor = connection.cursor()

    if user_id is not None:

        cursor.execute(
            """
            SELECT
                id,
                user_id,
                resume_name,
                resume_score,
                similarity_score,
                skill_match,
                matched_skills,
                missing_skills,
                created_at
            FROM analyses
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (
                user_id,
            )
        )

    else:

        cursor.execute(
            """
            SELECT
                id,
                user_id,
                resume_name,
                resume_score,
                similarity_score,
                skill_match,
                matched_skills,
                missing_skills,
                created_at
            FROM analyses
            ORDER BY id DESC
            """
        )

    rows = cursor.fetchall()

    connection.close()

    history = []

    for row in rows:

        item = dict(row)

        try:

            item["matched_skills"] = json.loads(
                item["matched_skills"] or "[]"
            )

        except Exception:

            item["matched_skills"] = []


        try:

            item["missing_skills"] = json.loads(
                item["missing_skills"] or "[]"
            )

        except Exception:

            item["missing_skills"] = []


        history.append(item)

    return history