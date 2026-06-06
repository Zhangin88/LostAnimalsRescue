import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "users.db"


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def connect_db():
    return sqlite3.connect(DB_PATH)


def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'player',
            unlocked_level INTEGER DEFAULT 1,
            total_stars INTEGER DEFAULT 0,
            created_at TEXT
        )
        """
    )

    conn.commit()
    conn.close()


def create_default_admin():
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users (
                username,
                password_hash,
                role,
                unlocked_level,
                total_stars,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "admin",
                hash_password("123"),
                "admin",
                5,
                0,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )

        conn.commit()

    except sqlite3.IntegrityError:
        pass

    finally:
        conn.close()


def register_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users (
                username,
                password_hash,
                role,
                unlocked_level,
                total_stars,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                username,
                hash_password(password),
                "player",
                1,
                0,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )

        conn.commit()
        return True, "Đăng ký thành công!"

    except sqlite3.IntegrityError:
        return False, "Tên đăng nhập đã tồn tại!"

    finally:
        conn.close()


def login_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, username, role, unlocked_level, total_stars
        FROM users
        WHERE username = ? AND password_hash = ?
        """,
        (username, hash_password(password)),
    )

    user = cursor.fetchone()
    conn.close()

    if user:
        return True, {
            "id": user[0],
            "username": user[1],
            "role": user[2],
            "unlocked_level": user[3],
            "total_stars": user[4],
        }

    return False, "Sai tên đăng nhập hoặc mật khẩu!"


def update_progress(user_id, unlocked_level, total_stars):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE users
        SET unlocked_level = ?, total_stars = ?
        WHERE id = ?
        """,
        (unlocked_level, total_stars, user_id),
    )

    conn.commit()
    conn.close()