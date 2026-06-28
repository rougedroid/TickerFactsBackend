import sqlite3
from config import DB_PATH


class Database:
    def __init__(self):
        self.conn = None

    def connect(self):
        if self.conn is None:
            self.conn = sqlite3.connect(DB_PATH)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def initialize(self):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processed_filings (
                accession_number TEXT PRIMARY KEY,
                form_type TEXT NOT NULL,

                status TEXT NOT NULL,

                retry_count INTEGER NOT NULL DEFAULT 0,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_attempt TIMESTAMP
            )
        """)

        conn.commit()

    def close(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None