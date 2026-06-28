from storage.database import Database


class FilingRepository:
    def __init__(self, database: Database):
        self.db = database

    def filing_exists(self, accession_number: str) -> bool:
        conn = self.db.connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT 1
            FROM processed_filings
            WHERE accession_number = ?
            """,
            (accession_number,)
        )

        return cursor.fetchone() is not None

    def insert_new_filing(
        self,
        accession_number: str,
        form_type: str,
        status: str = "NEW"
    ):
        conn = self.db.connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO processed_filings
            (
                accession_number,
                form_type,
                status
            )
            VALUES (?, ?, ?)
            """,
            (
                accession_number,
                form_type,
                status
            )
        )

        conn.commit()

    def update_status(
        self,
        accession_number: str,
        status: str
    ):
        conn = self.db.connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE processed_filings
            SET
                status = ?,
                updated_at = CURRENT_TIMESTAMP,
                last_attempt = CURRENT_TIMESTAMP
            WHERE accession_number = ?
            """,
            (
                status,
                accession_number
            )
        )

        conn.commit()

    def increment_retry(self, accession_number: str):
        conn = self.db.connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE processed_filings
            SET
                retry_count = retry_count + 1,
                updated_at = CURRENT_TIMESTAMP,
                last_attempt = CURRENT_TIMESTAMP
            WHERE accession_number = ?
            """,
            (accession_number,)
        )

        conn.commit()

    def get_waiting_llm(self):
        conn = self.db.connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM processed_filings
            WHERE status = 'WAITING_FOR_LLM'
            ORDER BY created_at ASC
            """
        )

        return cursor.fetchall()

    def get_failed(self):
        conn = self.db.connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM processed_filings
            WHERE status = 'FAILED'
            ORDER BY retry_count ASC
            """
        )

        return cursor.fetchall()