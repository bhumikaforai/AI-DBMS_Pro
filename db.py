import os
import pymysql
from pymysql.cursors import DictCursor
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DB = os.getenv("MYSQL_DB", "college_assistant")


MYSQL_USE_SSL = os.getenv("MYSQL_USE_SSL", "auto").strip().lower()


def _get_ssl_config():
    """Determine SSL parameters for cloud databases like TiDB Cloud."""
    if MYSQL_USE_SSL in ("true", "1", "yes", "require"):
        return {"ssl": True}
    if MYSQL_USE_SSL == "auto":
        # Automatically enable SSL for TiDB Cloud or port 4000
        if "tidbcloud.com" in MYSQL_HOST.lower() or MYSQL_PORT == 4000:
            return {"ssl": True}
    return None


def get_server_connection():
    """Connect to MySQL server without specifying a database (for DB creation)."""
    conn_params = {
        "host": MYSQL_HOST,
        "port": MYSQL_PORT,
        "user": MYSQL_USER,
        "password": MYSQL_PASSWORD,
        "charset": "utf8mb4",
        "cursorclass": DictCursor,
        "autocommit": True
    }
    ssl_config = _get_ssl_config()
    if ssl_config:
        conn_params["ssl"] = ssl_config
    return pymysql.connect(**conn_params)


def get_db_connection():
    """Connect to the specific application database."""
    conn_params = {
        "host": MYSQL_HOST,
        "port": MYSQL_PORT,
        "user": MYSQL_USER,
        "password": MYSQL_PASSWORD,
        "database": MYSQL_DB,
        "charset": "utf8mb4",
        "cursorclass": DictCursor,
        "autocommit": True
    }
    ssl_config = _get_ssl_config()
    if ssl_config:
        conn_params["ssl"] = ssl_config
    return pymysql.connect(**conn_params)


def init_db():
    """Create database and tables if they don't already exist."""
    try:
        # 1. Ensure database exists
        server_conn = get_server_connection()
        with server_conn.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DB}` "
                "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
            )
        server_conn.close()

        # 2. Ensure tables exist
        db_conn = get_db_connection()
        with db_conn.cursor() as cursor:
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(80) NOT NULL UNIQUE,
                    email VARCHAR(120) NOT NULL UNIQUE,
                    full_name VARCHAR(120) NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)

            # Chat history table (stores user conversations)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    role VARCHAR(20) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT fk_chat_user FOREIGN KEY (user_id) 
                        REFERENCES users(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
        db_conn.close()
        print(f"[OK] MySQL database '{MYSQL_DB}' and tables verified successfully.")
        return True, "Database initialized successfully"
    except Exception as e:
        error_msg = f"Database initialization failed: {str(e)}"
        print(f"[ERROR] {error_msg}")
        return False, error_msg


def register_user(username, email, full_name, password):
    """
    Register a new user with hashed password.
    Returns (success: bool, message: str, user_id: int or None)
    """
    username = username.strip().lower()
    email = email.strip().lower()
    full_name = full_name.strip()

    if not username or not email or not full_name or not password:
        return False, "All fields are required.", None

    if len(password) < 6:
        return False, "Password must be at least 6 characters long.", None

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Check if username or email already exists
            cursor.execute(
                "SELECT id, username, email FROM users WHERE username = %s OR email = %s",
                (username, email)
            )
            existing = cursor.fetchone()
            if existing:
                if existing["username"] == username:
                    conn.close()
                    return False, "Username is already taken. Please choose another.", None
                if existing["email"] == email:
                    conn.close()
                    return False, "Email is already registered. Please login.", None

            # Hash password and insert
            pwd_hash = generate_password_hash(password)
            cursor.execute(
                """
                INSERT INTO users (username, email, full_name, password_hash)
                VALUES (%s, %s, %s, %s)
                """,
                (username, email, full_name, pwd_hash)
            )
            user_id = cursor.lastrowid
        conn.close()
        return True, "Account created successfully! Please sign in.", user_id

    except Exception as e:
        return False, f"Registration error: {str(e)}", None


def authenticate_user(identifier, password):
    """
    Authenticate user by username or email and password.
    Returns (success: bool, message: str, user_dict: dict or None)
    """
    identifier = identifier.strip().lower()

    if not identifier or not password:
        return False, "Username/Email and Password are required.", None

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, username, email, full_name, password_hash, created_at
                FROM users
                WHERE username = %s OR email = %s
                """,
                (identifier, identifier)
            )
            user = cursor.fetchone()
        conn.close()

        if not user:
            return False, "No account found with this username or email.", None

        if not check_password_hash(user["password_hash"], password):
            return False, "Incorrect password. Please try again.", None

        # Return user without password_hash
        user_info = {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "created_at": user["created_at"]
        }
        return True, "Login successful!", user_info

    except Exception as e:
        return False, f"Authentication error: {str(e)}", None


def get_user_by_id(user_id):
    """Fetch user profile by user_id."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, username, email, full_name, created_at FROM users WHERE id = %s",
                (user_id,)
            )
            user = cursor.fetchone()
        conn.close()
        return user
    except Exception:
        return None


def save_chat_message(user_id, role, content):
    """Save a chat message in chat_history for a given user."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO chat_history (user_id, role, content) VALUES (%s, %s, %s)",
                (user_id, role, content)
            )
        conn.close()
        return True
    except Exception as e:
        print(f"Failed to save message: {e}")
        return False


def get_user_chat_history(user_id, limit=50):
    """Fetch past chat history for user."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT role, content, created_at 
                FROM chat_history 
                WHERE user_id = %s 
                ORDER BY id ASC 
                LIMIT %s
                """,
                (user_id, limit)
            )
            history = cursor.fetchall()
        conn.close()
        return history
    except Exception:
        return []
