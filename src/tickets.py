import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
from .config import DB_PATH

def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                type TEXT,
                uploaded_at TEXT,
                status TEXT
            );

            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT,
                question TEXT,
                category TEXT,
                priority TEXT,
                status TEXT,
                ai_analysis TEXT,
                suggested_response TEXT,
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER,
                role TEXT,
                content TEXT,
                created_at TEXT,
                FOREIGN KEY (ticket_id) REFERENCES tickets(id)
            );

            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT,
                answer TEXT,
                rating TEXT,
                created_at TEXT
            );
        """)

# Document DB operations
def record_document(name: str, doc_type: str, status: str = "Ready"):
    init_db()
    with get_db() as conn:
        conn.execute("""
            INSERT INTO documents (name, type, uploaded_at, status)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET status=excluded.status, uploaded_at=excluded.uploaded_at
        """, (name, doc_type, datetime.now().isoformat(), status))

def list_documents() -> List[Dict[str, Any]]:
    init_db()
    with get_db() as conn:
        cursor = conn.execute("SELECT * FROM documents ORDER BY uploaded_at DESC")
        return [dict(row) for row in cursor.fetchall()]

def delete_document_record(name: str):
    init_db()
    with get_db() as conn:
        conn.execute("DELETE FROM documents WHERE name = ?", (name,))

# Ticket operations
def create_ticket(
    question: str, 
    customer_name: str = "Customer", 
    category: str = "General", 
    priority: str = "Normal",
    ai_analysis: str = "",
    suggested_response: str = ""
) -> int:
    init_db()
    with get_db() as conn:
        cursor = conn.execute("""
            INSERT INTO tickets (customer_name, question, category, priority, status, ai_analysis, suggested_response, created_at)
            VALUES (?, ?, ?, ?, 'OPEN', ?, ?, ?)
        """, (customer_name, question, category, priority, ai_analysis, suggested_response, datetime.now().isoformat()))
        ticket_id = cursor.lastrowid
        conn.execute("""
            INSERT INTO messages (ticket_id, role, content, created_at)
            VALUES (?, 'customer', ?, ?)
        """, (ticket_id, question, datetime.now().isoformat()))
        return ticket_id

def list_tickets(status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    init_db()
    with get_db() as conn:
        if status_filter and status_filter != "All":
            cursor = conn.execute("SELECT * FROM tickets WHERE status = ? ORDER BY id DESC", (status_filter,))
        else:
            cursor = conn.execute("SELECT * FROM tickets ORDER BY id DESC")
        return [dict(row) for row in cursor.fetchall()]

def get_ticket(ticket_id: int) -> Optional[Dict[str, Any]]:
    init_db()
    with get_db() as conn:
        cursor = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
        row = cursor.fetchone()
        if not row:
            return None
        ticket = dict(row)
        msg_cursor = conn.execute("SELECT * FROM messages WHERE ticket_id = ? ORDER BY id ASC", (ticket_id,))
        ticket["messages"] = [dict(m) for m in msg_cursor.fetchall()]
        return ticket

def update_ticket_status(ticket_id: int, status: str, agent_response: Optional[str] = None):
    init_db()
    with get_db() as conn:
        conn.execute("UPDATE tickets SET status = ? WHERE id = ?", (status, ticket_id))
        if agent_response:
            conn.execute("""
                INSERT INTO messages (ticket_id, role, content, created_at)
                VALUES (?, 'agent', ?, ?)
            """, (ticket_id, agent_response, datetime.now().isoformat()))

# Feedback operations
def save_feedback(question: str, answer: str, rating: str):
    init_db()
    with get_db() as conn:
        conn.execute("""
            INSERT INTO feedback (question, answer, rating, created_at)
            VALUES (?, ?, ?, ?)
        """, (question, answer, rating, datetime.now().isoformat()))
