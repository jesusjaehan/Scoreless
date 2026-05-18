import sqlite3
from datetime import datetime
from pathlib import Path

class DatabaseManager:
    def __init__(self, db_path="C:/Users/jesus/CLIcoding/ScoreLessGUI/scoreless.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        with self.get_connection() as conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS concepts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT,
                domain TEXT,
                created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS competency_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                concept_id INTEGER,
                score REAL DEFAULT 0,
                session_count INTEGER DEFAULT 0,
                next_review_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (concept_id) REFERENCES concepts(id)
            );
            """)

    def get_user_id(self, name):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM users WHERE name=?", (name,))
            row = cur.fetchone()
            if row:
                return row[0]
            cur.execute("INSERT INTO users (name, created_at) VALUES (?,?)",
                        (name, datetime.now().isoformat()))
            return cur.lastrowid

    def get_all_concepts(self, user_id):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT c.id, c.name, c.domain, COALESCE(cs.score, 0), COALESCE(cs.session_count, 0)
                FROM concepts c LEFT JOIN competency_scores cs ON c.id = cs.concept_id
                WHERE c.user_id = ?
            """, (user_id,))
            return cur.fetchall()

    def add_concept(self, user_id, name, domain):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO concepts (user_id, name, domain, created_at) VALUES (?,?,?,?)",
                        (user_id, name, domain, datetime.now().isoformat()))
            return cur.lastrowid

    def upsert_cs(self, user_id, concept_id, score, next_review):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM competency_scores WHERE concept_id=?", (concept_id,))
            if cur.fetchone():
                cur.execute("""
                    UPDATE competency_scores SET score=?, session_count=session_count+1,
                    next_review_at=?, updated_at=? WHERE concept_id=?
                """, (score, next_review, datetime.now().isoformat(), concept_id))
            else:
                cur.execute("""
                    INSERT INTO competency_scores (user_id, concept_id, score, session_count, next_review_at, updated_at)
                    VALUES (?, ?, ?, 1, ?, ?)
                """, (user_id, concept_id, score, next_review, datetime.now().isoformat()))
