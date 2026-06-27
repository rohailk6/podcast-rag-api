import asyncpg
import secrets
from app.config import DATABASE_URL

# The connection pool — a set of reusable database connections.
# Think of it like a pool of taxi cabs sitting ready.
# Instead of calling a new cab every time (slow), you grab one
# that's already waiting (fast), use it, then return it to the pool.
pool = None

async def init_db():
    """
    Called once on startup. Creates the connection pool and
    creates all tables if they don't exist yet.
    """
    global pool

    pool = await asyncpg.create_pool(DATABASE_URL, min_size=2 , max_size= 10)

    async with pool.acquire() as conn:
        # Create users table
        # SERIAL = auto-incrementing integer (1, 2, 3...)
        # PRIMARY KEY = unique identifier for each row
        # UNIQUE = no two rows can have the same value in this column
        # NOT NULL = this field is required, can't be empty
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id        SERIAL PRIMARY KEY,
                name      TEXT NOT NULL,
                email     TEXT UNIQUE NOT NULL,
                api_key   TEXT UNIQUE NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        # Create sessions table
        # REFERENCES users(id) = foreign key — links each session to a user
        # ON DELETE CASCADE = if the user is deleted, their sessions are too
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id         SERIAL PRIMARY KEY,
            user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            created_at TIMESTAMPTZ DEFAULT NOW())
        """)

        # Create messages table
        # role is either 'user' or 'assistant'
        # CHECK constraint enforces only those two values are allowed
        await conn.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id         SERIAL PRIMARY KEY,
        session_id INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
        role       TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
        content    TEXT NOT NULL,
        created_at TIMESTAMPTZ DEFAULT NOW()
    )
    """)


    print("Database tables ready.")

async def close_db():
    """Called on shutdown — closes all connections in the pool cleanly."""
    global pool
    if pool:
        await pool.close()


# ─── User operations ──────────────────────────────────────────────────────────

async def create_user(name: str, email: str) -> dict:
    """
    Creates a new user and generates a secure random API key for them.
    Returns the user record including the raw API key (shown once only).
    
    secrets.token_hex(32) generates a 64-character random hex string.
    This is cryptographically secure — practically impossible to guess.
    """
    api_key = secrets.token_hex(32)

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO users (name, email, api_key)
            VALUES ($1, $2, $3)
            RETURNING id, name, email, created_at
            """,
            name, email, api_key
        )

    return {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "api_key": api_key,   # shown once — user must save this
        "created_at": row["created_at"]
    }

async def get_user_by_api_key(api_key: str):
    """
    Looks up a user by their API key.
    Returns the user row if found, None if not.
    Used by security.py to validate incoming requests.
    """
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, name, email FROM users WHERE api_key = $1",
            api_key
        )
    return row

# ─── Session operations ───────────────────────────────────────────────────────

async def create_session(user_id: int) -> int:
    """
    Creates a new conversation session for a user.
    Returns the new session's ID.
    """
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO sessions (user_id)
            VALUES ($1)
            RETURNING id
            """,
            user_id
        )
    return row["id"]

async def get_session(session_id: int, user_id: int):
    """
    Fetches a session — but only if it belongs to the requesting user.
    This prevents User A from reading User B's sessions.
    """
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, user_id, created_at FROM sessions WHERE id = $1 AND user_id = $2",
            session_id, user_id
        )
    return row


# ─── Message operations ───────────────────────────────────────────────────────

async def save_message(session_id: int, role: str, content: str):
    """
    Saves a single message to a session.
    Called twice per query — once for the user question, once for the answer.
    """
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO messages (session_id, role, content)
            VALUES ($1, $2, $3)
            """,
            session_id, role, content
        )


async def get_session_messages(session_id: int) -> list:
    """
    Returns all messages in a session, oldest first.
    Used to load conversation history before generating an answer.
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT role, content, created_at
            FROM messages
            WHERE session_id = $1
            ORDER BY created_at ASC
            """,
            session_id
        )
    return [dict(row) for row in rows]